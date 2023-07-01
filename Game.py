from aiogram import Bot, types, Dispatcher
import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import Roles


class SignUpForTheGame:  # class implements registration of players
    def __init__(self):
        self.players = list()

    def addPlayer(self, id):
        self.players.append(id)

    def checkPlayerInGame(self, id):
        if id not in self.players:
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
        self.status_game = None
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
        self.status_game = True  # while status game == True - game run, endgame when status_game = False

    async def game(self):
        await self.defineRoles()
        while self.status_game:
            if self.time_of_day == "night":
                await self.nightCycle()
            else:
                await self.dayCycle()

    # actions for night cycle
    async def nightCycle(self):
        await self.bot.send_message(chat_id=self.chat_id, text="The night is coming. "
                                                               "The city falls asleep, the mafia wakes up.")
        victim = await self.chooseVictim()
        self.killPlayer(victim)
        await self.bot.send_message(chat_id=victim, text="You were killed by the Mafia.")

        self.setDay()

    # actions for day cycle
    async def dayCycle(self):
        await self.bot.send_message(chat_id=self.chat_id, text="It's daytime. Discuss and vote for the Mafia.")
        self.setNight()

    # for Mafia players to choose a victim
    async def chooseVictim(self):
        self.votes = {player: 0 for player in self.__list_innocents}
        choosePlayers = InlineKeyboardMarkup(row_width=len(self.__list_innocents))
        for id in self.__list_innocents:
            username = await self.bot.get_chat_member(chat_id=self.chat_id, user_id=id)
            player = InlineKeyboardButton(text=username.user.username, callback_data="kill")
            choosePlayers.add(player)

        mafia_members = self.__mafia.getMafiaList()

        for member in mafia_members:
            await self.bot.send_message(chat_id=member, text="Choose a player to kill (write /kill @username)",
                                        reply_markup=choosePlayers)

        # Wait for the voting to complete
        while True:
            if sum(self.votes.values()) == len(mafia_members):
                print(sum(self.votes.values()))
                break

        # Find the player with the maximum votes
        victim_id = max(self.votes, key=self.votes.get)
        print("Victim id")
        print(victim_id)
        self.votes = {}  # Reset the votes dictionary for the next round of voting

        return victim_id

    async def getChatMemberIdByUsername(self, username):
        chat_member = await self.bot.get_chat_member(chat_id=self.chat_id, user_id=username)
        return chat_member.user.id

    def setDay(self):
        self.status_game = "day"

    def setNight(self):
        self.status_game = "night"

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
