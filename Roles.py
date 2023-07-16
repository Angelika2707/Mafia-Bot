"""
This module defines role in the gameпо.
Classes notify players of their role, stores lists of players with the same roles.
"""

from aiogram import Bot
from enum import Enum


class Role(Enum):
    """
    Represents roles in the game.
    """

    CITIZEN = 'citizen'
    DETECTIVE = 'detective'
    MAFIA = 'mafia'
    DOCTOR = 'doctor'


class Citizen:
    """
    Represents a citizen in the game.

    :param players: Players that was defined as citizens.
    """
    def __init__(self, players):
        self.__players = players

    async def notifyCitizens(self, bot: Bot):
        """
        Notify citizens about their role in the game.

        :param bot: The Telegram bot.
        """
        for player in self.__players:
            await bot.send_message(chat_id=player.getId(), text=f"You are {Role.CITIZEN.value}")

    def getCitizensList(self):
        """
        Get the list of citizens.

        :return: List of citizen.
        """
        return self.__players

    def setCitizensList(self, list_players):
        """
        Set the list of citizens.

        :param list_players: List of citizens.
        """
        self.__players = list_players

    def removeFromCitizensList(self, player):
        """
        Remove a player from the list of citizens.

        :param player: The player to remove.
        """
        self.__players.remove(player)


class Mafia:
    """
    Represents a mafia in the game.

    :param players: Players that was defined as mafia.
    """
    def __init__(self, players):
        self.__players = players

    async def notifyMafias(self, bot: Bot):
        """
        Notify mafia about their role in the game.

        :param bot: The Telegram bot.
        """
        for player in self.__players:
            await bot.send_message(chat_id=player.getId(), text=f"You are {Role.MAFIA.value}")

    def getMafiaList(self):
        """
        Get the list of mafia players.

        :return: List of mafia players.
        """
        return self.__players

    def setMafiaList(self, list_players):
        """
        Set the list of mafia players.

        :param list_players: List of mafia players.
        """
        self.__players = list_players

    def removeFromMafiaList(self, player):
        """
        Remove a player from the list of mafia players.

        :param player: The player to remove.
        """
        self.__players.remove(player)

    async def showMafiaTeammates(self, bot: Bot):
        """
        Show the mafia teammates to each mafia player.

        :param bot: The Telegram bot.
        """
        if len(self.__players) == 1:
            return
        else:
            for player in self.__players:
                teammates = [p.getName() for p in self.__players if p != player]
                await bot.send_message(chat_id=player.getId(), text=f"Your Mafia teammates: {', '.join(teammates)}")

    async def showRemainingMafiaTeammates(self, bot: Bot):
        """
        Show the remaining mafia teammates to each mafia player after one teammate is voted out.

        :param bot: The Telegram bot.
        """
        if len(self.__players) == 1:
            return
        else:
            for player in self.__players:
                teammates = [p.getName() for p in self.__players if p != player]
                await bot.send_message(chat_id=player.getId(), text="You have lost one of your teammates")
                await bot.send_message(chat_id=player.getId(), text=f"Remaining Mafia teammates: {', '.join(teammates)}")


class Detective:
    """
    Represents a detective in the game.

    :param player: A player that was defined as a detective.
    """
    def __init__(self, player):  # player - id of the player
        self.__player = player

    async def notifyDetective(self, bot: Bot):
        """
        Notify the detective about their role in the game.

        :param bot: The Telegram bot.
        """
        await bot.send_message(chat_id=self.__player.getId(), text=f"You are {Role.DETECTIVE.value}")

    def getDetective(self):
        """
        Get the detective player.

        :return: The detective player.
        """
        return self.__player

    def setDetective(self, player):
        """
        Set the detective player.

        :param player: The detective player.
        """
        self.__player = player


class Doctor:
    """
    Represents a doctor in the game.

    :param player: A players that was defined as a doctor.
    """
    def __init__(self, player):
        self.__player = player

    async def notifyDoctor(self, bot: Bot):
        """
        Notify the doctor about their role in the game.

        :param bot: The Telegram bot.
        """
        await bot.send_message(chat_id=self.__player.getId(), text=f"You are {Role.DOCTOR.value}")

    def getDoctor(self):
        """
        Get the doctor player.

        :return: The doctor player.
        """
        return self.__player

    def setDoctor(self, player):
        """
        Set the doctor player.

        :param player: The doctor player.
        """
        self.__player = player
