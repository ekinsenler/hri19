from random import randint
import time

# State of looking for a face
STATE_WAITING_USER = "STATE_WAITING_USER"
# State when pepper wait user to say yes for start a game
STATE_WAITING_AGREE_TO_START = "STATE_WAITING_AGREE_TO_START"
# State of playing a game
STATE_WAIT_GAME = "STATE_WAIT_GAME"
# State of playing a game
STATE_PLAYING = "STATE_PLAYING"


class Controller:

    def __init__(self, app, welcome_url, game_url):

        self.welcome_url = welcome_url
        self.game_url = game_url

        self.current_state = None
        self.face_detect_active = False
        self.speech_recogn_active = False

        self.games_won = 0

        self.app = app
        session = app.session
        # Get the service ALMemory.
        self.memory = session.service("ALMemory")
        self.ba_service = session.service("ALBasicAwareness")
        # self.ba_service.setEnabled(True)
        self.leds_service = session.service("ALLeds")
        self.leds_service.on('FaceLeds')  # reset to white
        # Connect the event callback.
        self.fdsub = self.memory.subscriber("FaceDetected")
        self.ch1 = self.fdsub.signal.connect(self.on_human_tracked)
        self.srsub = self.memory.subscriber("WordRecognized")
        self.ch2 = self.srsub.signal.connect(self.on_word_recognized)
        # self.vocabulary = ["yes", "no", "please", "hello", "goodbye", "hi, there", "go to the kitchen"]

        # Get the services ALTextToSpeech and ALFaceDetection.
        self.tts = session.service("ALTextToSpeech")
        self.asr = session.service("ALSpeechRecognition")
        self.asr.setLanguage("English")
        # self.asr.pause(True)
        # self.asr.setVocabulary(self.vocabulary, False)
        # self.asr.pause(False)
        #self.asr.subscribe("SpeechRecognition")
        self.face_detection = session.service("ALFaceDetection")
        self.posture_service = session.service("ALRobotPosture")
        self.motion_service = session.service("ALMotion")
        # Call it to set stiffness method to recover if thermal error occurred to head
        self.motion_service.setStiffnesses("Body", 1)
        #self.face_detection.subscribe("HumanGreeter")

        self.cheers_frases = ["Good job!", "Cool!", "Awesome!", "I'm impressed!", "You smart!"]
        self.encorage_frases= ['Try again', 'You can do it!', 'Very close!', ]

    def cheers_movement(self):
        pass

    def game_introduction_movement(self):
        pass

    def launch_address(self, url):
        tablet_service = self.app.session.service("ALTabletService")
        print("PEPPER launching URL: ", url)
        tablet_service.showWebview(url)


    def start_detect_face(self):
        if not self.face_detect_active:
            self.face_detection.subscribe("HumanGreeter")
            self.ba_service.setEnabled(True)
            self.face_detect_active = True


    def stop_face_detect(self):
        if self.face_detect_active:
            self.face_detection.unsubscribe("HumanGreeter")
            self.ba_service.setEnabled(False)
            self.face_detect_active = False

    def start_ask(self, vocabulary):
        self.asr.pause(True)
        self.asr.setVocabulary(vocabulary, False)
        self.asr.pause(False)
        if not self.speech_recogn_active:
            self.asr.subscribe("SpeechRecognition")
            self.speech_recogn_active = True

    def stop_ask(self):
        if self.speech_recogn_active:
            self.asr.unsubscribe('SpeechRecognition')
            self.speech_recogn_active = False

    def on_word_recognized(self, value):
        print "Word received: ",value
        if self.current_state == STATE_WAITING_AGREE_TO_START:
            if value[0] == 'yes':
                self.current_state = STATE_WAIT_GAME
                self.launch_address(self.game_url)
                self.stop_face_detect()
                self.stop_ask()
            else:
                self.say("Please!")

    def on_human_tracked(self, value):
        if value == []:  # empty value when the face disappears
            print "Face disappeared"
        else:
            print "I saw a face!"
            if self.current_state == STATE_WAITING_USER:
                self.current_state = STATE_WAITING_AGREE_TO_START
                self.say("Hello, Do you want to play a game?")
                self.start_ask(['yes', 'no'])


    def close(self):
        print "Clearing subscriptions"
        if self.face_detect_active:
            self.face_detection.unsubscribe("HumanGreeter")
            self.face_detect_active = False

        self.fdsub.signal.disconnect(self.ch1)
        self.ba_service.setEnabled(False)
        self.leds_service.on('FaceLeds') # reset to white
        if self.speech_recogn_active:
            self.asr.unsubscribe('SpeechRecognition')
            self.speech_recogn_active = False

        self.srsub.signal.disconnect(self.ch2)
        self.posture_service.goToPosture("StandInit", 2.0)

    def say(self, message):
        self.tts.say(message)

    def on_init(self):
        self.launch_address(self.welcome_url)
        self.current_state = STATE_WAITING_USER
        self.start_detect_face()

    def on_welcome(self):
        #self.start_detect_face()
        pass

    def on_jump_to_game(self):
        self.current_state = STATE_WAIT_GAME
        self.stop_face_detect()
        self.stop_ask()
        self.launch_address(self.game_url)

    def on_game_init(self):
        print "Received initialization"
        if self.current_state == STATE_WAIT_GAME:
            self.current_state = STATE_PLAYING
            #self.motion_service.angleInterpolation(["HeadYaw", "HeadPitch"], [0, 0], 1.0, True)
            self.game_introduction_movement()
            self.say("Okay! Find all pokemon twins. You can do it!")

    def game_success_2(self):
        self.say("Wow! You are doing great!")

    def game_success_1(self):
        self.cheers_movement()
        self.say(self.cheers_frases[randint(0, len(self.cheers_frases) - 1)])

    def game_on_win(self):
        self.games_won += 1
        self.say("Wow! You did it! Try it again!")
        self.launch_address(self.game_url)

    def game_mistake_2(self):
        self.cheers_movement()
        self.say(self.encorage_frases[randint(0, len(self.encorage_frases) - 1)])

    def game_mistake_4(self):
        self.say("No problem, you can do it next time!")

