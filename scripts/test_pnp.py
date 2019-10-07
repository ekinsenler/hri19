import os
import sys
from functools import partial
from action_names import *
import time
from naoqi import ALProxy

cmdsever_ip = os.getenv('PEPPER_IP')
cmdserver_port = 9559

pdir = os.getenv('PNP_HOME')
sys.path.insert(0, pdir + '/PNPnaoqi/py')

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *

pdir = os.getenv('MODIM_HOME')
sys.path.append(pdir + '/src/GUI')

from ws_client import *
import ws_client

try:
    faceProxy = ALProxy("ALFaceDetection", cmdsever_ip, cmdserver_port)
except Exception, e:
    print "Error when creating face detection proxy:"
    print str(e)
    exit(1)

period = 500
faceProxy.subscribe("Test_Face", period, 0.0)
memValue = "FaceDetected"

try:
    memoryProxy = ALProxy("ALMemory", cmdsever_ip, cmdserver_port)
except Exception, e:
    print "Error when creating memory proxy:"
    print str(e)
    exit(1)


def checkConditions(p):

    val = memoryProxy.getData(memValue, 0)
    if(val and isinstance(val, list) and len(val) == 2):
        p.set_condition('FaceDetected', True)
        print "FaceDetected"


def show_number(number=1):
    im.display.loadUrl('slide.html')

    im.executeModality('TEXT_title', str(number))
    im.executeModality('TEXT_default', str(number))


def welcome():
    im.display.loadUrl('welcome.html')


def ask():
    pass



# Start action server
if __name__ == "__main__":

    p = PNPCmd()
    mc = ModimWSClient()
    mc.setCmdServerAddr(cmdsever_ip, cmdserver_port)

    p.begin()

    # A simple loop that reads the memValue and checks whether faces are detected.
    
    for i in range(0, 20):
          time.sleep(0.5)
          val = memoryProxy.getData(memValue, 0)
          print ""
          print "\*****"
          print ""

    # Check whether we got a valid output: a list with two fields.
    if(val and isinstance(val, list) and len(val) == 2):
      # We detected faces !
      # For each face, we can read its shape info and ID.
      # First Field = TimeStamp.
      timeStamp = val[0]
      # Second Field = array of face_Info's.
      faceInfoArray = val[1]

      try:
      # Browse the faceInfoArray to get info on each detected face.
        for faceInfo in faceInfoArray:
            # First Field = Shape info.
            faceShapeInfo = faceInfo[0]
            # Second Field = Extra info (empty for now).
            faceExtraInfo = faceInfo[1]
            print "  alpha %.3f - beta %.3f" % (faceShapeInfo[1], faceShapeInfo[2])
            print "  width %.3f - height %.3f" % (faceShapeInfo[3], faceShapeInfo[4])
      except Exception, e:
        print "faces detected, but it seems getData is invalid. ALValue ="
        print val
        print "Error msg %s" % (str(e))
    else:
      print "Error with getData. ALValue = %s" % (str(val))
      # Unsubscribe the module.

    faceProxy.unsubscribe("Test_Face")
    print "Test terminated successfully."
    # for i in range(2):
    #    mc.run_interaction(show_number)
    #    p.exec_action(SAY_ACTION, str(i + 1))
    #    p.exec_action(WAIT_ACTION, 1)

    # sequence
    # p.exec_action('say', 'hello')     # blocking
    # p.exec_action('say', 'Good_morning')     # blocking
    # p.exec_action('wait', '2')  # blocking

    # # interrupt
    # p.exec_action('wait', '5', interrupt='timeout_2.5', recovery='wait_3;skip_action')  # blocking
    #
    # p.exec_action('wait', '5', interrupt='mycondition', recovery='wait_3;skip_action')  # blocking
    #
    # # concurrency
    # p.start_action('wait', '2') # non-blocking
    # p.start_action('wait', '5') # non-blocking
    #
    status = 'run'
    while status == 'run':
        status = p.action_status('wait')
        print(status)
        time.sleep(0.5)
    p.interrupt_action('wait')

    p.end()
