from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Game import SignUpForTheGame, Game

TOKEN = '5990396163:AAGOgKqVWSHStXo0CaD-kkD8lCxXdtCnmfY'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

registrationPlayers = SignUpForTheGame()

registrationKeyBoard = InlineKeyboardMarkup(row_width=1)
registration = InlineKeyboardButton(text="Register", callback_data="register")
registrationKeyBoard.add(registration)


@dp.callback_query_handler()
async def register(callback: types.CallbackQuery):
    if callback.data == 'register':
        if registrationPlayers.checkPlayerInGame(callback.from_user.id):
            await bot.send_message(chat_id=callback.from_user.id, text="You are already in the game!")
        else:
            await bot.send_message(chat_id=callback.from_user.id, text="You are in the game!")
            registrationPlayers.addPlayer(callback.from_user.id)


# обработка команды /start
@dp.message_handler(commands=['start'])
async def info_about_game(message: types.Message):  # message.answer = написать в чат
    await message.answer("Hello!\nI am a host bot that allows you to play Mafia online in Telegram. To do this, "
                         "you just need to add a bot to the group and follow the instructions.")


# вывод правил игры
@dp.message_handler(commands=['rules'])
async def info_about_game(message: types.Message):  # печатую правила игры
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


@dp.message_handler(commands=['registration'])
async def registration(message: types.Message):
    registrationPlayers.clearListPlayers()
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        await message.answer("Recruitment for the game", reply_markup=registrationKeyBoard)
    else:
        print(message.chat.type)
        await message.answer("This command only for groups")


@dp.message_handler(commands=['start_game'])
async def start_game(message: types.Message):
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        if registrationPlayers.getNumberPlayers() < 0:
            await message.answer("There are too few of you! Minimum number of players is 4.")
        else:
            await message.answer("Game is start!\nEveryone got their roles in the private messages.")
            main_game = Game(registrationPlayers.players, bot)
            await main_game.game()
    else:
        print(message.chat.type)
        await message.answer("This command only for groups")


# запуск бота
if __name__ == '__main__':
    executor.start_polling(dp)
