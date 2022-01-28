'''
Sqlite3 database functions store the PlayStation game information
'''

# System imports
from sqlite3 import connect, Error

# Database file path
DATABASE = ''


# **********************************************************************************************************************
def set_database_path(database_path):
	global DATABASE
	DATABASE = database_path
# **********************************************************************************************************************


# **********************************************************************************************************************
def create_database():
	_create_games_table()
	_create_tracks_table()
	_create_track_total_table()
# **********************************************************************************************************************


# **********************************************************************************************************************
def insert_game(game_id, name, release_date, edc, anti_mod, libcrypt, num_of_tracks):
	_insert(f'''INSERT INTO games 
			(game_id, name, release_date, edc, anti_mod, libcrypt, num_of_tracks) 
			VALUES 
			("{game_id}","{name}","{release_date}",{edc},{anti_mod},{libcrypt},{num_of_tracks});''')
# **********************************************************************************************************************


# **********************************************************************************************************************
def insert_track(game_id, track_number, pregap, length, sectors, size, crc, md5, sha):
	_insert(f'''INSERT INTO tracks 
			(game_id, track_number, pregap, length, sectors, size, crc, md5, sha) 
			VALUES 
			("{game_id}",{track_number},"{pregap}","{length}","{sectors}","{size}","{crc}","{md5}","{sha}");''')
# **********************************************************************************************************************

# **********************************************************************************************************************
def insert_track_total(game_id, length_total, sectors_total, size_total, crc_total):
	_insert(f'''INSERT INTO track_totals 
			(game_id, length_total, sectors_total, size_total, crc_total) 
			VALUES 
			("{game_id}","{length_total}","{sectors_total}","{size_total}","{crc_total}");''')
# **********************************************************************************************************************


# **********************************************************************************************************************
def _insert(query):
	conn = _create_connection(DATABASE)
	cursor = conn.cursor()
	insert_query = query
	cursor.execute(insert_query)
	conn.commit()
	cursor.close()
	conn.close()
# **********************************************************************************************************************


# **********************************************************************************************************************
def _create_connection(db_file):
	conn = None
	try:
		conn = connect(db_file)
		return conn
	except Error as error:
		print(error)

	return conn
# **********************************************************************************************************************


# **********************************************************************************************************************
def _create_table(create_table_sql):
	conn = _create_connection(DATABASE)
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except Error as error:
		print(error)
	conn.close()
# **********************************************************************************************************************


# **********************************************************************************************************************
def _create_games_table():
	sql_games_table = """ CREATE TABLE IF NOT EXISTS games (
										id INTEGER PRIMARY KEY,
										game_id varchar(10) NOT NULL UNIQUE,
										name varchar(200) NOT NULL,
										release_date varchar(20),
										edc bool,
										anti_mod bool,
										libcrypt bool,
										num_of_tracks int
									); """
	_create_table(sql_games_table)
# **********************************************************************************************************************


# **********************************************************************************************************************
def _create_tracks_table():
	sql_tracks_table = """CREATE TABLE IF NOT EXISTS tracks (
									id INTEGER PRIMARY KEY,
									game_id varchar(10) NOT NULL,
									track_number int NOT NULL,
									pregap varchar(30) NOT NULL,
									length varchar(30) NOT NULL,
									sectors varchar(30) NOT NULL,
									size varchar(30) NOT NULL,
									crc varchar(30) NOT NULL,
									md5 varchar(60) NOT NULL,
									sha varchar(60) NOT NULL,
									FOREIGN KEY (game_id) REFERENCES games (game_id)
								);"""
	_create_table(sql_tracks_table)
# **********************************************************************************************************************


# **********************************************************************************************************************
def _create_track_total_table():
	sql_track_totals_table = """CREATE TABLE IF NOT EXISTS track_totals (
									id INTEGER PRIMARY KEY,
									game_id varchar(10) NOT NULL,
									length_total varchar(30) NOT NULL,
									sectors_total varchar(30) NOT NULL,
									size_total varchar(30) NOT NULL,
									crc_total varchar(30) NOT NULL,
									FOREIGN KEY (game_id) REFERENCES games (game_id)
								);"""				
	_create_table(sql_track_totals_table)
# **********************************************************************************************************************
