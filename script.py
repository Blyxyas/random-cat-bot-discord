
# Database stuff

import sqlite3 as sq
import time

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
	cur.execute("SELECT userid, cat_counter, last_time FROM users WHERE userid = ?, guild_id = ?", (userid, serverguild))

	return cur.fetchone()

@commit
def more_cats(serverguild, cat_counter, userid):
	# We select the guild from the database
	cur.execute("UPDATE users SET cat_counter = ?, last_time = ? WHERE userid = ?, guild_id = ?", (cat_counter, time.time(), userid, serverguild))

@commit
def reset_cats(serverguild, userid):
	# We select the guild from the database
	cur.execute("UPDATE users SET cat_counter = 0 WHERE userid = ?, guild_id = ?", (userid, serverguild))

from discord.ext import commands
from dotenv import load_dotenv
import os

# We load the .env file
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
	await ctx.send()

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
		await bot.process_commands(message)
	else:
		# We fetch the user from the database
		user = fetch(message.guild.id, message.author.id)
		if user is None:
			cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (message.guild.id, message.author.id, 0, time.time()))
			cnx.commit()
		user = fetch(message.guild.id, message.author.id)
		cat_counter = user[2]
		for keyw in ["cat", "kitty", "kitten", "kittycat", "kittens", "kittycats", "kitties"]:
			if keyw in message.content.lower():
				cat_counter += message.content.lower().count(keyw)
				more_cats(message.guild.id, cat_counter, message.author.id)
				print(cat_counter)
				if cat_counter >= 3:
					reset_cats(message.guild.id, message.author.id)
					await message.channel.send("{} you have {} cats (reset)".format(message.author.mention, cat_counter))
				break

bot.run(DISCORD_TOKEN)