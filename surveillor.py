#! /usr/bin/env python

import concurrent.futures
import json
import os
import sys
import threading
from datetime import datetime
from time import sleep
import multiprocessing
import random

import ffmpy
import requests


RAW_DATA_DIR_NAME = 'data_dump'
VID_DIR_NAME = 'vids_preprocessed'
VID_PROC_DIR_NAME = 'vids_processed'

def datetime_tag():
    return datetime.now().strftime("%y%m%d_%H%M%S")


def m3u8_link_recorder(m3u8_link: str, model_username: str, sleep_time: int):
    """records video through m3u8 link. Is called by concurrent_stream_recording 
    method to be executed once per m3u8 link in parallel.
    """

    model_path = os.path.join(VID_DIR_NAME, model_username)
    vid_name = f"{datetime_tag()}.mkv"
    vid_path = os.path.join(VID_DIR_NAME, model_username, vid_name)
    ff = ffmpy.FFmpeg(
        inputs={m3u8_link: None},
        outputs={vid_path: "-vf \"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf: text='%{gmtime\:%d/%m/%y %H\\\\\\\\\:%M}': x=w-text_w: y=0: fontcolor=white: fontsize=30\""}
    )
    print('CMDCMD')
    print(ff.cmd)

    if not os.path.isdir(VID_DIR_NAME):
        os.mkdir(VID_DIR_NAME)
    if not os.path.isdir(model_path):
        os.mkdir(model_path)


    thread_1 = threading.Thread(target=ff.run)
    thread_1.start()
    while not ff.process:
        sleep(sleep_time)
    ff.process.terminate()
    thread_1.join()


def model_list_grabber():
    """ask xhamsterlive.com which models are online (with all sorts of other data). 
    tuple index: id, uname, 480p option
    """

    url = f"https://xhamsterlive.com/api/front/v2/models?topLimit={random.randint(5000, 10000)}"
    r = requests.get(url, stream=True)
    req = json.loads(r.content)
    models = req.get("blocks")[5].get("models")
    model_list_saver(models)
    models_online_resolution_option_480p = []

    for model in models:
        id = str(model.get("id"))
        if model.get("broadcastSettings").get("presets").get("testing") == None:
            resolution_option_480p = False
        else:
            resolution_option_480p = True
        uname = str(model.get("username"))
        m3u8_link = str(model['hlsPlaylist'])
        models_online_resolution_option_480p.append(
            tuple([id, uname, resolution_option_480p, m3u8_link]))


    return models_online_resolution_option_480p, models


def model_list_saver(model_list):
    """called to save API-data to create a cool dataset.
    """

    json_file_name = f"{datetime_tag()}.json"
    json_file_path = os.path.join(RAW_DATA_DIR_NAME, json_file_name)

    if not os.path.isdir(RAW_DATA_DIR_NAME):
        os.mkdir(RAW_DATA_DIR_NAME)
    with open(json_file_path, "w") as fp:
        json.dump(model_list, fp)


def stream_download_decider(all_model_names_480_option: tuple, wait_secs: int = 300):
    """takes tuple of all models online with odel id, model uname and 480p option. Will 
    decide according to models_followed.txt list rank which four models to record.
    """

    models_followed_online = []
    if len(sys.argv) == 1:
        with open("models_followed.txt", "r") as f:
            for line in set([x for x in f.readlines()]):
                model_followed = line.replace("\n", "")
                for id_online, uname_online, option_480p_online, m3u8_link in all_model_names_480_option:
                    if model_followed == uname_online.lower():
                        models_followed_online.append(
                            tuple([id_online, uname_online, option_480p_online, m3u8_link]))
    else:
        models_followed = sys.argv[1:]
        for model_followed in models_followed:
            for id_online, uname_online, option_480p_online, m3u8_link in all_model_names_480_option:
                if model_followed == uname_online.lower():
                    models_followed_online.append(
                        tuple([id_online, uname_online, option_480p_online, m3u8_link]))
    if len(models_followed_online) > 0:
        print(models_followed_online)
        
    elif len(models_followed_online) == 0:
        print(f"None of your models are online. Waiting {wait_secs * 60} mins to check again.")
        sleep(wait_secs)

    return models_followed_online


def concurrent_stream_recording(models_online_followed: tuple, sleep_time: int, models_to_record: int):
    """Invokes concurrent library.
    """

    m3u8_links = []
    usernames = [x[1] for x in models_online_followed]

    for id, uname, option_480p, m3u8_link in models_online_followed:
        if option_480p:
            m3u8_links.append(m3u8_link.replace('_240p', '_480p'))
        elif not option_480p:
            m3u8_links.append(m3u8_link)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(m3u8_link_recorder, m3u8_links[:models_to_record], usernames[:models_to_record], [sleep_time] * models_to_record)


def video_stitcher(dir_):
    """invoke method for stitching together videos in each subdirectory of "vids_preprocessed"
    -directory which is instatiated by m3u8_link_recorder
    """

    if dir_ == VID_DIR_NAME or None:
        subdirs = os.listdir(VID_DIR_NAME)


        for subdir in subdirs:
            dir_and_subdir = os.path.join(VID_DIR_NAME, subdir)
            if len(os.listdir(dir_and_subdir)) > 1:
                vids = os.listdir(dir_and_subdir)
                list_txt_dir = os.path.join(dir_and_subdir, "my_list.txt")
                output_dir = os.path.join(dir_and_subdir, f"concat_{datetime_tag()}.mkv")

                dict_ = dict(zip([int(''.join((x.split('_')[-2], x.split('_')[-1].replace('.mkv', '')))) for x in vids], [x for x in vids]))
                vids_sorted = list(dict(sorted(dict_.items())).values())
                with open(list_txt_dir, "w") as fp:
                    for vid in vids_sorted:
                        vid_str = f"file {vid}\n"
                        fp.writelines(vid_str)

                ff = ffmpy.FFmpeg(
                    global_options={"-f concat -safe 0"},
                    inputs={list_txt_dir: None},
                    outputs={output_dir: "-c copy"}
                )
                ff.run()

                for vid in vids:
                    vid_dir = os.path.join(dir_and_subdir, vid)
                    os.remove(vid_dir)
                os.remove(list_txt_dir)

    elif dir_ == VID_PROC_DIR_NAME:
        files_raw = os.listdir(dir_)
        files = [x.split('_')[0] for x in files_raw]
        duplicate_models = set([x for x in files if files.count(x) > 1])
        list_txt_dir = os.path.join(dir_, "my_list.txt")
        for model in duplicate_models:
            vids = [x for x in files_raw if model in x]
            new_fp = os.path.join(VID_PROC_DIR_NAME, f'{model}_{datetime_tag()}.mp4')
            dict_ = dict(zip([int(''.join((x.split('_')[-2], x.split('_')[-1].replace('.mp4', '')))) for x in vids], [x for x in vids]))
            vids_sorted = list(dict(sorted(dict_.items())).values())
            with open(list_txt_dir, "w") as fp:
                for vid in vids_sorted:
                    vid_str = f"file {vid}\n"
                    fp.writelines(vid_str)
            new_fp = os.path.join(VID_PROC_DIR_NAME, f'{model}_{datetime_tag()}.mp4')
            ff = ffmpy.FFmpeg(
                global_options={"-f concat -safe 0"},
                inputs={list_txt_dir: None},
                outputs={f'{new_fp}': "-c copy"}
            )
            ff.run()

            for vid in vids:
                vid_dir = os.path.join(VID_PROC_DIR_NAME, vid)
                os.remove(vid_dir)
            os.remove(list_txt_dir)

def process_vids():

    video_stitcher(VID_DIR_NAME)
    video_stitcher(VID_PROC_DIR_NAME)

    if not os.path.exists(VID_PROC_DIR_NAME):
        os.mkdir(VID_PROC_DIR_NAME)

    models = os.listdir(VID_DIR_NAME)
    for model in models:
        fp = os.path.join(VID_DIR_NAME, model)
        file = os.listdir(fp)
        if len(file) > 1:
            pass
        full_fp = os.path.join(fp, file[0])
        new_file_name = f'{model}_{datetime_tag()}.mp4'
        new_fp = os.path.join(VID_PROC_DIR_NAME, new_file_name)
        print(f'processing {model}')

        ff = ffmpy.FFmpeg(
            inputs={full_fp: None},
            outputs={new_fp: "-c:v libx264 -preset fast"}
        )

        ff.run()
        if os.path.exists(full_fp):
            os.remove(full_fp)
        dir_clean_up()

def dir_clean_up():
    models = os.listdir(VID_DIR_NAME)
    for model in models:
        sub_dir = os.path.join(VID_DIR_NAME, model)
        files = os.listdir(sub_dir)
        if not files:
            os.rmdir(sub_dir)


def main():
    while True:
        for i in range(random.randint(2, 4)):
            models_online, models = model_list_grabber()
            models_online_followed = stream_download_decider(models_online, 300)
            concurrent_stream_recording(models_online_followed, random.randint(120, 300) , multiprocessing.cpu_count())
        video_stitcher(VID_DIR_NAME)


if __name__ == "__main__":
    main()
