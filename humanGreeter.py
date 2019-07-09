"""Example: A Simple class to get & read FaceDetected Events"""

import qi
import time
import sys
import os
import argparse

from naoqi import ALProxy

class HumanGreeter(object):
    """
    A simple class to react to face detection events.
    """

    def __init__(self, app):
        """
        Initialisation of qi framework and event detection.
        """
        super(HumanGreeter, self).__init__()
        self.app = app
        session = app.session
        # Get the service ALMemory.
        self.memory = session.service("ALMemory")
        self.ba_service = session.service("ALBasicAwareness")
        self.ba_service.setEnabled(True)
        self.leds_service = session.service("ALLeds")
        self.leds_service.on('FaceLeds') # reset to white
        # Connect the event callback.
        self.fdsub = self.memory.subscriber("FaceDetected")
        self.ch1 = self.fdsub.signal.connect(self.on_human_tracked)
        self.srsub = self.memory.subscriber("WordRecognized")
        self.ch2 = self.srsub.signal.connect(self.on_word_recognized)
        self.vocabulary = ["yes", "no", "please", "hello", "goodbye", "hi, there", "go to the kitchen"]

        # Get the services ALTextToSpeech and ALFaceDetection.
        self.tts = session.service("ALTextToSpeech")
        self.asr = session.service("ALSpeechRecognition")
        self.asr.setLanguage("English")
        self.asr.pause(True)
        self.asr.setVocabulary(self.vocabulary, False)
        self.asr.pause(False)
        self.asr.subscribe("SpeechRecognition")
        self.face_detection = session.service("ALFaceDetection")
        self.face_detection.subscribe("HumanGreeter")
        self.got_face = False

    def on_word_recognized(self, value):
        if value == "yes":
            print "Yes..."
            self.close()
            self.app.stop()
        elif value == "no":
            print "No..."
            self.tts.say("Okay, see you than.")
            self.got_face = False
            time.sleep(5)
        else:
            print "Value of else: ", value


    def on_human_tracked(self, value):
        """
        Callback for event FaceDetected.
        """
        faceID = -1

        if value == []:  # empty value when the face disappears
            print "Face disappeared"
            self.got_face = False
            # white face leds
            self.leds_service.on('FaceLeds')

        else:
            # green face leds
            self.leds_service.off('LeftFaceLedsRed')
            self.leds_service.off('LeftFaceLedsBlue')
            self.leds_service.off('RightFaceLedsRed')
            self.leds_service.off('RightFaceLedsBlue')

            if not self.got_face:  # only the first time a face appears

                self.got_face = True
                print "I saw a face!"
                #self.tts.say("Hello, you!")
                # First Field = TimeStamp.
                timeStamp = value[0]
                print "TimeStamp is: " + str(timeStamp)

                # Second Field = array of face_Info's.
                faceInfoArray = value[1]
                for j in range( len(faceInfoArray)-1 ):
                    faceInfo = faceInfoArray[j]

                    # First Field = Shape info.
                    faceShapeInfo = faceInfo[0]

                    # Second Field = Extra info (empty for now).
                    faceExtraInfo = faceInfo[1]

                    faceID = faceExtraInfo[0]
    def close(self):
        self.face_detection.unsubscribe("HumanGreeter")
        self.fdsub.signal.disconnect(self.ch1)
        self.ba_service.setEnabled(False)
        self.leds_service.on('FaceLeds') # reset to white
        self.asr.unsubscribe('SpeechRecognition')
        self.srsub.signal.disconnect(self.ch2)

    def run(self):
        """
        Loop on, wait for events until manual interruption.
        """
        print "Starting HumanGreeter"
        try:
            while True:
                #val = self.memory.getData('FaceDetection/FaceDetected')
                #if len(val)>0:
                #    print('Memory value %r' %val)
                if self.got_face:
                    print "Got face!!"
                    self.tts.say("Hello, Do you want to play a game?")
                    #Once you run application, it never stops. There is bug.
                    #self.app.run()
                    self.close()

                time.sleep(1)
        except KeyboardInterrupt:
            print "Interrupted by user, stopping all behaviors"
            self.close()