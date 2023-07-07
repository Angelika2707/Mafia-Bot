from aiogram import Bot, types, Dispatcher
import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import Roles


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
        self.list_players = None
        self.bot = None
        self.chat_id = None
        self.time_of_day = None
        self.__mafia = None
        self.__citizens = None
        self.__doctor = None
        self.__detective = None
        self.__list_innocents = None
        self.votes = {}

    async def setInfo(self, l: list, bot: Bot, chat_id):
        self.list_players = l  # ids of players
        self.bot = bot  # bot from telegram
        self.chat_id = chat_id

    async def start_game(self):
        self.time_of_day = "night"  # flag that defines day cycle

    # actions for night cycle
    async def nightCycle(self):
        self.setNight()
        await self.bot.send_message(chat_id=self.chat_id, text="The night is coming. "
                                                               "The city falls asleep, the mafia wakes up.")
        await self.showVoteToKill()

    # actions for day cycle
    async def dayCycle(self):
        self.setDay()
        await self.bot.send_message(chat_id=self.chat_id, text="Mafia has made its choice -_-")
        await self.bot.send_message(chat_id=self.chat_id, text="It's daytime. Discuss and vote for the Mafia.")

    # for Mafia players to choose a victim
    async def showVoteToKill(self):
        self.votes = {player: 0 for player in self.__list_innocents}
        choosePlayers = InlineKeyboardMarkup(row_width=len(self.__list_innocents))
        for player in self.__list_innocents:
            username = player.getName()
            player_to_kill = InlineKeyboardButton(text=username, callback_data=username)
            choosePlayers.add(player_to_kill)

        mafia_members = self.__mafia.getMafiaList()

        for member in mafia_members:
            await self.bot.send_message(chat_id=member.getId(), text="Choose a player to kill",
                                        reply_markup=choosePlayers)

    async def getChatMemberIdByUsername(self, username):
        chat_member = await self.bot.get_chat_member(chat_id=self.chat_id, user_id=username)
        return chat_member.user.id

    def setDay(self):
        self.time_of_day = "day"

    def setNight(self):
        self.time_of_day = "night"

    def killPlayer(self, id):  # method for kill citizen
        self.list_players.remove(id)

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
        list_mafia_id = [self.list_players[i] for i in indexes_mafia_players]  # list of player's id to write them msgs

        mafia = Roles.Mafia(list_mafia_id)  # Create instance of class mafia and put ids mafia players
        await mafia.notifyMafias(self.bot)  # notify players
        self.__mafia = mafia
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        civilians = list(set(self.list_players).difference(set(list_mafia_id)))  # list of players without mafia
        self.__list_innocents = list(civilians)  # take list of innocents

        if len(self.list_players) > 3:
            doctor_id = random.choice(civilians)
            doctor = Roles.Doctor(doctor_id)  # Create doctor and notify player
            await doctor.notifyDoctor(self.bot)
            self.__doctor = doctor

            civilians.remove(doctor_id)  # list of players without mafia and doctor

        if len(self.list_players) > 5:
            detective_id = random.choice(civilians)
            detective = Roles.Detective(detective_id)  # Create detective and notify player
            await detective.notifyDetective(self.bot)
            self.__detective = detective

            civilians.remove(detective_id)  # list of citizens

        citizens = Roles.Citizen(civilians)  # Create citizens
        await citizens.notifyCitizens(self.bot)  # Notify players
        self.__citizens = citizens

        # We have to complete defines roles


class Player:
    def __init__(self, id, name):
        self.__name = name
        self.__id = id

    def getName(self):
        return self.__name

    def getId(self):
        return self.__id
