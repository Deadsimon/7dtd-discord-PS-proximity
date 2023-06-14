# 7daystodie-Bot-PS-proximity

Description:

Discord bot for pseudo proximity chat. moves players to different discord voice channels depending on location.
if they are in the defined home area, they are moved to the home discord voice channel.
if they are outside the home it compares the players to the biomes.png and returns which biome the player is in, and then moves them to the appropriate channel (E.G Forest - Forest voice channel)
See the Setup wiki for more details

Features

Player location tracking & history
home Area detection and Home Voice channel.
Biome detection and Biome voice channels
Configurable variables to customise it to your setup
currently setup for 5 Discord channels

Requirements:

allocs server fixes with web token and permissions setup
Mysql with the appropriate setup (check wiki)
7 days server
Discord bot with bot token

optional:
steam-discord id mapper - https://github.com/Deadsimon/steam-discordmapper

# Compatibitiy

https://github.com/Deadsimon/7dtd-disord-PS-proximity/wiki/Compatability

# To DO list:

Health warning - Bot plays a health warning for the user in the users voice channel

Movement warnings - bot sends a message to the admin discord text channel E.g : PLAYERNAME moved faster then achievable, Moved VALUE (MAX value)

add a Warnings table to the database.

add check to see how many movement warnings a player has had in a 24hrs - kick player if over 3 in 24hrs, otherwise send admin message "Potential Cheater: USERID, Please review the server logs."

Add ignore list for movement warnings(default: Admin ids) (will be stored in the variablestore)

add image output for RWG games with the historic Map 
