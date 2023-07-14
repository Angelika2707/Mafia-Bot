from aiogram import Bot
import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import Roles


class Player:
    def __init__(self, id, name):
        self.__name = name
        self.__id = id
        self.__role = None

    def getName(self):
        return self.__name

    def getId(self):
        return self.__id

    def setRole(self, role: Roles.Role):
        self.__role = role

    def getRole(self):
        return self.__role


class SignUpForTheGame:  # class implements registration of players
    def __init__(self):
        self.players = list()
        self.ids = list()

    def dataReset(self):
        self.players = list()
        self.ids = list()

    def addPlayer(self, id, name):
        player = Player(id, name)
        self.players.append(player)
        self.ids.append(id)

    def checkPlayerInGame(self, id):
        if id not in self.ids:
            return False
        else:
            return True

    def getNumberPlayers(self):
        return len(self.players)


class Game:
    def __init__(self):
        self.__vote_count = None
        self.list_players = None
        self.bot = None
        self.chat_id = None
        self.time_of_day = None
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

    def dataReset(self):
        self.__vote_count = None
        self.list_players = None
        self.bot = None
        self.chat_id = None
        self.time_of_day = None
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

    async def setInfo(self, l: list, bot: Bot, chat_id):
        self.list_players = l  # ids of players
        self.bot = bot  # bot from telegram
        self.chat_id = chat_id
        self.__vote_count = 0
        self.__votes = {}
        self.__killed_players = []
        self.__active_roles = []
        self.__moved_at_night = {}

    async def start_game(self):
        self.time_of_day = "night"  # flag that defines day cycle
        self.__status_game = True

    # actions for night cycle
    async def nightCycle(self):
        await self.check_players()
        if self.__status_game:
            self.setNight()
            await self.bot.send_message(chat_id=self.chat_id, text="The night is coming. "
                                                                   "The city falls asleep")
            await self.showVoteToKill()
            await self.bot.send_message(chat_id=self.chat_id, text="Mafia is waking up. They are choosing their victim")
            if self.__doctor is not None:
                await self.showPlayersToHeal()
            if self.__detective is not None:
                await self.showPlayersToCheckRole()
        await self.check_players()

    # actions for day cycle
    async def dayCycle(self):
        if self.__status_game:
            self.setDay()
            if self.__killed_at_night is not None and not (self.checkPlayerHealedByDoctor() or
                                                           self.checkPlayerSavedByDetective()):
                await self.killing(self.__killed_at_night)
                await self.bot.send_message(chat_id=self.__killed_at_night.getId(), text="You were killed by mafia")
                await self.bot.send_message(chat_id=self.chat_id, text=f"Player {self.__killed_at_night.getName()} "
                                                                       f"was killed that night. His role is "
                                                                       f"{self.__killed_at_night.getRole().value}")
            elif self.__killed_at_night is not None and self.checkPlayerHealedByDoctor():
                await self.bot.send_message(chat_id=self.chat_id, text=f"Player {self.__killed_at_night.getName()} "
                                                                       f"was saved that night. Doctor has healed him")
            elif self.__killed_at_night is not None and self.checkPlayerSavedByDetective():
                await self.bot.send_message(chat_id=self.chat_id, text=f"Player {self.__killed_at_night.getName()} "
                                                                       f"was saved that night. Detective scared "
                                                                       f"the mafia")
            else:
                await self.bot.send_message(chat_id=self.chat_id, text="Nobody died this night")

            self.resetMovedAtNight()
            self.resetNightVictimMafia()
            self.resetNightHealedPlayer()
            await self.check_players()
            await self.bot.send_message(chat_id=self.chat_id, text="It's daytime. Discuss and vote for the Mafia")
            await self.bot.send_message(chat_id=self.chat_id, text="Use command /start_voting to start voting for "
                                                                   "players")

    # for Mafia players to choose a victim
    async def showVoteToKill(self):
        self.__votes = {player: 0 for player in self.__list_innocents}
        choosePlayers = InlineKeyboardMarkup(row_width=len(self.__list_innocents))
        for player in self.__list_innocents:
            username = player.getName()
            callback_data_mafia = "mafia_kill_" + username
            player_to_kill = InlineKeyboardButton(text=username, callback_data=callback_data_mafia)
            choosePlayers.add(player_to_kill)

        mafia_members = self.__mafia.getMafiaList()

        for member in mafia_members:
            await self.bot.send_message(chat_id=member.getId(), text="Choose a player to kill",
                                        reply_markup=choosePlayers)

    async def showPlayersToHeal(self):
        choosePlayers = InlineKeyboardMarkup(row_width=len(self.list_players))
        for player in self.list_players:
            username = player.getName()
            callback_data_doctor = "doctor_heal_" + username
            player_to_heal = InlineKeyboardButton(text=username, callback_data=callback_data_doctor)
            choosePlayers.add(player_to_heal)

        doctor = self.__doctor.getDoctor()
        await self.bot.send_message(chat_id=doctor.getId(), text="Choose a player to heal", reply_markup=choosePlayers)

    async def showPlayersToCheckRole(self):
        choosePlayers = InlineKeyboardMarkup(row_width=len(self.list_players) - 1)
        for player in self.list_players:
            if player != self.__detective.getDetective():
                username = player.getName()
                callback_data_detective = "detective_check_" + username
                player_to_check = InlineKeyboardButton(text=username, callback_data=callback_data_detective)
                choosePlayers.add(player_to_check)

        detective = self.__detective.getDetective()
        await self.bot.send_message(chat_id=detective.getId(), text="Choose a player for checking role",
                                    reply_markup=choosePlayers)

    async def getChatMemberByUsername(self, username):
        for player in self.list_players:
            if player.getName() == username:
                return player
        return None

    def setDay(self):
        self.time_of_day = "day"

    def setNight(self):
        self.time_of_day = "night"

    async def killPlayer(self, player):
        self.__killed_at_night = player

    async def healPlayer(self, player):
        self.__healed_at_night = player

    async def checkRoleOfPlayer(self, player):
        self.__checked_at_night = player

    async def killing(self, player):
        self.list_players.remove(player)
        self.__list_innocents.remove(player)
        self.__killed_players.append(player)
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

    async def voteOut(self, player):
        self.list_players.remove(player)
        self.__killed_players.append(player)
        print(self.__killed_players)
        if player.getRole() == Roles.Role.MAFIA:
            self.__mafia.removeFromMafiaList(player)
        elif player.getRole() == Roles.Role.CITIZEN:
            self.__citizens.removeFromCitizensList(player)
            self.__list_innocents.remove(player)

    async def defineRoles(self):
        # DEFINE MAFIAS PLAYERS
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        number_of_mafia = int(len(self.list_players) / 4)

        # it is for debugging, delete in release
        # -------------------------------
        if number_of_mafia == 0:
            number_of_mafia = 1
        # -------------------------------

        indexes_mafia_players = random.sample(range(len(self.list_players)),
                                              k=number_of_mafia)  # choose random players to be mafia
        list_mafia = [self.list_players[i] for i in indexes_mafia_players]  # list of mafia players
        [player.setRole(Roles.Role.MAFIA) for player in list_mafia]

        mafia = Roles.Mafia(list_mafia)  # Create instance of class mafia and put ids mafia players
        await mafia.notifyMafias(self.bot)  # notify players
        await mafia.showMafiaTeammates(self.bot)
        self.__mafia = mafia
        self.__active_roles.append(Roles.Role.MAFIA)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        civilians = list(set(self.list_players).difference(set(list_mafia)))  # list of players without mafia
        self.__list_innocents = list(civilians)  # take list of innocents

        if len(self.list_players) > 3:
            doctor_player = random.choice(civilians)
            doctor_player.setRole(Roles.Role.DOCTOR)
            doctor = Roles.Doctor(doctor_player)  # Create doctor and notify player
            await doctor.notifyDoctor(self.bot)
            self.__doctor = doctor
            self.__active_roles.append(Roles.Role.DOCTOR)

            civilians.remove(doctor_player)  # list of players without mafia and doctor

        if len(self.list_players) > 3:
            detective_player = random.choice(civilians)
            detective_player.setRole(Roles.Role.DETECTIVE)
            detective = Roles.Detective(detective_player)  # Create detective and notify player
            await detective.notifyDetective(self.bot)
            self.__detective = detective
            self.__active_roles.append(Roles.Role.DETECTIVE)

            civilians.remove(detective_player)  # list of citizens

        [player.setRole(Roles.Role.CITIZEN) for player in civilians]
        citizens = Roles.Citizen(civilians)  # Create citizens
        await citizens.notifyCitizens(self.bot)  # Notify players
        self.__citizens = citizens
        for role in self.__active_roles:
            self.__moved_at_night[role] = False

    async def check_players(self):
        number_mafia = len(self.__mafia.getMafiaList())
        if number_mafia == 0:
            self.__status_game = False
            await self.bot.send_message(chat_id=self.chat_id, text="The number of citizens is bigger than the number "
                                                                   "of mafia. Citizens won!")
            self.dataReset()
        if number_mafia >= len(self.__citizens.getCitizensList()):
            self.__status_game = False
            await self.bot.send_message(chat_id=self.chat_id, text="The number of citizens is equal to the number of "
                                                                   "mafia. Mafia won!")
            self.dataReset()

    def checkPlayerHealedByDoctor(self):
        return self.__killed_at_night == self.__healed_at_night

    def checkPlayerSavedByDetective(self):
        return self.__killed_at_night == self.__checked_at_night

    def getMafia(self):
        return self.__mafia

    def getPlayers(self):
        return self.list_players

    def getKilledPlayers(self):
        return self.__killed_players

    def updateVotes(self, player):
        self.__votes[player] += 1

    def updateVoteCount(self):
        self.__vote_count += 1

    def resetVoteCount(self):
        self.__vote_count = 0

    def getVoteCount(self):
        return self.__vote_count

    def getVotes(self):
        return self.__votes

    def resetVotes(self):
        self.__votes = {}

    def getChatId(self):
        return self.chat_id

    def getBot(self):
        return self.bot

    def resetNightVictimMafia(self):
        self.__killed_at_night = None

    def resetNightHealedPlayer(self):
        self.__healed_at_night = None

    def setVotes(self, votes):
        self.__votes = votes

    def resetMovedAtNight(self):
        for role in self.__active_roles:
            self.__moved_at_night[role] = False

    async def confirmMove(self, role: Roles.Role):
        self.__moved_at_night[role] = True

    async def checkNightMoves(self):
        print(self.__moved_at_night)
        for moved in self.__moved_at_night.values():
            if not moved:
                return False
        return True
