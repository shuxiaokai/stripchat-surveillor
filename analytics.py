import sqlite3
import json
import os
from time import sleep

from surveillor import RAW_DATA_DIR_NAME

DB_NAME = 'analytics.db'
ARCHIVE_DIR_NAME = 'data_dump_archive'


def initialise_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    return cur, con

def check_environment() -> bool:
    if os.path.isdir(RAW_DATA_DIR_NAME) or os.path.isdir(DB_NAME):
        cur = initialise_db()
        return True
    else:
        raise Exception('no raw data or database found!')

def read_jsons(how_many: int = 10) -> dict:
    '''Reads random jsons from RAW_DATA_DIR_NAME and outputs them as python-object.
    Also keeps track of file_name of read jsons.
    Returns:
        dict of struct {json_file_name:str : json_file: list}
    '''

    all_jsons = os.listdir(RAW_DATA_DIR_NAME)
    print(f'There are {len(all_jsons)} json files to process. Will process {how_many} at a time.')
    data_with_trace = {}
    for json_file in all_jsons[-how_many:]:
        with open(os.path.join(RAW_DATA_DIR_NAME, json_file), 'r') as f:
            try:
                json_list = json.load(f)
                data_with_trace[json_file] = json_list
            except json.JSONDecodeError as e:
                print(f'There is a problem with json_file {json_file}. Error: json.JSONDecodeError: {e}')
                pass

    return data_with_trace


def populate_db(cursor, data):
    '''Populates db with raw data left to process and will initiate delete of 
    processed data
    Args:
        cursor: tuple of struct (sqlite3-cursor, sqlite3-db-connecntion)
        data: dict of struct {json_file_name:str : json_file: list} 
    '''

    cur, con = cursor

    for i, file in enumerate(data.keys()):
        for model in data[file]:
            model_name = model['username']
            cur.execute(f'''CREATE TABLE IF NOT EXISTS '{model_name}' (date_online text, time_online text)''')
            cur.execute(f"INSERT INTO '{model_name}' VALUES ('{file.split('_')[0]}', '{file.split('_')[1].replace('.json', '')}')")
            con.commit()
        print(f'Processing {file} {i+1}/{len(data.keys())}')
    print()

def cleanup_after_raw_data(data):
    if not os.path.exists(ARCHIVE_DIR_NAME):
        os.mkdir(ARCHIVE_DIR_NAME)

    files_to_delete = list(data.keys())
    for file in files_to_delete:
        fp = os.path.join(RAW_DATA_DIR_NAME, file)
        fp_new = os.path.join(ARCHIVE_DIR_NAME, file)
        os.rename(fp, fp_new)

def process_raw_data():
    raise NotImplementedError



if __name__ == '__main__':
    if check_environment():
        cur, con = initialise_db()
        while True:
            data = read_jsons(how_many = 10)
            populate_db((cur, con), data)
            cleanup_after_raw_data(data)

        
        
