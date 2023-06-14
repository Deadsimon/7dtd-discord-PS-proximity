import asyncio
import discord
import json
import requests
import timeit
import mysql.connector
import time
from discord.ext import commands
from variablestore import *
from PIL import Image

url = URL_endpoint_GPL
# Set the headers
headers = {
    'X-SDTD-API-TOKENNAME': token_name,
    'X-SDTD-API-SECRET': token_secret
}

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

biome_colors = {
    "forest": (0, 64, 0, 255),
    "desert": (255, 228, 119, 255),
    "irradiated": (255, 168, 0, 255),
    "snow": (255, 255, 255, 255)
}

biome_channels = biome_channels_vs


def check_if_player_in_home(x, z):
    home_x1 = home_x1_vs
    home_x2 = home_x2_vs
    home_z1 = home_z1_vs
    home_z2 = home_z2_vs

    if home_x1 <= x <= home_x2 and home_z1 <= z <= home_z2:
        return True
    else:
        return False


def get_biome_from_image(x, z):
    image = Image.open(map_path)  # Use the map_path variable from variablestore.py
    width, height = image.size
    map_x = int(width / 2) + x
    map_y = int(height / 2) - z
    pixel = image.getpixel((map_x, map_y))
    print("Pixel color:", pixel)  # Print the pixel color for troubleshooting
    for biome, color in biome_colors.items():
        if all(abs(pixel[i] - color[i]) <= 5 for i in range(3)):  # Compare each RGB component within a tolerance
            return biome
    return None


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host=mysql_config["host"],
        port=mysql_config["port"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"]
    )
    cursor = conn.cursor()

    # Fetch player mappings from the database
    cursor.execute("SELECT steam_id, discord_id FROM user_mapping")
    rows = cursor.fetchall()
    playerMapping = {int(row[0]): [] for row in rows}  # Initialize an empty list for each Steam ID
    print("Player Mapping:")
    for steam_id, discord_id in rows:
        playerMapping[int(steam_id)].append(int(discord_id))
        print(f"Steam ID: {steam_id} -> Discord ID: {discord_id}")

    while True:
        start_time = timeit.default_timer()  # Start measuring the time

        try:
            response = requests.get(url, headers=headers)

            # Check the response status code
            if response.status_code == 200:
                # Request successful
                response_data = response.json()

                # Extract player data
                players = response_data['data']['players']

                for player in players:
                    entityId = player['entityId']
                    name = player['name']
                    platformId = player['platformId']['platformId']
                    userId = player['platformId']['userId']
                    crossPlatformId = player['crossplatformId']['platformId']
                    crossUserId = player['crossplatformId']['userId']
                    totalPlayTimeSeconds = player['totalPlayTimeSeconds']
                    lastOnline = player['lastOnline']
                    online = player['online']
                    ip = player['ip']
                    ping = player['ping']
                    position = player['position']
                    position_x = position['x']
                    position_y = position['y']
                    position_z = position['z']
                    level = player['level']
                    health = player['health']
                    stamina = player['stamina']
                    score = player['score']
                    deaths = player['deaths']
                    zombieKills = player['kills']['zombies']
                    playerKills = player['kills']['players']
                    banned = player['banned']['banActive']
                    banReason = player['banned']['reason']
                    banUntil = player['banned']['until']


                discord_ids = playerMapping.get(steam_id)
                print("Discord IDs:", discord_ids)  # Added print statement

                timestamp = int(time.time())

                # Execute the SQL statements
                cursor.execute('''
                    SELECT timestamp
                    FROM player_movement
                    WHERE player_id = %s
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (name,))

                last_timestamp = cursor.fetchone()

                if last_timestamp is None or timestamp - last_timestamp[0] >= 10:
                    print(name)
                    print(timestamp)
                    print(position_x)
                    print(position_z)
                    try:
                        # Execute the SQL statement
                        cursor.execute('''
                            INSERT INTO player_movement (player_id, timestamp, x, z)
                            VALUES (%s, %s, %s, %s)
                        ''', (name, timestamp, position_x, position_z))
                        print((name, timestamp, position_x, position_z),
                              "Positional data inserted successfully.")
                    except mysql.connector.Error as error:
                        print("Error inserting positional data:", error)
                else:
                    print("Not enough time has passed since the last positional data.")
                    # Commit the changes
                    conn.commit()
                if discord_ids:
                    for discord_id in discord_ids:
                        guild = bot.get_guild(guild_id_vs)  # Replace guild_id with your actual guild ID
                        member = guild.get_member(discord_id)  # Changed get_member to get_user
                        print("Member:", member)  # Added print statement
                        if member:
                            if check_if_player_in_home(position_x, position_z):
                                home_channel_id = home_channel_id_vs
                                homechannel = bot.get_channel(home_channel_id)
                                print("Moving to home channel...")
                                print(f"{homechannel}")
                                await move_player_to_destination_channel(member, position_x, position_z,
                                                                         homechannel)
                            else:
                                biome = get_biome_from_image(position_x, position_z)
                                if biome:
                                    biome_channel_id = biome_channels.get(biome)
                                    biomeChannel = bot.get_channel(biome_channel_id)
                                    print(f"Moving to {biome} channel...")
                                    await move_player_to_destination_channel(member, position_x, position_z,
                                                                             biomeChannel)
                                else:
                                    print("Biome not found for player.")
                        else:
                            print(f"Discord member not found for Steam ID {userId}")
                else:
                    print(f"Discord ID not found for Steam ID {userId}")

        except requests.exceptions.RequestException as e:
            print("Error occurred during API request:", e)

        elapsed_time = timeit.default_timer() - start_time
        await asyncio.sleep(max(5 - elapsed_time, 0))

    # Close cursor and database connection
    cursor.close()
    conn.close()


async def move_player_to_destination_channel(member, position_x, position_z, destination_channel):
    guild = bot.get_guild(guild_id_vs)  # Replace guild_id with your actual guild ID

    x = position_x
    z = position_z
    print(x)
    print(z)
    if check_if_player_in_home(x, z):
        print("Player is inside the home area.")
        print("Moving to home channel...")
        await member.move_to(guild.get_channel(home_channel_id_vs))  # Move to home channel ID
    else:
        biome = get_biome_from_image(x, z)
        print("Biome:", biome)
        if biome:
            biome_channel_id = biome_channels.get(biome)
            if biome_channel_id:
                biome_channel = guild.get_channel(biome_channel_id)
                print(f"Moving to {biome} channel...")
                await member.move_to(biome_channel)  # Move to biome channel
            else:
                print("Biome channel ID not found.")
        else:
            print("Biome not found.")


bot.run(discordToken)  # Replace token with your actual bot token
