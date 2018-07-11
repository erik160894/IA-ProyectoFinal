#!/usr/bin/env python3

import argparse
import datetime
import os
import sys
import threading
import urllib.request
import math
import json


def record_interval(stop_rec, stream_url, target_dir, station, interval):
    filename = os.path.join(target_dir, station.lower().replace(" ", "_"))
    file_extension = ".mp3"

    conn = urllib.request.urlopen(stream_url)
    content_type = conn.getheader('Content-Type')
    if content_type == 'application/ogg' or content_type == 'audio/ogg':
        file_extension = '.ogg'
    elif content_type == 'audio/x-mpegurl':
        print('Sorry, M3U playlists are currently not supported')
        sys.exit()
    elif content_type != "audio/mpeg":
        print('Unknown content type "' + content_type + '". Assuming mp3.')

    timestamp = datetime.datetime.now().timestamp()
    timestamp = math.floor(timestamp + 0.5)

    tmp_filename = filename + ".downloading"
    with open(tmp_filename, "wb") as target:
        while not stop_rec.is_set() and not conn.closed and datetime.datetime.now().timestamp() - timestamp < interval:
            target.write(conn.read(1024))

    conn.close()
    os.rename(tmp_filename, filename + str(timestamp) + file_extension)


def record_worker(stop_rec, stream_url, target_dir, station, interval):
    while not stop_rec.is_set():
        try:
            record_interval(stop_rec, stream_url, target_dir, station, interval)
        except Exception as e:
            print(e, file=sys.stderr)


def record(stations, target_dir, interval):
    stop_rec = threading.Event()

    recording_threads = []
    for station in stations:
        record_thread = threading.Thread(target=record_worker, args=(stop_rec, station['endpoint'], target_dir, station['name'], interval))
        recording_threads.append(record_thread)

    for record_thread in recording_threads:
        record_thread.setDaemon(True)
        record_thread.start()
    
    for record_thread in recording_threads:
        record_thread.join()

    stop_rec.set()


def parse_arguments():
    parser = argparse.ArgumentParser(description='This script record internet streaming live stations.')

    parser.add_argument('-df', "--data_folder", type=str, help="Destination folder for recorded audios.", default="data")
    parser.add_argument('-i', "--interval", type=int, help="Interval time to reset recording", default=10*60)
    parser.add_argument('-f', "--stations", type=str, help="Json file with stations list", default="stations.json")

    return parser.parse_args()


def main():
    args = parse_arguments()
   
    stations = []
    try:
        with open(args.stations) as target:
            stations.extend(json.loads(target.read()))
    except Exception as e:
        print("Error loading config file: ", e, file=sys.stderr)
    
    if not os.path.isdir(args.data_folder):
        print('Folder to save data does not exist', file=sys.stderr)
        exit(0)
    
    record(stations, args.data_folder, args.interval)


if __name__ == '__main__':
    main()
