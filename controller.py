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

        # Get the services ALTextToSpeech and ALFaceDetection.
        self.tts = session.service("ALTextToSpeech")
        self.asr = session.service("ALSpeechRecognition")
        self.asr.setLanguage("English")
        self.face_detection = session.service("ALFaceDetection")
        self.posture_service = session.service("ALRobotPosture")
        self.motion_service = session.service("ALMotion")
        self.animated_speech = session.service("ALAnimatedSpeech")
        # Call it to set stiffness method to recover if thermal error occurred to head
        self.motion_service.setStiffnesses("Body", 1)

        self.cheers_frases = ["Good job!", "Cool!", "Awesome!", "I'm impressed!", "You're smart!"]
        self.encorage_frases= ['Try again', 'You can do it!', 'Very close!', ]
        self.asConf = {"bodyLanguageMode","contextual"}
        self.sonarValueList = ["Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value",
                          "Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value"]

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
                self.say("^start(animations/Stand/Gestures/Please_1) Please! ^wait(animations/Stand/Gestures/Please_1)")
                self.posture_service.goToPosture("StandInit", 2.0)

    def on_human_tracked(self, value):
        if value == []:  # empty value when the face disappears
            print "Face disappeared"
        else:
            print "I saw a face!"
            front_distance = self.memory.getListData(self.sonarValueList)[0]
            print front_distance
            if self.current_state == STATE_WAITING_USER and front_distance < 2:
                self.current_state = STATE_WAITING_AGREE_TO_START
                self.say("Hello! ^start(animations/Stand/Gestures/Hey_1) Do you want to play a game? ^wait(animations/Stand/Gestures/Hey_1)")
                self.posture_service.goToPosture("StandInit", 2.0)
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
        self.posture_service.goToPosture("StandInit", 4.0)


    def say(self,message):
        self.animated_speech.say(message)


    def on_init(self):
        print self.tts.getVolume()
        self.tts.setVolume(0.5)
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
            self.say("Okay! Find all pokemon twins. ^start(animations/Stand/Gestures/ShowTablet_2)! You can play on my tablet. ^wait(animations/Stand/Gestures/ShowTablet_2)")
            self.posture_service.goToPosture("StandInit", 3.0)

    def game_success_2(self):
        self.say("Wow! You are doing great!")

    def game_success_1(self):
        self.say(self.cheers_frases[randint(0, len(self.cheers_frases) - 1)])

    def game_on_win(self):
        self.games_won += 1
        self.say("Wow! You did it! Try it again!")
        self.launch_address(self.game_url)

    def game_mistake_2(self):
        self.say(self.encorage_frases[randint(0, len(self.encorage_frases) - 1)])

    def game_mistake_4(self):
        self.say("No problem, you can do it next time!")

