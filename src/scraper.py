'''
Redump Web scrapper to gather PlayStation game information
'''

# System imports
from sys import argv, exit
from os import mkdir, remove
from os.path import exists, join, dirname, abspath
from time import sleep
from tabulate import tabulate
from requests import get
from bs4 import BeautifulSoup

# Local imports
from database import set_database_path, create_database, insert_game, insert_track, insert_track_total

SCRIPT_PATH = abspath(dirname(argv[0]))
OUT_PATH = join(SCRIPT_PATH, 'scrapped_files')
DATABASE_PATH = join(SCRIPT_PATH, 'redump_playstation.db')

LETTERS = ['~', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
BASE_URL = 'http://redump.org'
PROCESSED_GAMES = []

PRINT_DATA = False
WRITE_DATA = False
STORE_DATA = True

# It is best practice to have a short delay to prevent sending too many page requests to the server in quick succession
DELAY = 0.5


# **********************************************************************************************************************
def _get_page_content(page_url):
	response = get(page_url)
	return response.text
# **********************************************************************************************************************


# **********************************************************************************************************************
def _format_game_id(id):
	if ',' in id:
		id = id.split(',')[0]
	return id.replace(' ', '_').replace('-', '_')
# **********************************************************************************************************************


# **********************************************************************************************************************
def _format_game_name(game_name):
	return game_name.replace('"', '').replace("'", "")
# **********************************************************************************************************************


# **********************************************************************************************************************
def _print_game_info(game_name, game_id, release_date, has_edc, has_anti_mod, has_libcrypt, num_of_tracks):
	print(f'Game Name: {game_name}')
	print(f'Game ID: {game_id}')
	print(f'Release Date: {release_date}')
	print(f'EDC: {has_edc}')
	print(f'Anti Modchip: {has_anti_mod}')
	print(f'Libcrypt: {has_libcrypt}')
	print(f'Tracks: {num_of_tracks}')
# **********************************************************************************************************************


# **********************************************************************************************************************
def _print_track_info(track_num, pregap, length, sectors, size, crc, md5, sha):
	print(tabulate([[track_num, pregap, length, sectors, size, crc, md5, sha]], headers=['Track', 'Pregap', 'Length', 'Sectors', 'Size', 'CRC', 'MD5', 'SHA1']))
# **********************************************************************************************************************


# **********************************************************************************************************************
def _print_track_info_multi(tracks):
	print(tabulate([track for track in tracks], headers=['Track', 'Pregap', 'Length', 'Sectors', 'Size', 'CRC', 'MD5', 'SHA1']))
# **********************************************************************************************************************


# **********************************************************************************************************************
def _print_track_info_total(length_total, sectors_total, size_total, crc_total):
	print(tabulate([[length_total, sectors_total, size_total, crc_total]], headers=['Total Length', 'Total Sectors', 'Total Size', 'Total CRC']))
# **********************************************************************************************************************


# **********************************************************************************************************************
def _write_file(game_name, game_id, game_release_date, has_edc, has_anti_modchip, has_libcrypt, tracks, length_total, sectors_total, size_total, crc_total):
	if not exists(OUT_PATH):
		mkdir(OUT_PATH)
		
	if exists(OUT_PATH):
		with open(join(OUT_PATH, f'{game_id}.txt'), 'w') as f:
			f.write(f'Name: {game_name}\n')
			f.write(f'ID: {game_id}\n')
			f.write(f'Date: {game_release_date}\n')
			f.write(f'EDC: {has_edc}\n')
			f.write(f'Anti-Mod: {has_anti_modchip}\n')
			f.write(f'Libcrypt: {has_libcrypt}\n')
			f.write(f'Number of Tracks: {len(tracks)}\n')
			
			for track in tracks:
				f.write(f'Track Number: {track[0]}\n')
				f.write(f'Track Pregap: {track[1]}\n')
				f.write(f'Track Length: {track[2]}\n')
				f.write(f'Track Sectors: {track[3]}\n')
				f.write(f'Track Size: {track[4]}\n')
				f.write(f'Track CRC: {track[5]}\n')
				f.write(f'Track MD5: {track[6]}\n')
				f.write(f'Track SHA1: {track[7]}\n')
				
			if len(tracks) > 1:
				f.write(f'Total Length: {length_total}\n')
				f.write(f'Total Sectord: {sectors_total}\n')
				f.write(f'Total Size: {size_total}\n')
				f.write(f'Total CRC: {crc_total}\n')
# **********************************************************************************************************************


# **********************************************************************************************************************
def _insert_data(game_name, game_id, game_release_date, has_edc, has_anti_modchip, has_libcrypt, tracks, length_total, sectors_total, size_total, crc_total):
	edc = True if has_edc == 'Yes' else False
	anti_modchip = True if has_anti_modchip == 'Yes' else False
	libcrypt = True if has_libcrypt == 'Yes' else False
	insert_game(game_id, game_name, game_release_date, edc, anti_modchip, libcrypt, len(tracks))
	for track in tracks:
		insert_track(game_id, track[0], track[1], track[2], track[3], track[4], track[5], track[6], track[7])
		
	if len(tracks) > 1:	   
		insert_track_total(game_id, length_total, sectors_total, size_total, crc_total)
# **********************************************************************************************************************


# **********************************************************************************************************************
def _parse_game_details(game_info, tracks_number_index):
	game_id = game_info[5].text
	game_release_date = game_info[6].text
	has_edc = game_info[8].text
	has_anti_modchip = game_info[9].text
	has_libcrypt = game_info[10].text
	number_of_tracks = game_info[tracks_number_index].text
	return game_id, game_release_date, has_edc, has_anti_modchip, has_libcrypt, number_of_tracks
# **********************************************************************************************************************


# **********************************************************************************************************************
def _parse_track(track_rows):
	track_number = track_rows[2].text
	pregap = track_rows[4].text
	length = track_rows[5].text
	sectors = track_rows[6].text
	size = track_rows[7].text
	crc = track_rows[8].text
	md5 = track_rows[9].text
	sha = track_rows[10].text
	return track_number, pregap, length, sectors, size, crc, md5, sha
# **********************************************************************************************************************


# **********************************************************************************************************************
def _parse_multi_track(track_rows, number_of_tracks, number_of_colums):
	tracks = []

	# Remove the first 2 rows from the table
	track_rows.pop(0)
	track_rows.pop(0)

	# Loop through the columns and rows in the table
	count = 0
	for row in range(int(number_of_tracks)):
		for column in range(number_of_colums):
			if column == 0:
				track_number = track_rows[count].text
			elif column == 2 and number_of_colums == 9:
				pregap = track_rows[count].text
			elif column == 3 and number_of_colums == 10:
				pregap = track_rows[count].text
			elif column == 3 and number_of_colums == 9:
				length = track_rows[count].text
			elif column == 4 and number_of_colums == 10:
				length = track_rows[count].text
			elif column == 4 and number_of_colums == 9:
				sectors = track_rows[count].text
			elif column == 5 and number_of_colums == 10:
				sectors = track_rows[count].text 
			elif column == 5 and number_of_colums == 9:
				size = track_rows[count].text 
			elif column == 6 and number_of_colums == 10:
				column = track_rows[count].text	
			elif column == 6 and number_of_colums == 9:
				crc = track_rows[count].text	  
			elif column == 7 and number_of_colums == 10:
				crc = track_rows[count].text 
			elif column == 7 and number_of_colums == 9:
				md5 = track_rows[count].text 
			elif column == 8 and number_of_colums == 10:
				md5 = track_rows[count].text	 
			elif column == 8 and number_of_colums == 9:
				sha = track_rows[count].text	
				tracks.append([track_number, pregap, length, sectors, size, crc, md5, sha])
			elif column == 9:
				sha = track_rows[count].text	 
				tracks.append([track_number, pregap, length, sectors, size, crc, md5, sha])

			count += 1
			
	return tracks
# **********************************************************************************************************************


# **********************************************************************************************************************
def _scrape_data():
	# Loop through all of the letters in the array
	for letter in LETTERS:
		game_links = []

		# Get the html page source for the specified url
		page_content = _get_page_content(f'{BASE_URL}/discs/system/psx/letter/{letter}/')

		# Get the 'gamesblock' DIV from the page
		soup = BeautifulSoup(page_content, features="lxml")

		# Find all of the relevant links from the DIV
		for link in soup.find_all('a'):
			link_string = link.get('href')
			if link_string is not None:
				if 'disc' in link_string and 'system' not in link_string:
					if link_string.count('/') == 3:
						full_game_link = BASE_URL + link_string
						game_links.append(full_game_link)

		# Loop through all of the links
		for count, game_link in enumerate(game_links):
			page_content = _get_page_content(game_link)
			soup = BeautifulSoup(page_content, features='lxml')
			
			# Get the game name
			game_name = soup.find('h1').text
			game_name = _format_game_name(game_name)

			# Get the game info
			game_info_table = soup.find('table',{'class':'gameinfo'})
			game_info_headers = game_info_table.find_all('th')
			game_info = game_info_table.find_all('td')
			
			# Get the track number index (Sometimes it is the 11th element and sometimes it is the 12th)
			tracks_number_index = None
			for index, item in enumerate(game_info_headers):
				if item.text == 'Number of tracks':
					tracks_number_index = index
				
			# Get the game details
			game_id, game_release_date, has_edc, has_anti_modchip, has_libcrypt, number_of_tracks = _parse_game_details(game_info, tracks_number_index)
			
			# Some games have more than 1 ID (for special edition versions of the disc etc) so we get the 1st ID
			game_id = _format_game_id(game_id)
			
			# Prevent processing duplicate games
			if game_id not in PROCESSED_GAMES:

				# Get the track data
				track_table = soup.find('table',{'class':'tracks'})
				track_rows = track_table.find_all('td')
				tracks = []
				track_number = pregap = length = sectors = size = crc = md5 = sha = None
				
				# These variables are only used when there are multiple tracks
				crc_total = size_total = sectors_total = length_total = 0
				
				# Get the number of columns from the table (can vary between 9 or 10 columns)
				try:
					number_of_colums = int(track_rows[0]['colspan'])
				except (ValueError, KeyError) as e:
					number_of_colums = 0
				
				# If the cue_sheet contains a single track
				if int(number_of_tracks) == 1:
					track_number, pregap, length, sectors, size, crc, md5, sha = _parse_track(track_rows)
					tracks.append([track_number, pregap, length, sectors, size, crc, md5, sha])	
				else:
					tracks = _parse_multi_track(track_rows, number_of_tracks, number_of_colums)
	
				# Print the track data
				if PRINT_DATA:
					_print_game_info(game_name, game_id, game_release_date, has_edc, has_anti_modchip, has_libcrypt, number_of_tracks)
					if tracks:
						_print_track_info_multi(tracks)
					if len(tracks) > 1:
						_print_track_info_total(length_total, sectors_total, size_total, crc_total)
					print('\n')
				else:
					print(f'Processed: {game_name}')
					
				if WRITE_DATA:
					_write_file(game_name, game_id, game_release_date, has_edc, has_anti_modchip, has_libcrypt, tracks, length_total, sectors_total, size_total, crc_total)
					
				if STORE_DATA:
					_insert_data(game_name, game_id, game_release_date, has_edc, has_anti_modchip, has_libcrypt, tracks, length_total, sectors_total, size_total, crc_total)
				
				# Add the game ID to the list of processed games
				PROCESSED_GAMES.append(game_id)
				
				sleep(DELAY)
# **********************************************************************************************************************


# **********************************************************************************************************************
def main():
	if PRINT_DATA:
		print('\n')
		
	if STORE_DATA:
		if exists(DATABASE_PATH):
			remove(DATABASE_PATH)
		set_database_path(DATABASE_PATH)
		create_database()
	
	# Start the scrapping process
	_scrape_data()
# **********************************************************************************************************************


if __name__ == '__main__':
	main()
	