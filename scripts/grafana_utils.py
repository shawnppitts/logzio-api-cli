from . import endpoints, common
import random, string

# ANSI color codes for CLI text
white = "\033[1,37m+"
green = "\033[0;32m"
yellow = "\033[1;33m"
blue = "\033[0;34m"
red = "\033[0;31m"
cyan = "\033[0;36m"
end_color = "\033[0m"
bold = "\033[1m"

def exist_and_create(folders, folder_name, api_url, api_token):
	warning_message = print(f"{yellow}WARNING! All Alerts will be nested under the folder '{folder_name}'{end_color}")
	folder_uid = ""
	for folder in folders:
		if (folder["title"] == folder_name):
			folder_uid = folder["uid"]
			print(f"We have detected the folder {blue}{folder_name}{end_color} already exists.\n")
			create_new_folder = False
			break
		# If it does not exist then we need to create the new folder
		else:
			create_new_folder = True

	# If flag to create is true then create folder
	if create_new_folder == True:
		print(f"Creating {folder_name} folder...")
		folder_response = endpoints.create_grafana_folder(folder_name, api_url, api_token)
		folder_uid = folder_response["uid"]
		print(f"{folder_name} successfully created with uid {folder_uid}")
		return folder_uid
	# If not just use existing uid
	elif create_new_folder == False:
		return folder_uid