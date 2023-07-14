from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import Roles
from Game import SignUpForTheGame, Game

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

referenceKeyBoard = InlineKeyboardMarkup(row_width=1)
reference = InlineKeyboardButton(text="Text to Bot", url="https://t.me/InnopolisMafiaBot")
referenceKeyBoard.add(reference)


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
@dp.callback_query_handler(text_startswith="mafia_kill_")
async def kill(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback_query_id=callback.id)
    victim_username = callback.data.replace("mafia_kill_", "")
    if len(main_game.getMafia().getMafiaList()) > 1:
        message = f"Player {callback.from_user.username} decided to kill {victim_username}"
        mafia_players = main_game.getMafia().getMafiaList()
        current_player = await main_game.getChatMemberByUsername(callback.from_user.username)
        current_player_id = current_player.getId()
        for player in mafia_players:
            if player.getId() != current_player_id:
                await main_game.getBot().send_message(chat_id=player.getId(), text=message)
    chosen_victim = await main_game.getChatMemberByUsername(victim_username)
    main_game.updateVotes(chosen_victim)
    main_game.updateVoteCount()
    await bot.send_message(chat_id=callback.from_user.id, text=f"Your vote to kill {victim_username} has been recorded")

    if main_game.getVoteCount() == len(main_game.getMafia().getMafiaList()):
        await main_game.confirmMove(Roles.Role.MAFIA)
        main_game.resetVoteCount()
        await main_game.getBot().send_message(chat_id=main_game.getChatId(), text="Mafia has made its choice")
        max_votes = max(main_game.getVotes().values())
        max_voted_players = [player.getName() for player, count in main_game.getVotes().items() if count == max_votes]
        if len(max_voted_players) > 1:
            await main_game.getBot().send_message(chat_id=main_game.getChatId(),
                                                  text="This night Mafia could not reach an agreement")
        else:
            victim = await main_game.getChatMemberByUsername(max_voted_players[0])
            await main_game.killPlayer(victim)
        main_game.resetVotes()
        if await main_game.checkNightMoves():
            await main_game.dayCycle()


@dp.callback_query_handler(text_startswith="doctor_heal_")
async def heal(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback_query_id=callback.id)
    await main_game.getBot().send_message(chat_id=main_game.getChatId(), text="Doctor went to the call")
    username = callback.data.replace("doctor_heal_", "")
    healed_player = await main_game.getChatMemberByUsername(username)
    await main_game.healPlayer(healed_player)
    await main_game.confirmMove(Roles.Role.DOCTOR)
    if await main_game.checkNightMoves():
        await main_game.dayCycle()


@dp.callback_query_handler(text_startswith="detective_check_")
async def check_role(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback_query_id=callback.id)
    await main_game.getBot().send_message(chat_id=main_game.getChatId(), text="The detective went to check")
    username = callback.data.replace("detective_check_", "")
    checked_player = await main_game.getChatMemberByUsername(username)
    await main_game.checkRoleOfPlayer(checked_player)
    await bot.send_message(chat_id=callback.from_user.id, text=f"The role of checked player {checked_player.getName()} "
                                                               f"is {checked_player.getRole().value}")
    await main_game.confirmMove(Roles.Role.DETECTIVE)
    if await main_game.checkNightMoves():
        await main_game.dayCycle()


# command start
@dp.message_handler(commands=['start'])
async def info_about_game(message: types.Message):  # message.answer = написать в чат
    await message.answer("Hello!\nI am a host bot that allows you to play Mafia online in Telegram. To do this, "
                         "you just need to add a bot to the group and follow the instructions.")


@dp.message_handler(commands=['start_voting'])
async def day_voting(message: types.Message):
    if await main_game.getChatMemberByUsername(message.from_user.username) not in main_game.getPlayers():
        await bot.delete_message(message.chat.id, message.message_id)
        await main_game.getBot().send_message(chat_id=message.from_user.id, text="You cannot use this command")
        return
    if main_game.time_of_day == "day":
        await main_game.getBot().send_message(chat_id=main_game.getChatId(), text="Use '/vote @username' to vote for "
                                                                                  "a player")
        votes = {player: 0 for player in main_game.getPlayers()}
        main_game.setVotes(votes)
    else:
        await message.answer("Voting can only be started during the day")


@dp.message_handler(commands=['vote'])
async def voting(message: types.Message):
    who_voted = await main_game.getChatMemberByUsername(message.from_user.username)
    if who_voted not in main_game.getPlayers():
        await bot.delete_message(message.chat.id, message.message_id)
        await main_game.getBot().send_message(chat_id=message.from_user.id, text="You cannot vote")
        return
    username = message.text.split('@')[1].strip()
    voted_player = await main_game.getChatMemberByUsername(username)
    if voted_player:
        if who_voted in main_game.getWhoVoted():
            await bot.delete_message(message.chat.id, message.message_id)
            await main_game.getBot().send_message(chat_id=message.from_user.id, text="You have already voted this day")
            return
        main_game.addVoter(who_voted)
        # Update the votes
        main_game.updateVotes(voted_player)
        main_game.updateVoteCount()
        await main_game.getBot().send_message(chat_id=message.from_user.id, text=f"You voted for {username}")

        # Get the current vote counts
        votes = main_game.getVotes()

        # Generate the vote summary
        vote_summary = "Votes:\n"
        for player, count in votes.items():
            if count != 0:
                vote_summary += f"{player.getName()}: {count}\n"

        # Send the vote summary message
        await main_game.getBot().send_message(chat_id=main_game.getChatId(), text=vote_summary)
    else:
        await main_game.getBot().send_message(chat_id=main_game.getChatId(), text="Player is not found")

    if main_game.getVoteCount() == len(main_game.getPlayers()):
        main_game.resetVoteCount()
        main_game.resetWhoVoted()
        max_votes = max(main_game.getVotes().values())
        max_voted_players = [player.getName() for player, count in main_game.getVotes().items() if count == max_votes]
        if len(max_voted_players) > 1:
            await main_game.getBot().send_message(chat_id=main_game.getChatId(),
                                                  text="No one was voted out during the day voting")
        else:
            await main_game.getBot().send_message(chat_id=main_game.getChatId(),
                                                  text=f"As a result of the vote, "
                                                       f"player {max_voted_players[0]} was voted out")
            voted_out_player = await main_game.getChatMemberByUsername(max_voted_players[0])
            if voted_out_player.getRole() == Roles.Mafia:
                await main_game.getMafia().showRemainingMafiaTeammates(main_game.getBot())
            await main_game.voteOut(voted_out_player)
        main_game.resetVotes()
        await main_game.nightCycle()


# print rules of game
@dp.message_handler(commands=['rules'])
async def info_about_game(message: types.Message):
    await message.answer('Before the game you need to write the command "/start" to the bot If you are playing for '
                         'the first time', reply_markup=referenceKeyBoard)
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
    registrationPlayers.dataReset()
    main_game.dataReset()
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        await message.answer("Recruitment for the game\n", reply_markup=registrationKeyBoard)
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
            registrationPlayers.dataReset()
            await main_game.start_game()
            await main_game.defineRoles()
            await main_game.nightCycle()
            await main_game.check_players()
    else:
        print(message.chat.type)
        await message.answer("This command only for groups")


@dp.message_handler(commands=['end_game'])
async def end_game(message: types.Message):
    registrationPlayers.dataReset()
    main_game.dataReset()
    main_game.status_game = False
    await message.answer("The game has been ended. Thank you for playing!\n"
                         "You can start a new registration by using the /registration command.")


@dp.message_handler()
async def prohibition_speech_night(message: types.Message):
    flag_not_player = False

    if main_game.time_of_day == "night":
        await bot.delete_message(message.chat.id, message.message_id)
        return

    for player in main_game.getKilledPlayers():
        if player.getId() == message.from_user.id:
            flag_not_player = True

    if flag_not_player:
        await bot.delete_message(message.chat.id, message.message_id)
        return

    for player in main_game.getKilledPlayers():
        if player.getId() == message.from_user.id:
            await bot.delete_message(message.chat.id, message.message_id)
            return


# start bot
if __name__ == '__main__':
    executor.start_polling(dp)
