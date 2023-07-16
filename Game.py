"""
This module controls the flow of the game.
It does player registration, keeps track of the day/night cycle, emergency game interruptions.
"""

from aiogram import Bot
import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import Roles


class Player:
    """
    Represents a player in the game.

    :param id: The player's ID.
    :param name: The player's username.
    """

    def __init__(self, id, name):
        self.__name = name
        self.__id = id
        self.__role = None

    def getName(self):
        """
        Get the username of the player.

        :return: The username of the player.
        """
        return self.__name

    def getId(self):
        """
        Get the ID of the player.

        :return: The ID of the player.
        """
        return self.__id

    def setRole(self, role: Roles.Role):
        """
        Set the role of the player.

        :param role: The role of the player.
        """
        self.__role = role

    def getRole(self):
        """
        Get the role of the player.

        :return: The role of the player.
        """
        return self.__role


class SignUpForTheGame:
    """
    Class that implements the registration of players for the game.
    """

    def __init__(self):
        self.players = list()
        self.ids = list()

    def dataReset(self):
        """
        Reset the player and ID lists.
        """
        self.players = list()
        self.ids = list()

    def addPlayer(self, id, name):
        """
        Add a player to the game.

        :param id: The player's ID.
        :param name: The player's username.
        """
        player = Player(id, name)
        self.players.append(player)
        self.ids.append(id)

    def checkPlayerInGame(self, id):
        """
        Check if a player is already in the game.

        :param id: The player's ID.
        :return: True if the player is in the game, False otherwise.
        """
        if id not in self.ids:
            return False
        else:
            return True

    def getNumberPlayers(self):
        """
        Get the number of players in the game.

        :return: The number of players in the game.
        """
        return len(self.players)


class Game:
    """
    Represents a game instance.

     Attributes:
        __vote_count (int): The count of votes during the day or night actions.
        __list_players (list): A list of Player objects representing the players in the game.
        __bot (Bot): The Telegram bot object.
        __chat_id (int): The ID of the chat.
        __time_of_day (str): The current time of the day (either "day" or "night").
        __mafia (Roles.Mafia): The Mafia role object.
        __citizens (Roles.Citizen): The Citizen role object.
        __doctor (Roles.Doctor): The Doctor role object.
        __detective (Roles.Detective): The Detective role object.
        __list_innocents (list): A list of players in the innocent team.
        __killed_at_night (Player): The player chosen by mafia for the kill at night.
        __killed_players (list): A list of players killed throughout the game.
        __healed_at_night (Player): The player chosen by doctor for to heal at night.
        __checked_at_night (Player): The player checked by the Detective during the night.
        __votes (dict): A dictionary mapping players to the number of votes they received.
        __status_game (bool): The status of the game (True if the game is ongoing, False otherwise).
        __active_roles (list): A list remaining of active roles in the game.
        __moved_at_night (dict): A dictionary mapping players with active roles to a boolean indicating whether they
        have taken action during the night.
        __who_voted_during_day (list): A list of players who have voted during the day.
    """

    def __init__(self):
        """
        Initialize a Game object.
        """
        self.__vote_count = None
        self.__list_players = None
        self.__bot = None
        self.__chat_id = None
        self.__time_of_day = None
        self.__mafia = None
        self.__citizens = None
        self.__doctor = None
        self.__detective = None
        self.__list_innocents = None
        self.__killed_at_night = None
        self.__killed_players = None
        self.__healed_at_night = None
        self.__checked_at_night = None
        self.__votes = None
        self.__status_game = False
        self.__active_roles = None
        self.__moved_at_night = None
        self.__who_voted_during_day = None

    def dataReset(self):
        """
        Reset the game data.
        """
        self.__vote_count = None
        self.__list_players = None
        self.__bot = None
        self.__chat_id = None
        self.__time_of_day = None
        self.__mafia = None
        self.__citizens = None
        self.__doctor = None
        self.__detective = None
        self.__list_innocents = None
        self.__killed_at_night = None
        self.__killed_players = None
        self.__healed_at_night = None
        self.__checked_at_night = None
        self.__votes = None
        self.__status_game = False
        self.__active_roles = None
        self.__moved_at_night = None
        self.__who_voted_during_day = None

    async def setInfo(self, l: list, bot: Bot, chat_id):
        """
        Set the game information.

        :param l: List of player IDs.
        :param bot: The Telegram bot.
        :param chat_id: The ID of the chat.
        """
        self.__list_players = l
        self.__bot = bot
        self.__chat_id = chat_id
        self.__vote_count = 0
        self.__votes = {}
        self.__killed_players = []
        self.__active_roles = []
        self.__moved_at_night = {}
        self.__who_voted_during_day = []

    async def start_game(self):
        """
        Start the game.
        """
        self.__time_of_day = "night"  # flag that defines day cycle
        self.__status_game = True

    async def nightCycle(self):
        """
        Perform the night cycle actions.
        """
        await self.check_players()
        if self.__status_game:
            self.setNight()
            await self.__bot.send_photo(chat_id=self.__chat_id, photo=open("images/night_city.jpg", "rb"))
            await self.__bot.send_message(chat_id=self.__chat_id, text="The night is coming. The city falls asleep")
            await self.showVoteToKill()  # give the mafia the opportunity to choose a victim
            await self.__bot.send_message(chat_id=self.__chat_id, text="Mafia is waking up. They are choosing their "
                                                                       "victim")
            # if there is a doctor or detective in the game, then let them choose a player for the night action
            if self.__doctor is not None:
                await self.showPlayersToHeal()
            if self.__detective is not None:
                await self.showPlayersToCheckRole()
        await self.check_players()

    async def dayCycle(self):
        """
        Perform the day cycle actions.
        """
        if self.__status_game:
            self.setDay()
            # actions if no one saved the player chosen by the mafia
            if self.__killed_at_night is not None and not (self.checkPlayerHealedByDoctor() or
                                                           self.checkPlayerSavedByDetective()):
                await self.killing(self.__killed_at_night)
                await self.__bot.send_message(chat_id=self.__killed_at_night.getId(), text="You were killed by mafia")
                await self.__bot.send_message(chat_id=self.__chat_id, text=f"Player {self.__killed_at_night.getName()} "
                                                                           "was killed that night. His role was "
                                                                           f"{self.__killed_at_night.getRole().value}")
            # actions if the player chosen by the mafia was saved by the doctor
            elif self.__killed_at_night is not None and self.checkPlayerHealedByDoctor():
                await self.__bot.send_message(chat_id=self.__chat_id, text=f"Player {self.__killed_at_night.getName()} "
                                                                           f"was saved that night. Doctor has "
                                                                           f"healed him")
            # actions if the player chosen by the mafia was saved by the detective
            elif self.__killed_at_night is not None and self.checkPlayerSavedByDetective():
                await self.__bot.send_message(chat_id=self.__chat_id, text=f"Player {self.__killed_at_night.getName()} "
                                                                           f"was saved that night. Detective scared "
                                                                           f"the mafia")
            # if the mafia didn't kill anyone
            else:
                await self.__bot.send_message(chat_id=self.__chat_id, text="Nobody died this night")

            self.resetMovedAtNight()
            self.resetNightVictimMafia()
            self.resetNightHealedPlayer()
            self.resetNightCheckedPlayer()
            await self.check_players()  # check conditions for win
            await self.__bot.send_photo(chat_id=self.__chat_id, photo=open("images/day_city.jpg", "rb"))
            await self.__bot.send_message(chat_id=self.__chat_id, text="It's daytime. Discuss and vote for the Mafia")
            await self.__bot.send_message(chat_id=self.__chat_id, text="Use command /start_voting to start voting for "
                                                                       "players")

    async def showVoteToKill(self):
        """
        Create and show mafia players a keyboard with players so that they can select a player to kill.
        """
        self.__votes = {player: 0 for player in self.__list_innocents}  # change dictionary to collect votes from mafia
        choosePlayers = InlineKeyboardMarkup(row_width=len(self.__list_innocents))
        for player in self.__list_innocents:
            username = player.getName()
            callback_data_mafia = "mafia_kill_" + username
            player_to_kill = InlineKeyboardButton(text=username, callback_data=callback_data_mafia)
            choosePlayers.add(player_to_kill)

        mafia_members = self.__mafia.getMafiaList()

        for member in mafia_members:
            await self.__bot.send_message(chat_id=member.getId(), text="Choose a player to kill",
                                          reply_markup=choosePlayers)

    async def showPlayersToHeal(self):
        """
        Create and show the doctor a keyboard with players so that he can select a player to heal.
        """
        choose_players = InlineKeyboardMarkup(row_width=len(self.__list_players))
        for player in self.__list_players:
            username = player.getName()
            callback_data_doctor = "doctor_heal_" + username
            player_to_heal = InlineKeyboardButton(text=username, callback_data=callback_data_doctor)
            choose_players.add(player_to_heal)

        doctor = self.__doctor.getDoctor()
        await self.__bot.send_message(chat_id=doctor.getId(), text="Choose a player to heal",
                                      reply_markup=choose_players)

    async def showPlayersToCheckRole(self):
        """
        Create and show the detective a keyboard with players so that he can select a player to check their role.
        """
        choose_players = InlineKeyboardMarkup(row_width=len(self.__list_players) - 1)
        for player in self.__list_players:
            if player != self.__detective.getDetective():
                username = player.getName()
                callback_data_detective = "detective_check_" + username
                player_to_check = InlineKeyboardButton(text=username, callback_data=callback_data_detective)
                choose_players.add(player_to_check)

        detective = self.__detective.getDetective()
        await self.__bot.send_message(chat_id=detective.getId(), text="Choose a player for checking role",
                                      reply_markup=choose_players)

    async def getChatMemberByUsername(self, username):
        """
        Get the chat member by their username.

        :param username: The username of the player.
        :return: The Player object or None if not found.
        """
        for player in self.__list_players:
            if player.getName() == username:
                return player
        return None

    def setDay(self):
        """
        Set the time to daytime.
        """
        self.__time_of_day = "day"

    def setNight(self):
        """
        Set the time of day to nighttime.
        """
        self.__time_of_day = "night"

    async def killPlayer(self, player):
        """
        Save the player selected by the mafia at night for killing.

        :param player: The player chosen to kill.
        """
        self.__killed_at_night = player

    async def healPlayer(self, player):
        """
        Save the player selected by the doctor at night for healing.

        :param player: The player chosen to heal.
        """
        self.__healed_at_night = player

    async def checkRoleOfPlayer(self, player):
        """
        Save the player selected by the detective at night for checking.

        :param player: The player chosen to check their role.
        """
        self.__checked_at_night = player

    async def killing(self, player):
        """
        Perform the killing of a player.

        :param player: The player to kill.
        """
        # general actions to kill a player
        self.__list_players.remove(player)
        self.__list_innocents.remove(player)
        self.__killed_players.append(player)
        # actions depending on the role of the player
        if player.getRole() == Roles.Role.DETECTIVE:
            self.__detective.setDetective(None)
            self.__moved_at_night.pop(Roles.Role.DETECTIVE)
            self.__active_roles.remove(Roles.Role.DETECTIVE)
        elif player.getRole() == Roles.Role.DOCTOR:
            self.__doctor.setDoctor(None)
            self.__moved_at_night.pop(Roles.Role.DOCTOR)
            self.__active_roles.remove(Roles.Role.DOCTOR)
        else:
            self.__citizens.removeFromCitizensList(player)

    async def deletePlayer(self, player):
        """
        Delete a player according to results of day voting.

        :param player: The player to be deleted.
        """
        # general actions to remove a player based on voting results
        self.__list_players.remove(player)
        self.__killed_players.append(player)
        # role dependent actions
        if player.getRole() == Roles.Role.MAFIA:
            self.__mafia.removeFromMafiaList(player)
        else:
            self.__list_innocents.remove(player)
            if player.getRole() == Roles.Role.DOCTOR:
                self.__doctor.setDoctor(None)
            elif player.getRole() == Roles.Role.DETECTIVE:
                self.__detective.setDetective(None)
            else:
                self.__citizens.removeFromCitizensList(player)

    async def defineRoles(self):
        """
        Define the roles for the players in the game.
        """
        # define mafias players
        number_of_mafia = int(len(self.__list_players) / 4)

        indexes_mafia_players = random.sample(range(len(self.__list_players)),
                                              k=number_of_mafia)  # choose random players to be mafia
        list_mafia = [self.__list_players[i] for i in indexes_mafia_players]  # list of mafia players
        [player.setRole(Roles.Role.MAFIA) for player in list_mafia]

        mafia = Roles.Mafia(list_mafia)  # Create instance of class mafia and put ids mafia players
        await mafia.notifyMafias(self.__bot)  # notify players
        await mafia.showMafiaTeammates(self.__bot)
        self.__mafia = mafia
        self.__active_roles.append(Roles.Role.MAFIA)

        civilians = list(set(self.__list_players).difference(set(list_mafia)))  # list of players without mafia
        self.__list_innocents = list(civilians)  # take list of innocents

        if len(self.__list_players) > 3:
            doctor_player = random.choice(civilians)
            doctor_player.setRole(Roles.Role.DOCTOR)
            doctor = Roles.Doctor(doctor_player)  # Create doctor and notify player
            await doctor.notifyDoctor(self.__bot)
            self.__doctor = doctor
            self.__active_roles.append(Roles.Role.DOCTOR)

            civilians.remove(doctor_player)  # list of players without mafia and doctor

        if len(self.__list_players) > 5:
            detective_player = random.choice(civilians)
            detective_player.setRole(Roles.Role.DETECTIVE)
            detective = Roles.Detective(detective_player)  # Create detective and notify player
            await detective.notifyDetective(self.__bot)
            self.__detective = detective
            self.__active_roles.append(Roles.Role.DETECTIVE)

            civilians.remove(detective_player)  # list of citizens

        [player.setRole(Roles.Role.CITIZEN) for player in civilians]
        citizens = Roles.Citizen(civilians)  # Create citizens
        await citizens.notifyCitizens(self.__bot)  # Notify players
        self.__citizens = citizens
        for role in self.__active_roles:
            self.__moved_at_night[role] = False

    async def check_players(self):
        """
        Check the number of players in the teams and end the game if the conditions for any of them to win are met.
        """
        number_mafia = len(self.__mafia.getMafiaList())
        if number_mafia == 0:
            self.__status_game = False
            await self.__bot.send_photo(chat_id=self.__chat_id, photo=open("images/citizens.jpg", "rb"))
            await self.__bot.send_message(chat_id=self.__chat_id,
                                          text="The number of citizens is bigger than the number "
                                               "of mafia. Citizens won!")
            self.dataReset()
        if number_mafia >= len(self.__list_innocents):
            self.__status_game = False
            await self.__bot.send_photo(chat_id=self.__chat_id, photo=open("images/mafia_together.jpg", "rb"))
            await self.__bot.send_message(chat_id=self.__chat_id,
                                          text="The number of citizens is equal to the number of "
                                               "mafia. Mafia won!")
            self.dataReset()

    def checkPlayerHealedByDoctor(self):
        """
        Check if player selected by mafia to kill was healed by the doctor.

        :return: True if the player was healed, False otherwise.
        """
        return self.__killed_at_night == self.__healed_at_night

    def checkPlayerSavedByDetective(self):
        """
        Check if player selected by mafia to kill was saved by the visit of the detective.

        :return: True if the player was saved, False otherwise.
        """
        return self.__killed_at_night == self.__checked_at_night

    def getMafia(self):
        """
        Get the Mafia instance.

        :return: The Mafia instance.
        """
        return self.__mafia

    def getPlayers(self):
        """
        Get the list of players in the game.

        :return: The list of players.
        """
        return self.__list_players

    def getKilledPlayers(self):
        """
        Get the list of killed or voted out players.

        :return: The list of killed or voted out players.
        """
        return self.__killed_players

    def updateVotes(self, player):
        """
        Update the votes for a player.

        :param player: The player to update the votes for.
        """
        self.__votes[player] += 1

    def updateVoteCount(self):
        """
        Update the vote count after player vote.
        """
        self.__vote_count += 1

    def resetVoteCount(self):
        """
        Reset the vote count after finishing voting.
        """
        self.__vote_count = 0

    def getVoteCount(self):
        """
        Get the vote count.

        :return: The vote count.
        """
        return self.__vote_count

    def getVotes(self):
        """
        Get the dictionary with votes.

        :return: The votes.
        """
        return self.__votes

    def resetVotes(self):
        """
        Reset the dictionary with votes.
        """
        self.__votes = {}

    def getChatId(self):
        """
        Get the chat ID.

        :return: The chat ID.
        """
        return self.__chat_id

    def resetNightVictimMafia(self):
        """
        Reset the victim chosen by mafia to kill during the night.
        """
        self.__killed_at_night = None

    def resetNightHealedPlayer(self):
        """
        Reset the player chosen by the doctor to heal during the night.
        """
        self.__healed_at_night = None

    def resetNightCheckedPlayer(self):
        """
        Reset the player chosen by the detective to check their role during the night.
        """
        self.__checked_at_night = None

    def setVotes(self, votes):
        """
        Get a dictionary with votes and set it as the dictionary used in the class.

        :param votes: The votes to set.
        """
        self.__votes = votes

    def resetMovedAtNight(self):
        """
        Reset night action flags for all remaining active roles.
        """
        for role in self.__active_roles:
            self.__moved_at_night[role] = False

    async def confirmMove(self, role: Roles.Role):
        """
        Confirm the move of an active role during the night.

        :param role: The role to confirm the move for.
        """
        self.__moved_at_night[role] = True

    async def checkNightMoves(self):
        """
        Check if all night moves of active roles have been confirmed (this is for checking that all active
        roles made a move at night).

        :return: True if all moves have been confirmed, False otherwise.
        """
        for moved in self.__moved_at_night.values():
            if not moved:
                return False
        return True

    def getWhoVoted(self):
        """
        Get the list of players who voted during the day.

        :return: The list of players who voted.
        """
        return self.__who_voted_during_day

    def resetWhoVoted(self):
        """
        Reset the list of players who voted during the day.
        """
        self.__who_voted_during_day = []

    def addVoter(self, player):
        """
        Add a player to the list of players who voted during the day (after getting a vote from player).

        :param player: The player to add.
        """
        self.__who_voted_during_day.append(player)

    def getTimeOfDay(self):
        """
        Get the time of day in the game.

        :return: The time of day. Possible values: "day" or "night".
        """
        return self.__time_of_day
