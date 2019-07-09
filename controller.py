from random import randint

class Controller:

    def __init__(self, session):
        self.pep_session = session
        self.tts = session.service("ALTextToSpeech")
        self.cheers_frases = ["Good job!", "Cool!", "Awesome!", "I'm impressed!", "You smart!"]

    def say(self, message):
        self.tts.say(message)

    def on_init(self):
        print "Received initialization"
        self.say("Okay! Find all pokemon twins. You can do it!")

    def success_2(self):
        self.say("Wow! You are doing great!")

    def success_1(self):
        self.say(self.cheers_frases[randint(0, len(self.cheers_frases))])

    def on_game_win(self):
        self.say("Wow! You did it!")

