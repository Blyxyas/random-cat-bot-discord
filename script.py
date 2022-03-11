
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

class User:
	def __init__(self, userid, cat_counter, message):
		self.userid = userid
		self.cat_counter = cat_counter
		self.message = message
	
	def fetch(self):
		# We select the guild from the database
		cur.execute("SELECT * FROM servers WHERE serverid = ?", self.message.guild.id)

		# We fetch the result
		cur.execute("SELECT userid, cat_counter FROM users WHERE userid = ?", self.userid)

		return cur.fetchone()
	
	@commit
	def more_cats(self):
		cur.execute("UPDATE users SET cat_counter = ?, last_time = ? WHERE userid = ?", (self.cat_counter + 1, time.time(), self.userid))

	@commit
	def reset_cats(self):
		cur.execute("UPDATE users SET cat_counter = 0 WHERE userid = ?", self.userid)
















from discord.ext import commands
from dotenv import load_dotenv

# We load the .env file
load_dotenv()

DISCORD_TOKEN = "ODYxMjY3NDAxODE4NjM2Mjg4.YOHTxg.zdXRL30a7T8xoDo2gHWw1kFskIM"
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

@bot.event
async def on_message(message):
	cnx = sq.connect('dtb.db')
	cursor = cnx.cursor()
	if message.content.startswith(DEFAULT_PREFIX):
		await bot.process_commands(message)
	else:
		# We analyze the message
		# We see how many times the user mentions `cat` and things

		for keyw in ["cat", "kitty", "kitten", "kittycat", "kittens", "kittycats", "kitties"]:
			if keyw in message.content.lower():
				cat_counter += message.content.lower().count(keyw)

		# We get the userid
		user = User(message.author.id, cat_counter. message.guild.id)

		# We update the counter
		user.more_cats()
		cnx.commit()

		# We get all the data
		if user.fetch() is None:
			# We create the user
			cur.execute("INSERT INTO users VALUES (?, ?, ?)", (user.userid, user.cat_counter, time.time()))
		else:
			# We update the user
			if user.cat_counter >= 2:
				# We reset the counter
				user.reset_cats()
				# We send the message
				await message.channel.send(f"{message.author.mention} you have {user.cat_counter} cat(s)")
		cursor.close()
		cnx.close()
			# image = requests.get("https://api.thecatapi.com/v1/images/search?api_key=c1404cc3-7fae-4c6e-8cb0-4d14303ae6d1").json()[0].get("url")
			# embedded = discord.Embed(title="Cat fan detected", description="You can't ask for a cat too much, you know.", color=0xd47b00)
			# embedded.set_image(url=image)
			# await message.channel.send(embed=embedded)

bot.run(DISCORD_TOKEN)