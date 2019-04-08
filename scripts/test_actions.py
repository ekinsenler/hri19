import os, sys

pdir = os.getenv('PNP_HOME')
sys.path.insert(0, pdir+'/PNPnaoqi/actions/')

import action_base
from action_base import *

pdir = os.getenv('PEPPER_TOOLS_HOME')
sys.path.append(pdir+ '/cmd_server')

import pepper_cmd
from pepper_cmd import *


class SayAction(NAOqiAction_Base):

    def __init__(self, actionName, session, robot):
        NAOqiAction_Base.__init__(self,actionName, session)
        self.robot = robot

    def actionThread_exec (self, params):
        # action init
        # action exec
        print "Action "+self.actionName+" "+params+" exec..."
        self.robot.say(params)
        # action end
        action_termination(self.actionName,params)


class WaitAction(NAOqiAction_Base):

    def actionThread_exec (self, params):
        # action init
        dt = 0.25
        tmax = float(params)
        t = 0
        # action exec
        while (self.do_run and t<tmax):
            print "Action "+self.actionName+" "+params+" exec..."
            time.sleep(dt)
            t += dt

        # action end
        action_termination(self.actionName,params)



def initActions():

    pepper_cmd.begin()

    app = pepper_cmd.robot.app # action_base.initApp()

    SayAction('sayD', app.session, pepper_cmd.robot)
    WaitAction('waitD', app.session)

    return app

# Start action server
if __name__ == "__main__":

    print("Starting action server (CTRL+C to quit)")

    app = initActions()

    app.run()
