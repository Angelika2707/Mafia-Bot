# Inno Mafia Bot
This repository contains a source code for a [@InnopolisMafiaBot](https://t.me/InnopolisMafiaBot) Telegram bot.
Inno Mafia Bot can conduct collective mafia games in groups and supergroups.


# How to use
Add [@InnopolisMafiaBot](https://t.me/InnopolisMafiaBot) to your group or supergroup and give it permission to delete messages. 


# Available commands
* ```/rules``` - print the rules of the mafia game and send a keyboard with a button that starts the bot (for those who play for the first time)
* ```/register``` - create a request for registration in a mafia game
* ```/start_game``` - start a game from existing request
* ```/start_voting``` - start daytime voting process
* ```/vote``` - vote for another player during daytime voting process (sample of usage: /vote @username)
* ```/end_game``` - forcefully ends the mafia game

# Game Rules
The Inno Mafia Bot follows the traditional rules of the mafia game, with slight modifications to accommodate the group dynamics on Telegram. Here are the basic rules:
1. **Objective**: The objective of the game is to identify and eliminate the Mafia members if you are an innocent player, or to deceive and eliminate the innocent players if you are a Mafia member.
2. **Roles**: Each player is assigned a role, which is kept secret from other players. The available roles include Citizen, Mafia, Detective, and Doctor.
3. **Discussion**: During the daytime, players engage in discussions to share their suspicions, observations, and opinions. Players can use this time to convince others of their innocence or identify suspicious behavior.
4. **Voting**: At the end of the day, players vote for the player they suspect to be a Mafia member. The player with the highest number of votes is eliminated.
5. **Night Actions**: At night, specific roles, such as the Mafia, Detective, and Doctor, can perform their respective night actions. The Mafia chooses a player to eliminate, the Detective investigates the role of another player, and the Doctor can protect a player from being eliminated.
6. **Game Progression**: The game progresses with alternating day and night cycles. Players continue to discuss, vote, and perform night actions until one team achieves victory.
7. **Win Conditions**: The game concludes when one of the following conditions is met:
   
      * The Mafia members outnumber the remaining players, or both are equal in number, resulting in a Mafia victory.
      * All Mafia members are eliminated, leading to a victory for the innocent players.
