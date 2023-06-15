from aiogram import Bot
import random
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
    def __init__(self, l: list, bot: Bot):
        self.list_players = l  # ids of players
        self.time_of_day = "night"  # flag that defines day cycle
        self.status_game = True  # while status game == True - game run, endgame when status_game = False
        self.bot = bot  # bot from telegram

    async def game(self):
        await self.defineRoles()

        while self.status_game:  # main part of game
            if self.time_of_day == "night":
                # mafia chooses a victim
                # doctor chooses player to save
                # detective chooses player to check
                pass
            else:
                # citizens talks about who is mafia
                # Vote
                # one player leave the game
                # if number of citizens equals num of mafia, status_game = False and game end
                pass

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

        mafia = Roles.Mafia(list_mafia_id)  # Create class mafia and put ids mafia players
        await mafia.notifyMafias(self.bot)  # notify players
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # We have to complete defines roles
