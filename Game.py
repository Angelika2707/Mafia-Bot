import asyncio

from aiogram import Bot
import random

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import Roles


# Galia was here


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
    def __init__(self, l: list, bot: Bot, chat_id):
        self.list_players = l  # ids of players
        self.time_of_day = "night"  # flag that defines day cycle
        self.status_game = True  # while status game == True - game run, endgame when status_game = False
        self.bot = bot  # bot from telegram
        self.list_innocents = []
        self.list_mafia = []
        self.chat_id = chat_id

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
        victim = await self.chooseVictim(self.list_mafia)
        self.killPlayer(victim)
        await self.bot.send_message(chat_id=victim, text="You were killed by the Mafia.")

        self.setDay()

    # actions for day cycle
    async def dayCycle(self):
        await self.bot.send_message(chat_id=self.chat_id, text="It's daytime. Discuss and vote for the Mafia.")
        # we need to add voting
        eliminated_player = random.choice(self.list_innocents)  # for debug
        self.killPlayer(eliminated_player)
        await self.bot.send_message(chat_id=eliminated_player, text="You have been eliminated from the game.")

        # check conditions for ending a game
        num_citizens = len(self.list_innocents)
        num_mafia = len(self.list_mafia)
        if num_citizens <= num_mafia:
            self.status_game = False
            await self.bot.send_message(chat_id=self.chat_id, text="The Mafia has won!")
        elif num_mafia == 0:
            self.status_game = False
            await self.bot.send_message(chat_id=self.chat_id, text="Citizens have won!")
        else:
            self.setNight()

    # for Mafia players to choose a victim
    async def chooseVictim(self, mafia):
        panel_markup = InlineKeyboardMarkup(row_width=1)
        buttons = []

        for player_id in self.list_innocents:       # add buttons with every innocent player name
            player_name = await self.bot.get_chat_member(self.group_id, player_id)
            button = InlineKeyboardButton(text=player_name.user.full_name, callback_data=str(player_id))
            buttons.append(button)

        panel_markup.add(*buttons)

        for player in mafia:    # send message to Mafia players
            await self.bot.send_message(chat_id=player, text="Choose a victim:", reply_markup=panel_markup)

        # choose victim
        victim = None
        while victim is None:
            try:
                response = await self.bot.wait_for('callback_query', timeout=60) # 60 seconds for choosing
                victim = response.data
            except asyncio.TimeoutError:
                for player in mafia:
                    await self.bot.send_message(chat_id=player, text="Time is out. No victim chosen.")

        return victim

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
        self.list_mafia = list_mafia_id # need to put list of mafia players from Mafia class, not from here (to solve)

        mafia = Roles.Mafia(list_mafia_id)  # Create class mafia and put ids mafia players
        await mafia.notifyMafias(self.bot)  # notify players
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        civilians = list(set(self.list_players).difference(set(list_mafia_id)))     # list of players without mafia
        self.list_innocents = civilians # take list of innocents

        doctor_id = random.choice(civilians)
        doctor = Roles.Doctor(doctor_id)        # Create doctor and notify player
        await doctor.notifyDoctor(self.bot)

        civilians.remove(doctor_id)   # list of players without mafia and doctor

        detective_id = random.choice(civilians)
        detective = Roles.Detective(detective_id)       # Create detective and notify player
        await detective.notifyDetective(self.bot)

        civilians.remove(detective_id)    # list of citizens
        citizens = Roles.Citizen(civilians)       # Create citizens
        await citizens.notifyCitizens(self.bot)     # Notify players

        # We have to complete defines roles
