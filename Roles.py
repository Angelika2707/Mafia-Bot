from aiogram import types, Bot


class Citizen:
    def __init__(self, *players):
        self.players = players

    def notifyCitizens(self, bot: Bot):
        for id in self.players:
            bot.send_message(chat_id=id, text="You are citizen")


class Mafia:
    def __init__(self, *players):
        self.players = players

    def notifyMafias(self, bot: Bot):
        for id in self.players:
            bot.send_message(chat_id=id, text="You are mafia")


class Detective:
    def __init__(self, player):
        self.player = player

    def notifyDetective(self, bot: Bot):
        bot.send_message(chat_id=self.player, text="You are detective")


class Doctor:
    def __init__(self, player):
        self.player = player

    def notifyDoctor(self, bot: Bot):
        bot.send_message(chat_id=self.player, text="You are doctor")
