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
# State of offer user to play again
STATE_WAITING_OFFER_PLAY_AGAIN = "STATE_WAITING_OFFER_PLAY_AGAIN"


class Controller:

    def __init__(self, app, welcome_url, game_url):

        self.welcome_url = welcome_url
        self.game_url = game_url

        self.current_state = None
        self.face_detect_active = False
        self.speech_recogn_active = False

        self.cheers_frases = ["Good job!", "Cool!", "Awesome!", "I'm impressed!", "You're smart!"]
        self.encorage_frases = ['Try again', 'You can do it!', 'Very close!', ]
        self.begging = ['Please!', "Play! It's fine", 'Oh, come on!', ]
        self.asConf = {"bodyLanguageMode", "contextual"}
        self.sonarValueList = ["Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value",
                               "Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value"]

        self.positive_answers = ["yes", "sure", "okay", "fine"]
        self.answers = ["no"]
        self.answers.extend(self.positive_answers)

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
        #self.motion_service.setStiffnesses("RHand", 1)

    def _get_random_item(self, inp_list):
        return inp_list[randint(0, len(inp_list) - 1)]

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
            if value[0] in self.positive_answers:
                self.current_state = STATE_WAIT_GAME
                self.launch_address(self.game_url)
                self.stop_face_detect()
                self.stop_ask()
            else:
                self.say("^start(animations/Stand/Gestures/Please_1) %s ^wait(animations/Stand/Gestures/Please_1)" % self._get_random_item(self.begging))
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
                self.say("Hello! ^start(animations/Stand/Emotions/Positive/Happy_4) Do you want to play a game?")
                self.start_ask(self.answers)


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
        if self.current_state == STATE_WAITING_OFFER_PLAY_AGAIN:
            if self.games_won == 1:
                text = "You won your first game!"
            else:
                text = "You won %s times!" % self.games_won
            self.say("^start(animations/Stand/Gestures/Yes_1) " + text + " One more?")
            self.current_state = STATE_WAITING_AGREE_TO_START
            self.start_ask(self.answers)

    def on_jump_to_game(self):
        self.current_state = STATE_WAIT_GAME
        self.stop_face_detect()
        self.stop_ask()
        self.launch_address(self.game_url)

    def on_game_init(self):
        print "Received initialization"
        if self.current_state == STATE_WAIT_GAME:
            self.current_state = STATE_PLAYING
            if self.games_won > 0:
                text = "Okay! Let's start!"
            else:
                text = "Okay! Find all pokemon twins! ^start(animations/Stand/Gestures/ShowTablet_2) You can play on my tablet. ^stop(animations/Stand/Gestures/ShowTablet_2)"
            self.say(text)
            self.posture_service.goToPosture("StandInit", 0.5)

    def game_success_2(self):
        self.say("Wow! You are doing great!")

    def game_success_1(self):
        self.say(self._get_random_item(self.cheers_frases))

    def game_on_win(self):
        self.games_won += 1
        self.say("^start(animations/Stand/Gestures/Enthusiastic_4) Wow! You did it!")
        self.current_state = STATE_WAITING_OFFER_PLAY_AGAIN
        self.launch_address(self.welcome_url)

    def game_mistake_2(self):
        self.say(self._get_random_item(self.encorage_frases))

    def game_mistake_4(self):
        self.say("No problem, you can do it next time!")

