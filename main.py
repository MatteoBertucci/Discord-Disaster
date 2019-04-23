##### WEB SERVER #####
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot running"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():  
    t = Thread(target=run)
    t.start()



##### BOT #####
import discord
import os
import json
import time
#import pickle
import _thread
import asyncio
import xml.etree.ElementTree as ET

client = discord.Client()

class Connection:
	def checkTimeout(self):
		if self.timeout < int(time.time()):
			return True
		else:
			return False
	
	def __init__(self,message):
		self.client = message.author
		self.server = message.server
		self.channel = message.channel
		self.timeout = int(time.time()) + 30
		self.message = None

def getJsonData(jsonPath):
	with open(jsonPath) as jsonFile:
		data = json.load(jsonFile)
		return(data)

def saveJson(jsonPath,data):
	with open(jsonPath,"w") as outfile:
		json.dump(data,outfile)

def getElement(id, client):
	lang_data = getJsonData("data/lang.txt")
	lang = lang_data[str(client.id)]
	if lang == 1:
		xmlRoot = rootFR
	elif lang == 2:
		xmlRoot = rootEN
	else:
		raise valueEroor("Unknow lang value")
	text = xmlRoot[id][0].attrib["text"] + client.mention + xmlRoot[id][1].attrib["text"]+ "\n:one: " + xmlRoot[id][2].attrib["text"]
	question = 1
	if xmlRoot[id][3].attrib["text"] != "":
		text = text + "\n:two: " + xmlRoot[id][3].attrib["text"]
		question = 2
	if xmlRoot[id][4].attrib["text"] != "":
		text = text + "\n:three: " + xmlRoot[id][4].attrib["text"]
		question = 3
	return (text, question)

def follow(connection,react):
	save_data = getJsonData("data/save.txt")
	id = save_data[str(connection.client.id)]
	lang_data = getJsonData("data/lang.txt")
	lang = lang_data[str(connection.client.id)]
	if lang == 1:
		xmlRoot = rootFR
	elif lang == 2:
		xmlRoot = rootEN
	else:
		raise valueEroor("Unknow lang value")
	if react == "1\u20e3":
		waitTime = int(xmlRoot[id][2][0].attrib["time"])
		nextId = int(xmlRoot[id][2][1].attrib["id"])
		EventId = int(xmlRoot[id][2][2].attrib["id"])
	elif react == "2\u20e3":
		waitTime = int(xmlRoot[id][3][0].attrib["time"])
		nextId = int(xmlRoot[id][3][1].attrib["id"])
		EventId = int(xmlRoot[id][3][2].attrib["id"])
	elif react == "3\u20e3":
		waitTime = int(xmlRoot[id][4][0].attrib["time"])
		nextId = int(xmlRoot[id][4][1].attrib["id"])
		EventId = int(xmlRoot[id][4][2].attrib["id"])
	return (waitTime, nextId, EventId)


async def sendHelloMessage(fromMessage):
	print("Creating save...")
	save_data = getJsonData("data/save.txt")
	save_data[str(fromMessage.author.id)] = 1
	messageSend = await client.send_message(fromMessage.channel, fromMessage.author.mention + ' Welcome to **Discord Nightmare**\n*Please select your language*')
	await client.add_reaction(messageSend, "🇬🇧")
	await client.add_reaction(messageSend, "🇫🇷")
	print("Waiting for user lang selection...")
	reactLang = await client.wait_for_reaction(message = messageSend, user = fromMessage.author, emoji = ["🇬🇧","🇫🇷"])
	lang_data = getJsonData("data/lang.txt")
	if reactLang.reaction.emoji == "🇫🇷":
		print("French selected !")
		lang_data[str(fromMessage.author.id)] = 1
	elif reactLang.reaction.emoji == "🇬🇧":
		print("English selected !")
		lang_data[str(fromMessage.author.id)] = 2
	saveJson("data/lang.txt",lang_data)
	saveJson("data/save.txt",save_data)
	client.delete_message(messageSend)
	print("")
	await openConnection(fromMessage)

async def openConnection(fromMessage):
	print("Opening Session...")
	connection = Connection(fromMessage)
	#connects[str(fromMessage.author.id)] = newConnection
	while True:
		save_data =  getJsonData("data/save.txt")
		#msgText = getElement(save_data[str(fromMessage.author.id)],connection.client)
		text = getElement(save_data[str(connection.client.id)],connection.client)
		connection.message = await client.send_message(connection.channel, text[0])
		print("Message send !\nWaiting for user reaction...")
		await client.add_reaction(connection.message, "1\u20e3")
		if text[1] >= 2:
			await client.add_reaction(connection.message, "2\u20e3")
		if text[1] == 3:
			await client.add_reaction(connection.message, "3\u20e3")
		react = await client.wait_for_reaction(emoji = ["1\u20e3","2\u20e3","3\u20e3"], user = connection.client, timeout = 180 ,message = connection.message)
		if react == None:
			print("Timeout !")
			await client.delete_message(connection.message)
			return
		followQuestion = follow(connection, react.reaction.emoji)
		save_data[str(connection.client.id)] = followQuestion[1]
		saveJson("data/save.txt",save_data)
		await client.delete_message(connection.message)
		asyncio.wait(followQuestion[0])

async def loadGame(fromMessage):
	print("Loading save of player : [%s / %s]" % (fromMessage.author, fromMessage.author.id))
	save_data = getJsonData("data/save.txt")
	try:
		save_data[str(fromMessage.author.id)]
	except KeyError:
		print("Save not found !")
		await sendHelloMessage(fromMessage)
	else:
		await openConnection(fromMessage)

@client.event
async def on_ready():
		print("")
		print("")
		print("")
		print("Current time : %s" % int(time.time()))
		print("")
		print("===================================================================")
		print("Bot started with id : [%s / %s]" % (client.user, client.user.id))
		print("===================================================================")
		print("")
#		recoverLastSession()

@client.event
async def on_message(message):
    if message.author != client.user:
      if message.content == "Vigli le Bof":
        await client.send_message(message.channel, "This Is Not An Easter Egg")
      #await client.send_message(message.channel, message.content[::-1])
      if message.content == "Ok":
      	await loadGame(message)

#def tick():
#	time.sleep(5)
#	while True:
#		#print("tick")
#		time.sleep(20)
#		with connectKey:
#			global connects
#			d = 0
#			for i in connects:
#				if connects[i].checkTimeout():
#					closeConnection(connects[i])
#					d = d + 1
#			if d > 0:
#				print("%s connections closed !" % (d))

#_thread.start_new_thread(tick, ())
#connectKey = _thread.allocate_lock()
treeFR = ET.parse('lang/fr.xml')
rootFR = treeFR.getroot()
treeEN = ET.parse('lang/en.xml')
rootEN = treeEN.getroot()
_thread.start_new_thread(keep_alive,())
token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)
