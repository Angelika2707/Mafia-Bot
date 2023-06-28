from aiogram import Bot


# file contains roles in mafia

class Citizen:
    def __init__(self, players):
        self.players = players

    async def notifyCitizens(self, bot: Bot):  # this method notify citizen players in game
        for id in self.players:
            await bot.send_message(chat_id=id, text="You are citizen")

    def getCitizensList(self):
        return self.players


class Mafia:
    def __init__(self, players):
        self.players = players
        print(self.players)

    async def notifyMafias(self, bot: Bot):   # this method notify mafia players in game
        for id in self.players:
            await bot.send_message(chat_id=id, text="You are mafia")

    def getMafiaList(self):
        return self.players


class Detective:
    def __init__(self, player):     # player - id of the player
        self.player = player

    async def notifyDetective(self, bot: Bot):   # this method notify detective player in game
        await bot.send_message(chat_id=self.player, text="You are detective")

    def getDetective(self):
        return self.player


class Doctor:
    def __init__(self, player):
        self.player = player

    async def notifyDoctor(self, bot: Bot):  # this method notify doctor player in game
        await bot.send_message(chat_id=self.player, text="You are doctor")

    def getDoctor(self):
        return self.player
