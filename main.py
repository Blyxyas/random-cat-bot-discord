
from replit import db

import discord
from discord.ext import commands

import requests
from time import time 

from keep_alive import keep_alive

import os

# We load the environment variables

 
DEFAULT_PREFIX = ">"

async def determine_prefix(bot, message):
	guild = str(message.guild.id)
	if guild in db:
		return db[guild][2]
	return DEFAULT_PREFIX

bot = commands.Bot(command_prefix = determine_prefix, help_command=None)

COLOR = 0xe36e00

# ─── UTILS ──────────────────────────────────────────────────────────────────────

url = "https://api.thecatapi.com/v1/breeds"
file = requests.get(url, allow_redirects=True).json()

breeds: list = []
ids: list = []

for each in file:
	breeds.append(each['name'].lower())
	ids.append(each['id'])

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

async def reply_breed(message, breed):
	# We reply with a random cat image
	cat = requests.get(f"https://api.thecatapi.com/v1/images/search?breed_ids={ids[breeds.index(breed)]}").json()[0]['url']

	embed = discord.Embed(title="**Cat fan detected!**", description=f"You was talking about a ***{breed}***, right?", color=COLOR)
	embed.set_image(url=cat)
	await message.channel.send(embed=embed)


# ─── DATABASE ───────────────────────────────────────────────────────────────────

keywords: list = ["cat", "kitty", "kitten", "kittycat", "kittens", "kittycats", "kitties"]

# We collect the breeds of all the cats

# ─── COMMANDS ───────────────────────────────────────────────────────────────────

@bot.command()
async def ping(ctx):
	await ctx.send("Yes, I'm conected to the server")

@bot.command()
async def cat(ctx, breed = None):
	if breed is None:
		await reply(ctx)
	else:
		await reply_breed(ctx, breed)

# ─── ADMIN COMMANDS ─────────────────────────────────────────────────────────────


@bot.command()
async def setprefix(ctx, new_prefix = None):
	#You'd obviously need to do some error checking here
	#All I'm doing here is if prefixes is not passed then
	#set it to default 
	if new_prefix is None:
		await ctx.send("Please enter a prefix")
		return
	db[str(ctx.guild.id)][2] = new_prefix
	await ctx.send("Prefix set!")

@bot.command()
async def settolerance(ctx, new_tolerance = None):
	if new_tolerance is None:
		await ctx.send("Please enter a tolerance")
		return
	if type(new_tolerance) is not int:
		await ctx.send("Please enter a number.")
		return

	db[str(ctx.guild.id)][3] = new_tolerance
	await ctx.send("Tolerance set!")

@bot.command()
async def config(ctx):
	embed = discord.Embed(title="**Configuration**", description="Here are the current settings", color=COLOR)

	embed.add_field(name="Prefix", value=f"**{db[str(ctx.guild.id)][2]}**, the prefix needed to use the commands. **Default: `\">\"`**, use `{db[str(ctx.guild.id)][2]}setprefix NEW PREFIX` to change the prefix", inline=False)
	
	embed.add_field(name="Tolerance", value=f"Current: **{db[str(ctx.guild.id)][3]}**, The amount of times a user must mention \"cat words\" ('cat', 'kitty', etc...) to send a cat picture. **Default: *3***, use `{db[str(ctx.guild.id)][2]}settolerance NEW TOLERANCE` to change the tolerance", inline=False)

	await ctx.channel.send(embed=embed)

@bot.command()
async def help(ctx):
	embed = discord.Embed(title="**Help**")
	embed.add_field(name="**`cat`**", value="Get a random cat image, you can use `cat [breed]` to request for a specific breed.", inline=False)
	embed.add_field(name="**`help`", value="Get this message", inline=False)
	# if the user is an admin
	if ctx.author.guild_permissions.administrator:
		embed.add_field(name="**`ping` (Admin)**", value="Check if the bot is online", inline=False)
		embed.add_field(name="**`config` (Admin)**", value="Change the settings for the bot", inline=False)

	# Now we reply
	await ctx.message.reply(embed=embed)

# ─── EVENTS ─────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
	print(breeds)
	for key in db.keys():
		db.pop(key)
	print("Bot is ready")

@bot.event
async def on_message(message):
	serverid = str(message.guild.id)
	authid = str(message.author.id)
	currenttime = int(time())
	
	if serverid not in db:
		# We add the server to the database
		db[serverid] = [currenttime, {}, ">", 3]
	else:
		if currenttime - db[serverid][0] > 3600:
			del db[serverid]
	
	if message.author == bot.user:
		return

	if message.content.startswith(db[serverid][2]):
		await bot.process_commands(message)

	if authid not in db[serverid][1]:
		# We add the user to the database
		db[serverid][1][authid] = [message.guild.id, 1, int(time())]
	user = db[serverid][1][authid]
	
	# We check if the user is talking about a cat
	if any(x in message.content.lower() for x in ["cat", "kitty", "kitten", "kittycat", "kittens", "kittycats", "kitties"]):
		new_cat_counter = 0
		for keyw in ["cat", "kitty", "kitten", "kittycat", "kittens", "kittycats", "kitties"]:
			if keyw in message.content.lower():
				new_cat_counter += message.content.lower().count(keyw)

		if currenttime - user[2] >= 30:
			user[1] = 0
	# Now we update the user
		user[1] += new_cat_counter
		user[2] = currenttime
		print(user[1])

	if user[1] >= db[serverid][3] or (any(x in message.content.lower() for x in breeds) and user[1] >= 1):
		if user[1] >= db[serverid][3]:
			await reply(message)
		else:
			for breed in breeds:
				if breed in message.content.lower():
					await reply_breed(message, breed)
			
		user[1] = 0

@bot.event
async def on_command_errro(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		await ctx.send("Command not found")
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Missing argument")

keep_alive()
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
bot.run(DISCORD_TOKEN)
