from aiogram import Bot
from enum import Enum


class Role(Enum):
    CITIZEN = 'citizen'
    DETECTIVE = 'detective'
    MAFIA = 'mafia'
    DOCTOR = 'doctor'


class Citizen:
    def __init__(self, players):
        self.__players = players

    async def notify_citizens(self, bot: Bot):
        """
        Notify citizens about their role in the game.

        :param bot: The Telegram bot.
        """
        for player in self.__players:
            await bot.send_message(chat_id=player.get_id(), text=f"You are {Role.CITIZEN.value}")

    def get_citizens_list(self):
        """
        Get the list of citizens.

        :return: List of citizen.
        """
        return self.__players

    def set_citizens_list(self, list_players):
        """
        Set the list of citizens.

        :param list_players: List of citizens.
        """
        self.__players = list_players

    def remove_from_citizens_list(self, player):
        """
        Remove a player from the list of citizens.

        :param player: The player to remove.
        """
        self.__players.remove(player)


class Mafia:
    def __init__(self, players):
        self.__players = players

    async def notify_mafias(self, bot: Bot):
        """
        Notify mafia about their role in the game.

        :param bot: The Telegram bot.
        """
        for player in self.__players:
            await bot.send_message(chat_id=player.get_id(), text=f"You are {Role.MAFIA.value}")

    def get_mafia_list(self):
        """
        Get the list of mafia players.

        :return: List of mafia players.
        """
        return self.__players

    def set_mafia_list(self, list_players):
        """
        Set the list of mafia players.

        :param list_players: List of mafia players.
        """
        self.__players = list_players

    def remove_from_mafia_list(self, player):
        """
        Remove a player from the list of mafia players.

        :param player: The player to remove.
        """
        self.__players.remove(player)

    async def show_mafia_teammates(self, bot: Bot):
        """
        Show the mafia teammates to each mafia player.

        :param bot: The Telegram bot.
        """
        if len(self.__players) == 1:
            return
        else:
            for player in self.__players:
                teammates = [p.get_name() for p in self.__players if p != player]
                await bot.send_message(chat_id=player.get_id(), text=f"Your Mafia teammates: {', '.join(teammates)}")

    async def show_remaining_mafia_teammates(self, bot: Bot):
        """
        Show the remaining mafia teammates to each mafia player after one teammate is voted out.

        :param bot: The Telegram bot.
        """
        if len(self.__players) == 1:
            return
        else:
            for player in self.__players:
                teammates = [p.get_name() for p in self.__players if p != player]
                await bot.send_message(chat_id=player.get_id(), text="You have lost one of your teammates")
                await bot.send_message(chat_id=player.get_id(),
                                       text=f"Remaining Mafia teammates: {', '.join(teammates)}")


class Detective:
    def __init__(self, player):  # player - id of the player
        self.__player = player

    async def notify_detective(self, bot: Bot):
        """
        Notify the detective about their role in the game.

        :param bot: The Telegram bot.
        """
        await bot.send_message(chat_id=self.__player.get_id(), text=f"You are {Role.DETECTIVE.value}")

    def get_detective(self):
        """
        Get the detective player.

        :return: The detective player.
        """
        return self.__player

    def set_detective(self, player):
        """
        Set the detective player.

        :param player: The detective player.
        """
        self.__player = player


class Doctor:
    def __init__(self, player):
        self.__player = player

    async def notify_doctor(self, bot: Bot):
        """
        Notify the doctor about their role in the game.

        :param bot: The Telegram bot.
        """
        await bot.send_message(chat_id=self.__player.get_id(), text=f"You are {Role.DOCTOR.value}")

    def get_doctor(self):
        """
        Get the doctor player.

        :return: The doctor player.
        """
        return self.__player

    def set_doctor(self, player):
        """
        Set the doctor player.

        :param player: The doctor player.
        """
        self.__player = player
