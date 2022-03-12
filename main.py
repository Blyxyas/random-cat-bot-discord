
from replit import db

import discord #upm package(py-cord)
from discord.ext import commands

import requests #upm package(requests)
from time import time

import os

# We load the environment variables

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
 
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

async def reply_breed(message, breed, id):
	# We reply with a random cat image
	cat = requests.get(f"https://api.thecatapi.com/v1/images/search?breed_ids={ids[breeds.index(breed)]}").json()[0]['url']

	embed = discord.Embed(title="**Cat fan detected!**", description=f"You was talking about a ***{breed}***, right?", color=COLOR)
	embed.set_image(url=cat)
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
		self.last_time = time()

	def reset_cats(self):
		self.cat_counter += 1
		self.last_time = time()


keywords: list = ["cat", "kitty", "kitten", "kittycat", "kittens", "kittycats", "kitties"]

# We collect the breeds of all the cats
url = "https://api.thecatapi.com/v1/breeds"
file = requests.get(url, allow_redirects=True).json()

breeds: list = []
ids: list = []

for each in file:
	breeds.append(each['name'].lower())
	ids.append(each['id'])

# ─── COMMANDS ───────────────────────────────────────────────────────────────────

@bot.command()
async def ping(ctx):
	await ctx.send("Yes, I'm conected to the server")

@bot.command()
async def cat(ctx):
	await reply(ctx)

# ─── EVENTS ─────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
	for key in db.keys():
		db.pop(key)
	print("Bot is ready")

from typing import List

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	if message.content.startswith(DEFAULT_PREFIX):
		bot.process_commands(message)

	serverid = str(message.guild.id)
	authid = str(message.author.id)
	currenttime = int(time())
	if serverid not in db:
		# We add the server to the database
		db[serverid] = [currenttime, {}]

	if authid not in db[serverid][1]:
		# We add the user to the database
		db[serverid][1][authid] = [message.guild.id, 1, int(time())]
	
	# We check if the user is talking about a cat
	if any(x in message.content.lower() for x in ["cat", "kitty", "kitten", "kittycat", "kittens", "kittycats", "kitties"]):
		user = db[serverid][1][authid]
		new_cat_counter = 0
		for keyw in ["cat", "kitty", "kitten", "kittycat", "kittens", "kittycats", "kitties"]:
			if keyw in message.content.lower():
				new_cat_counter += message.content.lower().count(keyw)
		
		if currenttime - user[2] > 60:
			user[1] = 0
	# Now we update the user
		user[1] += new_cat_counter
		user[2] = currenttime
		
		if user[1] >= 3:
			await reply(message)
			user[1] = 0

bot.run(DISCORD_TOKEN)
