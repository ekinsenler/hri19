from random import randint

STATE_WAITING_USER = "STATE_WAITING_USER"
STATE_WAITING_AGREE_TO_START = "STATE_WAITING_AGREE_TO_START"
STATE_PLAYING = "STATE_PLAYING"


class Controller:

    def __init__(self, app, welcome_url, game_url):

        self.welcome_url = welcome_url
        self.game_url = game_url

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
        #self.face_detection.subscribe("HumanGreeter")

        self.current_state = STATE_WAITING_USER
        self.face_detect_active = False
        self.speech_recogn_active = False

        self.cheers_frases = ["Good job!", "Cool!", "Awesome!", "I'm impressed!", "You smart!"]

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

    def start_ask(self, ask_id, vocabulary):
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
        print value

    def on_human_tracked(self, value):
        print str(None) if len(value) == 0 else "some_face"

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

    def say(self, message):
        self.tts.say(message)

    def on_init(self):
        self.launch_address(self.welcome_url)
        self.current_state = STATE_WAITING_USER

    def on_welcome(self):
        self.start_detect_face()

    def on_jump_to_game(self):
        self.launch_address(self.game_url)

    def on_game_init(self):
        print "Received initialization"
        self.say("Okay! Find all pokemon twins. You can do it!")

    def game_success_2(self):
        self.say("Wow! You are doing great!")

    def game_success_1(self):
        self.say(self.cheers_frases[randint(0, len(self.cheers_frases))])

    def game_on_win(self):
        self.say("Wow! You did it!")

