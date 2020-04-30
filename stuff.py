
import os, random, re
from nio import exceptions, responses

image_ext_whitelist = ["jpeg", "jpg", "png", "jpe", "webp", ]

def write_bin(path, data):
	outfile = open(path, "w+b")
	outfile.write(data)

#returns image path or None if failed
async def download_image(client, server_name, media_id, save_folder):
	dl_response = await client.download(server_name, media_id)
	if type(dl_response) is not responses.DownloadResponse:
		print("failed to download image: "+str(type(dl_response)))
		return None

	print("dl_response:\n"+str(type(dl_response))+"\n"+str(dl_response)+"\n")

	#get file extension from dl_response.content_type
	file_ext = re.search(r"image/(\w+)", dl_response.content_type).groups()[0]
	if file_ext not in image_ext_whitelist:
		print("Unsupported file type: "+str(file_ext))
		return None

	#find a filename that doesn't exist yet
	goeie_naam = False
	while not goeie_naam:
		image_path = save_folder+"/"+str(random.randint(0, 99999999))+'.'+file_ext
		goeie_naam = not os.path.lexists(image_path)

	write_bin(image_path, dl_response.body)
	print("saved as "+image_path)
	return image_path

#returns mxc of file
async def upload_image(client, file_path):
	
	#get mimetype from file extension
	file_ext = re.search(r"\.(\w+)$", file_path).groups()[-1]
	mimetype = "image/"+file_ext

	#upload
	file_path_holder = StringHolder(file_path)
	try:
		ul_response = await client.upload(file_path_holder.get_string, mimetype)
	except exceptions.TransferCancelledError:
		print("TransferCancelledError")
		return None

	ul_response_response = ul_response[0]
	# decryption_info = ul_response[1]

	if type(ul_response_response) is responses.UploadError:
		print("UploadError")
		return None

	# print("ul_response:\n")
	# print(str(type(ul_response)))
	# for idk in ul_response:
	# 	print(idk)

	return ul_response_response.content_uri

class StringHolder:
	def __init__(self, a_string):
		self.the_string = a_string

	def get_string(self, too_many_request_errors_count, server_timeout_exceptions_count):
		return self.the_string