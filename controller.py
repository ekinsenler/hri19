class Controller:

    def __init__(self, session):
        self.pep_session = session
        self.tts = session.service("ALTextToSpeech")

    def say(self, message):
        self.tts.say(message)

    def on_init(self):
        print "Received initialization"

    def success_2(self):
        self.say("Wow! You are doing great!")

    def success_1(self):
        self.say("Good job!")

    def on_game_win(self):
        self.say("Wow! You did it!")

