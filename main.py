
from replit import db

from discord.ext import commands
import discord

import requests
import time

from dotenv import load_dotenv
import os

# We load the environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
 
DEFAULT_PREFIX = ">"

bot = discord.Client()
bot = commands.Bot(command_prefix=DEFAULT_PREFIX)

COLOR = 0xe36e00

# ─── UTILS ──────────────────────────────────────────────────────────────────────

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


# ─── DATABASE ───────────────────────────────────────────────────────────────────

from dataclasses import dataclass

@dataclass
class user:
	guild_id: int
	user_id: int
	cat_counter: int
	last_time: int

	def more_cats(self, new_cats):
		self.cat_counter += new_cats
		self.last_time = time.time()

	def reset_cats(self):
		self.cat_counter += 1
		self.last_time = time.time()

# ─── COMMANDS ───────────────────────────────────────────────────────────────────

@bot.command()
async def ping(ctx):
	await ctx.send("Yes, I'm conected to the server")

@bot.command()
async def cat(ctx):
	await reply(ctx)

# Setup de database
@bot.command
async def setup(ctx):
	if ctx.guild.id in db:
		await ctx.send("The server is already in the database")
	else:
		db[ctx.guild.id] = []
		await ctx.send("The server has been added to the database")

# ─── EVENTS ─────────────────────────────────────────────────────────────────────

from typing import List

@bot.event
async def on_ready():
	# db = {
	# 	"serverid": [list of users]
	# }
	print("Bot is ready")

@bot.event
async def on_message(message):
	# We check if the user is registered
	if message.author.id not in db[message.guild.id]:
		# We register the user
		db[message.guild.id].append(user(message.guild.id, message.author.id, 0, time.time()))
		print(f"{message.author.name} has been registered")
	else:
		if any(x in message.content.lower() for x in ["cat", "kitty", "kitten", "kittycat", "kittens", "kittycats", "kitties"]):
			for keyw in ["cat", "kitty", "kitten", "kittycat", "kittens", "kittycats", "kitties"]:
				if keyw in message.content.lower():
					cat_counter += message.content.lower().count(keyw)
			# Now we update the user
			db[message.guild.id][message.author.id].more_cats(cat_counter)

		if time.time() - db[message.guild.id][message.author.id].last_time > 60:

			db[message.guild.id][message.author.id].reset_cats()
		
		else:
			if db[message.guild.id][message.author.id].cat_counter >= 3:
				await reply(message)
				db[message.guild.id][message.author.id].reset_cats()

bot.run(DISCORD_TOKEN)
