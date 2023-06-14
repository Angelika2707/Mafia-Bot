from aiogram import Bot
import random
import Roles


class SignUpForTheGame:
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
        self.list_players = l
        self.time_of_day = "night"
        self.status_game = True
        self.bot = bot

    async def game(self):
        await self.defineRoles()
        # while self.status_game:
        #     if self.time_of_day == "night":
        #         pass
        #     else:
        #         pass

    def setDay(self):
        self.status_game = "day"

    def setNight(self):
        self.status_game = "night"

    def killPlayer(self, id):
        self.list_players.remove(id)

    async def defineRoles(self):
        number_of_mafia = int(len(self.list_players) / 4)
        if number_of_mafia == 0:
            number_of_mafia = 1

        indexes_mafia_players = random.sample(range(len(self.list_players)), k=number_of_mafia)
        print(indexes_mafia_players)
        list_mafia_id = [self.list_players[i] for i in indexes_mafia_players]

        mafia = Roles.Mafia(list_mafia_id)
        await mafia.notifyMafias(self.bot)
