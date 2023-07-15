import csv
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=True)

# Global constants
CSV_PATH = "./Redeptions_Generate.csv"
MONKEY_IMAGES_DIRECTORY = "./WuKongLayer"
OUTPUT_DIRECTORY = "./NFTImages"
SIGNATURE_PATH = "./Signature_HQ.PNG"
LOGO_PATH = "Logo_HQ.PNG"
FONT_PATH = "./arlrdbd.ttf"
FONT_SIZE = 140
IMAGE_PADDING = 40
LOGO_SIZE = 360



# Global variables
nft_info_list = []
monkey_images_dict = {}
try:
	signature_image = Image.open(SIGNATURE_PATH).convert("RGBA")
except:
	print(f"{Fore.LIGHTRED_EX}Signature image not found! Please put Signature_HQ.PNG to the current working directory!")
	sys.exit()

try:
	logo_image = Image.open(LOGO_PATH).convert("RGBA").resize((LOGO_SIZE, LOGO_SIZE))
except:
	print(f"{Fore.LIGHTRED_EX}Logo image not found! Please put Logo_HQ.PNG to the current working directory!")
	sys.exit()

try:
	font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
except:
	print(f"{Fore.LIGHTRED_EX}Font not found! Please put arlrdbd.ttf to the current working directory!")
	sys.exit()



def get_nft_info_list_from_csv(csv_path: str) -> list[dict]:
	"""
		Get the image stack, nft number and signature boolean from the csv file,
		and return a list of dictionaries containing the info
	"""
	nft_info_list: list[dict] = []

	try:
		with open(csv_path, 'r', encoding="utf-8", errors="ignore") as file:
			reader = csv.DictReader((row.replace('\0', '') for row in file))
			for info in reader:
				if len(info) == 0:
					continue
				temp_dict = {
					"images_stack": info.get("NFTDesign"),
					"nft_number_str": info.get("NFTNumber"),
					"signature_bool": True if info.get("Signature") == "True" else False
				}
				nft_info_list.append(temp_dict)
	except IOError:
		print(f"CSV file {csv_path} does not exist")

	return nft_info_list


def load_monkey_images(images_directory: str) -> dict:
	"""
		Load all possible images into a dict and sort them in the categories that they belongs to 
	"""
	images_dict = {
		"a": [],
		"b": [],
		"c": [],
		"d": [],
		"e": [],
		"f": [],
		"g": [],
	}

	if not os.path.exists(images_directory):
		print(f"Directory {images_directory} does not exist!")
		sys.exit()

	images = os.listdir(images_directory)
	images = sorted(images, key=lambda x: int(x.split('.')[0][3:]))
	for image_path in images:
		for key in images_dict.keys():
			if image_path.startswith(f"wk{key}"):
				images_dict[key].append(Image.open(f"{images_directory}/{image_path}").convert("RGBA"))

	return images_dict


def generate_nft_number_image(nft_number: str, width: int, height: int):
	text = f"My Way {nft_number}"
	image = Image.new("RGBA", (width, height))
	draw = ImageDraw.Draw(image)
	x = IMAGE_PADDING + logo_image.width + 35
	y = height - IMAGE_PADDING - logo_image.height + 95
	text_color = (0, 0, 0)
	draw.text((x, y), text, font=font, fill=text_color)

	return image


def stack_image_layers(images: list, stack_numbers_list: list, signature: bool):
	# for letter, number in zip(monkey_images_dict.keys(), stack_numbers_list):
	# 	images.append(monkey_images_dict[letter][number - 1])

	images.append(monkey_images_dict['a'][stack_numbers_list[0] - 1])
	images.append(monkey_images_dict['b'][stack_numbers_list[1] - 1])
	images.append(monkey_images_dict['c'][stack_numbers_list[2] - 1])

	if stack_numbers_list[6] == 6:
		images.append(monkey_images_dict['g'][stack_numbers_list[6] - 1])

	images.append(monkey_images_dict['e'][stack_numbers_list[4] - 1])

	if stack_numbers_list[3] != 1 and stack_numbers_list[3] != 3 and stack_numbers_list[3] != 10:
		images.append(monkey_images_dict['d'][stack_numbers_list[3] - 1])

	if stack_numbers_list[6] != 6 and stack_numbers_list[6] != 7 and stack_numbers_list[6] != 8 and stack_numbers_list[6] != 9:
		images.append(monkey_images_dict['g'][stack_numbers_list[6] - 1])

	if stack_numbers_list[5] != 8:
		images.append(monkey_images_dict['f'][stack_numbers_list[5] - 1])

	if stack_numbers_list[6] == 8:
		images.append(monkey_images_dict['g'][stack_numbers_list[6] - 1])
	
	if stack_numbers_list[3] == 1 or stack_numbers_list[3] == 10:
		images.append(monkey_images_dict['d'][stack_numbers_list[3] - 1])
	
	if stack_numbers_list[6] == 7 or stack_numbers_list[6] == 9:
		images.append(monkey_images_dict['g'][stack_numbers_list[6] - 1])

	if stack_numbers_list[5] == 8:
		images.append(monkey_images_dict['f'][stack_numbers_list[5] - 1])

	if stack_numbers_list[3] == 3:
		images.append(monkey_images_dict['d'][stack_numbers_list[3] - 1])

	if signature is True:
		images.append(signature_image)


def generate_stacked_image(stack_numbers_list: int, signature: bool, nft_number: str, output_path: str):
	"""
		Generate the output image layer by layer
	"""

	images = []
	stack_image_layers(images, stack_numbers_list, signature)

	max_width = max(image.width for image in images)
	max_height = max(image.height for image in images)
	images.append(generate_nft_number_image(nft_number, max_width, max_height))

	stacked_image = Image.new("RGBA", (max_width, max_height))

	# stack the layers
	for image in images:
		x_offset = (max_width - image.width) // 2  # Calculate the x offset to center the image horizontally
		y_offset = (max_height - image.height) // 2  # Calculate the y offset to center the image vertically
		stacked_image.paste(image, (x_offset, y_offset), mask=image)
	
	stacked_image.paste(logo_image, (IMAGE_PADDING, max_height - IMAGE_PADDING - logo_image.height - 15), mask=logo_image)

	stacked_image.save(output_path)


def put_images_to_folder(folder_name: str, nft_info_list: list[dict]):
	if not os.path.exists(folder_name):
		os.mkdir(folder_name)

	for nft_info in nft_info_list:
		stack_numbers = list(map(int, nft_info["images_stack"].split(',')))
		image_path = f"{folder_name}/{nft_info['nft_number_str'].zfill(4)}.png"
		if os.path.exists(image_path):
			print(f"{Fore.CYAN}{image_path} already exists, skipping...")
			continue
		generate_stacked_image(stack_numbers, nft_info["signature_bool"], nft_info["nft_number_str"], image_path)
		print(f"{Fore.LIGHTMAGENTA_EX}Generated {nft_info['nft_number_str']}.png!")


def close_images():
	for category in monkey_images_dict.values():
		for image in category:
			image.close()
	logo_image.close()
	signature_image.close()


def main():
	global nft_info_list, monkey_images_dict

	print(f"{Fore.YELLOW}Initializing...")
	nft_info_list = get_nft_info_list_from_csv(CSV_PATH)
	monkey_images_dict = load_monkey_images(MONKEY_IMAGES_DIRECTORY)
	print(f"{Fore.BLUE}Started generating...")
	put_images_to_folder(OUTPUT_DIRECTORY, nft_info_list)
	close_images()
	print(f"{Fore.GREEN}Done!")


if __name__ == "__main__":
	main()