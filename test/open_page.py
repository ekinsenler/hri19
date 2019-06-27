import qi
import sys

pip = '10.0.1.200'
pport = '9559'
weburl = "http://10.0.1.202:9580/"

session = qi.Session()
try:
    session.connect("tcp://" + pip + ":" + str(pport))
except RuntimeError:
    print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
           "Please check your script arguments. Run with -h option for help.")
    sys.exit(1)

tablet_service = session.service("ALTabletService")

# Display a local image located in img folder in the root of the web server
# The ip of the robot from the tablet is 198.18.0.1

if weburl.startswith('http'):
    strurl=weburl
else:
    strurl = "http://198.18.0.1/apps/spqrel/%s" %(weburl)
print ("URL: ",strurl)
tablet_service.showWebview(strurl)