import time

import qi

PEPPER_IP = '10.0.1.201'
PEPPER_CMD_PORT = '9559'
PC_IP = '10.0.1.208'
HTTP_SERVER_PORT = '9580'

pepper_session = qi.Session()
try:
    pepper_session.connect("tcp://" + PEPPER_IP + ":" + PEPPER_CMD_PORT)
except RuntimeError as e:
    print("Can't connect to Naoqi at ip \"" + PEPPER_IP + "\" on port " + PEPPER_CMD_PORT)
    raise e

tablet_service = pepper_session.service("ALTabletService")
url = "http://" + PC_IP + ":" + HTTP_SERVER_PORT + "/welcome/welcome.html"
#url = "http://198.18.0.1/apps/spqrel/index.html"
#url = "http://10.0.1.1"
print("PEPPER launching URL: ", url)
# Ensure that the tablet wifi is enable
print tablet_service.showWebview(url)