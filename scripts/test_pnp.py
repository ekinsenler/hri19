import os, sys
from functools import partial
from action_names import *

cmdsever_ip = os.getenv('PEPPER_IP')
cmdserver_port = 9101

pdir = os.getenv('PNP_HOME')
sys.path.insert(0, pdir+'/PNPnaoqi/py')

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *

pdir = os.getenv('MODIM_HOME')
sys.path.append(pdir + '/src/GUI')

from ws_client import *
import ws_client

def checkConditions(p):

    p.set_condition('mycondition', True)


def show_number(number=1):
    im.display.loadUrl('slide.html')

    im.executeModality('TEXT_title',str(number))
    im.executeModality('TEXT_default',str(number))

# Start action server
if __name__ == "__main__":

    p = PNPCmd()
    mc = ModimWSClient()
    mc.setCmdServerAddr(cmdsever_ip, cmdserver_port)

    p.begin()

    # checkConditions(p)

    for i in range(2):
        mc.run_interaction(show_number)
        p.exec_action(SAY_ACTION, str(i + 1))
        p.exec_action(WAIT_ACTION, 1)

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
    # status = 'run'
    # while status == 'run':
    #     status = p.action_status('wait')
    #     print(status)
    #     time.sleep(0.5)
    #
    # p.interrupt_action('wait')

    p.end()
