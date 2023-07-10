from aiogram import Bot
from enum import Enum

# file contains roles in mafia


class Role(Enum):
    CITIZEN = 'citizen'
    DETECTIVE = 'detective'
    MAFIA = 'mafia'
    DOCTOR = 'doctor'


class Citizen:
    def __init__(self, players):
        self.__players = players

    async def notifyCitizens(self, bot: Bot):  # this method notify citizen players in game
        for player in self.__players:
            await bot.send_message(chat_id=player.getId(), text=f"You are {Role.CITIZEN.value}")

    def getCitizensList(self):
        return self.__players

    def setCitizensList(self, list):
        self.__players = list

    def removeFromCitizensList(self, player):
        self.__players.remove(player)


class Mafia:
    def __init__(self, players):
        self.__players = players

    async def notifyMafias(self, bot: Bot):  # this method notify mafia players in game
        for player in self.__players:
            await bot.send_message(chat_id=player.getId(), text=f"You are {Role.MAFIA.value}")

    def getMafiaList(self):
        return self.__players

    def setMafiaList(self, list):
        self.__players = list

    def removeFromMafiaList(self, player):
        self.__players.remove(player)

    async def showMafiaTeammates(self, bot: Bot):
        if len(self.__players) == 1:
            return
        else:
            for player in self.__players:
                teammates = [p.getName() for p in self.__players if p != player]
                await bot.send_message(chat_id=player.getId(), text=f"Your Mafia teammates: {', '.join(teammates)}")

    async def showRemainingMafiaTeammates(self, bot: Bot):
        if len(self.__players) == 1:
            return
        else:
            for player in self.__players:
                teammates = [p.getName() for p in self.__players if p != player]
                await bot.send_message(chat_id=player.getId(), text="You have lost one of your teammates")
                await bot.send_message(chat_id=player.getId(), text=f"Remaining Mafia teammates: {', '.join(teammates)}")


class Detective:
    def __init__(self, player):  # player - id of the player
        self.__player = player

    async def notifyDetective(self, bot: Bot):  # this method notify detective player in game
        await bot.send_message(chat_id=self.__player.getId(), text=f"You are {Role.DETECTIVE.value}")

    def getDetective(self):
        return self.__player

    def setDetective(self, player):
        self.__player = player


class Doctor:
    def __init__(self, player):
        self.__player = player

    async def notifyDoctor(self, bot: Bot):  # this method notify doctor player in game
        await bot.send_message(chat_id=self.__player.getId(), text=f"You are {Role.DOCTOR.value}")

    def getDoctor(self):
        return self.__player

    def setDoctor(self, player):
        self.__player = player
