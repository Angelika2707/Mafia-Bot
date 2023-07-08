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
    await bot.answer_callback_query(callback_query_id=callback.id)
    print(callback.from_user.id)
    if registrationPlayers.checkPlayerInGame(callback.from_user.id):
        await bot.send_message(chat_id=callback.from_user.id, text="You are already in the game!")
    else:
        await bot.send_message(chat_id=callback.from_user.id, text="You are in the game!")
        registrationPlayers.addPlayer(callback.from_user.id, callback.from_user.username)


# process callback to vote to kill
@dp.callback_query_handler()
async def kill(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback_query_id=callback.id)
    for player in main_game.list_players:
        if player.getName() == callback.data:
            victim_username = callback.data
            victim = await main_game.getChatMemberByUsername(victim_username)
            main_game.updateVotes(victim)
            main_game.updateVoteCount()
            await bot.send_message(chat_id=callback.from_user.id,
                                   text=f"Your vote to kill {victim_username} has been recorded")

    if main_game.getVoteCount() == len(main_game.getMafia().getMafiaList()):
        main_game.resetVoteCount()
        victim = max(main_game.getVotes(), key=main_game.getVotes().get)
        await main_game.getBot().send_message(chat_id=main_game.getChatId(), text="Mafia has made its choice")
        main_game.killPlayer(victim)
        main_game.resetVotes()
        await main_game.dayCycle()


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
            await main_game.defineRoles()
            await main_game.nightCycle()
    else:
        print(message.chat.type)
        await message.answer("This command only for groups")


@dp.message_handler(commands=['end_game'])
async def end_game(message: types.Message):
    registrationPlayers.clearListPlayers()  # Clear the list of players
    main_game.status_game = False
    await message.answer("The game has been ended. Thank you for playing!\n"
                         "You can start a new game by using the /start_game command.")


@dp.message_handler()
async def prohibition_speech_night(message: types.Message):
    if main_game.time_of_day == "night":
        await bot.delete_message(message.chat.id, message.message_id)
        return
    print("bbb")
    for player in main_game.getKilledPlayers():
        if player.getId() == message.from_user.id:
            await bot.delete_message(message.chat.id, message.message_id)
            return


# start bot
if __name__ == '__main__':
    executor.start_polling(dp)
