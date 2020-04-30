#! /usr/bin/python3

import asyncio, sys, re, os, shutil, random
from nio import AsyncClient, RoomMessageText, RoomMessageImage, responses
from stuff import *
from facezooming import do_facezoom


if not os.path.isfile("config.txt"):
	print("please specify domain, username and password in config.txt")
	exit()

config = open("config.txt", "r").readlines()

#[:-1] = remove newline
domain = config[0][:-1]
username = config[1][:-1]
password = config[2][:-1]

#todo
wapp_mode = True
client = None
save_folder = "temp"

if(os.path.isdir(save_folder)):
	shutil.rmtree(save_folder)
	
os.makedirs(save_folder)

async def text_msg_callback(room, event):
	print("=========")

	print(
		"Message received for room {} | {}: {}".format(
			room.display_name, room.user_name(event.sender), event.body
		)
	)

async def image_msg_callback(room, event):
	print("=========")
	print("received img from "+event.sender+":\n"+event.url+'\n'+event.body)

	#get server name and media id from event.url
	server_name = re.match(r"mxc://([\w|\.]+)/", event.url).groups()[0]
	media_id = re.match(r"mxc://[\w|\.]+/(\w+)", event.url).groups()[0]
	print("server_name: "+server_name)
	print("media_id: "+media_id)

	image_path = await download_image(client, server_name, media_id, save_folder)
	if image_path is None:
		return	

	#facezoom
	zoom_success = do_facezoom(image_path)

	if zoom_success:
		if wapp_mode:
			#random delay to maybe avoid bot detection by Whatsapp
			await asyncio.sleep(random.uniform(0.5, 1.5))

		uploaded_mxc = await upload_image(client, image_path)
		if uploaded_mxc is None:
			print("failed to upload")
		else:
			#send
			await client.room_send(
				room_id=room.room_id,
				message_type="m.room.message",
				content={
					"msgtype": "m.image",
					"body": "zoomed image",
					"url": uploaded_mxc
				}
			)

	#delete file
	os.remove(image_path)


async def main():
	global client

	client = AsyncClient("https://"+domain, user=username)
	await client.login(password)
	#sync to clear old messages
	await client.sync()

	client.add_event_callback(text_msg_callback, RoomMessageText)
	client.add_event_callback(image_msg_callback, RoomMessageImage)

	#sync_forever() ?
	while True:
		sync_response = await client.sync(timeout=6000,
			sync_filter= {
				"room": { #RoomFilter
					"timeline":{ #RoomEventFilter
						"limit": 5,
						"not_senders": ["@"+username+":"+domain], #ignore own messages
						"types": ["m.room.message"]
					}
				}
			}
		)
		if(type(sync_response) is responses.SyncError):
			print("failed to sync: "+str(type(sync_response)))
			print(str(sync_response))

		await asyncio.sleep(1)

print("start")

try:
	asyncio.get_event_loop().run_until_complete(main())
except KeyboardInterrupt:
	print("KeyboardInterrupt, exiting.")
	shutil.rmtree(save_folder)
	exit()