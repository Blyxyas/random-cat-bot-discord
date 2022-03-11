
# Database stuff

import sqlite3 as sq
import time

COLOR = 0xe36e00

# We connect to the database
con =sq.connect("dtb.db", check_same_thread=False)
# We create a cursor
cur = con.cursor()

with open("build.sql", "r", encoding="utf-8") as script:
	# We read the .sql file and execute it
	con.executescript(script.read())
	con.commit()

import discord

def commit(func):
	def inner(*args, **kwargs):
		func(*args, **kwargs)
		con.commit()
	return inner

def fetch(serverguild, userid):
	# We select the guild from the database
	# We fetch the result
	cur.execute("SELECT userid, cat_counter, last_time FROM users WHERE userid = ? AND guild_id = ?", (userid, serverguild))

	return cur.fetchone()

@commit
def more_cats(serverguild, cat_counter, userid):
	# We select the guild from the database
	cur.execute("UPDATE users SET cat_counter = ?, last_time = ? WHERE userid = ? AND guild_id = ?", (cat_counter, time.time(), userid, serverguild))

@commit
def reset_cats(serverguild, userid):
	# We select the guild from the database
	cur.execute("UPDATE users SET cat_counter = 0 WHERE userid = ? AND guild_id = ?", (userid, serverguild))

from discord.ext import commands
import requests
import os

async def reply(message):
	# We reply with a random cat image
	cat = requests.get(f'https://api.thecatapi.com/v1/images/search?api_key=c1404cc3-7fae-4c6e-8cb0-4d14303ae6d1').json()[0]

	if len(cat['breeds']) == 0:
		embed = discord.Embed(title="**Cat fan detected!**", description="Take this with you", color=COLOR)
		embed.set_image(url=cat['url'])
		await message.channel.send(embed=embed)
	else:
		embed = discord.Embed(title="**Cat fan detected!**", description="Take this with you", color=COLOR)
		embed.add_field(name="Breed", value=cat['breeds'][0]['name'], inline=False)
		embed.set_image(url=cat['url'])
		await message.channel.send(embed=embed)

# We load the .env file
from dotenv import load_dotenv
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
 
DEFAULT_PREFIX = ">"

bot = discord.Client()
bot = commands.Bot(command_prefix=DEFAULT_PREFIX)

@bot.command()
async def ping(ctx):
	await ctx.send("Yes, I'm conected to the server")

@bot.command()
async def cat(ctx):
	await reply(ctx)

@bot.event
async def on_ready():
	print("Bot is ready")

@bot.command()
@commands.has_permissions(administrator=True)
async def db(ctx):
	cur.execute("SELECT * FROM servers WHERE guild_id = ?", (ctx.guild.id, ))
	if cur.fetchone() is None:
		cur.execute("INSERT INTO servers VALUES (?, ?)", (ctx.guild.id, ))
		con.commit()
		await ctx.send("The server has been added to the database") 
	await ctx.send("Database is ready")

@bot.event
async def on_message(message):
	cnx = sq.connect('dtb.db')
	cursor = cnx.cursor()
	if message.author == bot.user:
		return
	if message.content.startswith(DEFAULT_PREFIX):
		# We process the command
		await bot.process_commands(message)
	else:
		# We fetch the user from the database
		user = fetch(message.guild.id, message.author.id)
		if user is None:
			cursor.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)", (message.guild.id, message.author.id, 0, time.time()))
			cnx.commit()
		user = fetch(message.guild.id, message.author.id)
		cat_counter = user[1]
		last_time = user[2]

		print(cat_counter)
		if last_time - time.time() < -60:
			cat_counter = 0
			print("cat counter reiniciado")

		for keyw in ["cat", "kitty", "kitten", "kittycat", "kittens", "kittycats", "kitties"]:
			if keyw in message.content.lower():
				cat_counter += message.content.lower().count(keyw)
				more_cats(message.guild.id, cat_counter, message.author.id)
				if cat_counter >= 3:
					reset_cats(message.guild.id, message.author.id)
					
					await reply(message)
		cnx.close()

bot.run(DISCORD_TOKEN)