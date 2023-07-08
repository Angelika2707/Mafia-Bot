from aiogram import Bot, types, Dispatcher
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

    def clearListPlayers(self):
        self.players.clear()


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
        self.__votes = None

    async def setInfo(self, l: list, bot: Bot, chat_id):
        self.list_players = l  # ids of players
        self.bot = bot  # bot from telegram
        self.chat_id = chat_id
        self.__vote_count = 0
        self.__votes = {}
        self.__killed_players = []

    async def start_game(self):
        self.time_of_day = "night"  # flag that defines day cycle

    # actions for night cycle
    async def nightCycle(self):
        self.setNight()
        await self.bot.send_message(chat_id=self.chat_id, text="The night is coming. "
                                                               "The city falls asleep")

        await self.bot.send_message(chat_id=self.chat_id, text="Mafia is waking up. They are choosing their victim")
        await self.showVoteToKill()

    # actions for day cycle
    async def dayCycle(self):
        self.setDay()
        if self.__killed_at_night is not None:
            await self.bot.send_message(chat_id=self.__killed_at_night.getId(), text="You were killed by mafia")
            await self.bot.send_message(chat_id=self.chat_id, text=f"Player {self.__killed_at_night.getName()} "
                                                                   f"was killed that night. His role is "
                                                                   f"{self.__killed_at_night.getRole().value}")
        else:
            await self.bot.send_message(chat_id=self.chat_id, text="Nobody died this night.")

        self.resetNightVictimMafia()
        await self.bot.send_message(chat_id=self.chat_id, text="It's daytime. Discuss and vote for the Mafia")

    # for Mafia players to choose a victim
    async def showVoteToKill(self):
        self.__votes = {player: 0 for player in self.__list_innocents}
        choosePlayers = InlineKeyboardMarkup(row_width=len(self.__list_innocents))
        for player in self.__list_innocents:
            username = player.getName()
            player_to_kill = InlineKeyboardButton(text=username, callback_data=username)
            choosePlayers.add(player_to_kill)

        mafia_members = self.__mafia.getMafiaList()

        for member in mafia_members:
            await self.bot.send_message(chat_id=member.getId(), text="Choose a player to kill",
                                        reply_markup=choosePlayers)

    async def getChatMemberByUsername(self, username):
        for player in self.__list_innocents:
            if player.getName() == username:
                return player
        return None

    def setDay(self):
        self.time_of_day = "day"

    def setNight(self):
        self.time_of_day = "night"

    def killPlayer(self, player):  # method for kill citizen
        self.list_players.remove(player)
        self.__killed_at_night = player
        self.__killed_players.append(player)

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
        self.__mafia = mafia
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        civilians = list(set(self.list_players).difference(set(list_mafia)))  # list of players without mafia
        self.__list_innocents = list(civilians)  # take list of innocents

        if len(self.list_players) > 3:
            doctor = random.choice(civilians)
            doctor.setRole(Roles.Role.DOCTOR)
            doctor = Roles.Doctor(doctor)  # Create doctor and notify player
            await doctor.notifyDoctor(self.bot)
            self.__doctor = doctor

            civilians.remove(doctor)  # list of players without mafia and doctor

        if len(self.list_players) > 5:
            detective = random.choice(civilians)
            detective.setRole(Roles.Role.DETECTIVE)
            detective = Roles.Detective(detective)  # Create detective and notify player
            await detective.notifyDetective(self.bot)
            self.__detective = detective

            civilians.remove(detective)  # list of citizens

        [player.setRole(Roles.Role.CITIZEN) for player in civilians]
        citizens = Roles.Citizen(civilians)  # Create citizens
        await citizens.notifyCitizens(self.bot)  # Notify players
        self.__citizens = citizens

        # We have to complete defines roles

    def getMafia(self):
        return self.__mafia

    def getPlayers(self):
        return self.list_players

    def getKilledPlayers(self):
        return self.__killed_players

    def updateVotes(self, player: Player):
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
