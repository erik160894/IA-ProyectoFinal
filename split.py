#!/usr/bin/env python3

import os
import argparse
import re
import datetime
import multiprocessing
import sys

from pydub import AudioSegment


def get_audio_files(path, stations=None, days=None, hours=None):
    if not os.path.exists(path):
        raise Exception('Source folder not found')

    def check_filter(name):
        p = name.split('.')
        if len(p) != 2:
            return False
        if p[-1] not in ['mp3', 'ogg']:
            return False
        p = re.search('([a-zA-Z_]*)([0-9]*)', name).group(1, 2)
        if len(p) != 2:
            return False
        if stations and p[0] not in stations:
            return False
        date = datetime.datetime.fromtimestamp(int(p[1]))
        if days and str(date.weekday()) not in days:
            return False
        if hours and date.hour not in hours:
            return False
        return True

    return [os.path.join(path, f) for f in os.listdir(path) if check_filter(f)]


def split_audio_file(path, dest, duration):
    if not os.path.exists(dest):
        raise Exception('Destination folder not found')
    if not os.path.exists(path):
        raise Exception('Audio file not found')

    name = os.path.basename(path)
    station, timestamp = re.search('([a-zA-Z_]*)([0-9]*)', name).group(1, 2)
    timestamp = int(timestamp)

    song = AudioSegment.from_file(path, path.split('.')[-1])
    sr = 1000

    for i, start in enumerate(range(0, len(song), duration*sr)):
        if start + duration*sr > len(song):
            break

        f_out_name = station + str(timestamp + i*duration) + ".mp3"
        song_part = song[start:start + duration*sr]
        song_part.export(os.path.join(dest, f_out_name), format='mp3')


def worker(_id, queue_in, queue_out, dest, duration):
    print('Worker', _id, 'starting...')
    while True:
        task = queue_in.get()
        try:
            split_audio_file(task, dest, duration)
            queue_out.put('Ok')
        except:
            print('Error with file: ', task, file=sys.stderr)
            queue_out.put('Error')


def run(args):
    print('Listing audio files...')
    files = get_audio_files(args.source, stations=args.f_stations, days=args.f_day, hours=args.f_hour)
    print(len(files), 'audio files found.')
    print('Loading tasks to queue.')

    tasks = multiprocessing.Queue()
    results = multiprocessing.Queue()
    for i, f in enumerate(files):
        tasks.put(f)

    print('Starting multi-processes...')
    for _ in range(multiprocessing.cpu_count()):
        process = multiprocessing.Process(target=worker, args=(_, tasks, results, args.dest, args.duration))
        process.daemon = True
        process.start()

    print('Waiting for results...')
    for i in range(len(files)):
        results.get()
        print('\r', int((i+1)*100.0/len(files)), '% done.', end='')
    print('\nEnd.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-fs', '--f_stations', action='append', type=str)
    parser.add_argument('-fd', '--f_day', type=str)
    parser.add_argument('-fh', '--f_hour', type=int, action='append')
    parser.add_argument('-d', '--duration', type=int, default=2)
    parser.add_argument('source', type=str)
    parser.add_argument('dest', type=str)

    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
