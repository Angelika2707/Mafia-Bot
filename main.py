from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Game import SignUpForTheGame, Game, Player

TOKEN = '5990396163:AAGOgKqVWSHStXo0CaD-kkD8lCxXdtCnmfY'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
main_game = Game()

# class from Game.py for registration
registrationPlayers = SignUpForTheGame()

# create inline keyboard for registration
registrationKeyBoard = InlineKeyboardMarkup(row_width=1)
registration = InlineKeyboardButton(text="Register", callback_data="register")
registrationKeyBoard.add(registration)


# process callback to registrate player
@dp.callback_query_handler(lambda callback: callback.data == "register")
async def register(callback: types.CallbackQuery):
    print(callback.from_user.id)
    if registrationPlayers.checkPlayerInGame(callback.from_user.id):
        await bot.send_message(chat_id=callback.from_user.id, text="You are already in the game!")
    else:
        await bot.send_message(chat_id=callback.from_user.id, text="You are in the game!")
        registrationPlayers.addPlayer(callback.from_user.id, callback.from_user.full_name)


# process callback to vote to kill
@dp.callback_query_handler(lambda callback: callback.data == "kill")
async def kill(callback: types.CallbackQuery):
    victim_username = callback.message.text     # wrong, to fix
    print(victim_username)
    victim_username = "@" + victim_username
    victim_id = await main_game.getChatMemberIdByUsername(victim_username)
    main_game.votes[victim_id] += 1

    await bot.send_message(chat_id=callback.from_user.id,
                           text=f"Your vote to kill {victim_username} has been recorded.")


# command start
@dp.message_handler(commands=['start'])
async def info_about_game(message: types.Message):  # message.answer = написать в чат
    await message.answer("Hello!\nI am a host bot that allows you to play Mafia online in Telegram. To do this, "
                         "you just need to add a bot to the group and follow the instructions.")


# print rules of game
@dp.message_handler(commands=['rules'])
async def info_about_game(message: types.Message):
    await message.answer(
        '-- THE AIM OF THE GAME --\n\nThe aim of the game is different for the Mafia and Citizen players. '
        'Citizens will want to unmask the Mafia players. At the same time, the Mafia will want to '
        'stay hidden. The Mafia players will win if they equal the number of Citizens.\n\n-- ROLES IN THE GAME --\n\n'
        'THE MAFIA - These players determine who will be killed. They also know the identities of their teammates\n'
        'THE VILLAGERS - Also known as the “townspeople,” these players only know the number of Mafiosi in the game\n'
        'THE DETECTIVE – an Innocent who learns the team of one player every night\n'
        'THE DOCTOR – an Innocent may protect a player or him/herself from being killed each night'
        '\n\n-- THE NIGHT CYCLE --\n\nThe Mafia players should choose the citizen that they want to kill in '
        'bot private messages. After that, Doctor choose the citizen that they want to save. Afterwards,'
        ' The Detective choose the citizen that they want to check.\n\n-- THE DAY CYCLE --\n\nThe Bot opens '
        'the day cycle by announcing which Citizen was killed by the Mafia. Players can begin to debate '
        'what has happened. The killed player can’t participate. One player should leave each day. '
        'Once a character is eliminated they show their card to the remaining players.')


# create inline keyboard and announce about registration
@dp.message_handler(commands=['registration'])
async def registration(message: types.Message):
    registrationPlayers.clearListPlayers()
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        await message.answer("Recruitment for the game", reply_markup=registrationKeyBoard)
    else:
        print(message.chat.type)
        await message.answer("This command only for groups")


# start game
@dp.message_handler(commands=['start_game'])
async def start_game(message: types.Message):
    if message.chat.type == 'group' or message.chat.type == 'supergroup':  # this command only for chats
        print(registrationPlayers.getNumberPlayers())
        if registrationPlayers.getNumberPlayers() <= 0:  # check that players are enough for game
            await message.answer("There are too few of you! Minimum number of players is 4.")
        else:
            await message.answer("Game is start!\nEveryone got their roles in the private messages.")
            await main_game.setInfo(registrationPlayers.players, bot, message.chat.id)
            await main_game.start_game()
            await main_game.game()
    else:
        print(message.chat.type)
        await message.answer("This command only for groups")


@dp.message_handler(commands=['end_game'])
async def end_game(message: types.Message):
    registrationPlayers.clearListPlayers()  # Clear the list of players
    main_game.status_game = False
    await message.answer("The game has been ended. Thank you for playing!\n"
                         "You can start a new game by using the /start_game command.")


# start bot
if __name__ == '__main__':
    executor.start_polling(dp)
