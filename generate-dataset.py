#!/usr/bin/env python3

import librosa
import numpy as np
import argparse
import multiprocessing
import csv
import os


def extract_feature(file_name):
    X, sample_rate = librosa.load(file_name)
    stft = np.abs(librosa.stft(X))
    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
    chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0)
    mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T, axis=0)
    contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate).T, axis=0)
    tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(X), sr=sample_rate).T, axis=0)
    return mfccs, chroma, mel, contrast, tonnetz


def worker(w_id, queue_in, queue_out, folder):
    print('Worker', w_id, 'starting...')
    while True:
        _id = queue_in.get()
        try:
            mfccs, chroma, mel, contrast, tonnetz = extract_feature(os.path.join(folder, _id + '.mp3'))
            queue_out.put((_id, mfccs, chroma, mel, contrast, tonnetz))
        except:
            queue_out.put(None)


def run(tags_csv, samples_folder, out_csv):
    if not os.path.exists(tags_csv):
        print('Tags csv file not found.')
        return

    if not os.path.isdir(samples_folder):
        print('Samples folder not found.')
        return

    tasks = multiprocessing.Queue()
    results = multiprocessing.Queue()

    print('Loading tags csv file')
    with open(tags_csv) as f_in:
        with open(out_csv, 'w') as f_out:
            csv_in = csv.reader(f_in)
            csv_out = csv.writer(f_out)

            csv_in.__next__()
            tasks_count = 0
            tag_map = {}

            print('Uploading tasks to queue.')
            for row in csv_in:
                tag_map[row[0]] = row[1]
                tasks_count += 1
                tasks.put(row[0])
            print(tasks_count, 'samples found...')

            print('Starting multi-processes...')
            for _ in range(multiprocessing.cpu_count()):
                process = multiprocessing.Process(target=worker, args=(_, tasks, results, samples_folder))
                process.daemon = True
                process.start()

            n_row = ['id', 'tag']
            for tp, length in [('mfcss', 40), ('chroma', 12), ('mel', 128), ('contrast', 7), ('tonnetz', 6)]:
                n_row.extend([tp + str(x) for x in range(length)])
            csv_out.writerow(n_row)

            print('Waiting for results..')
            for i in range(tasks_count):
                result = results.get()
                if result:
                    _id = result[0]
                    n_row = [_id, tag_map[_id]]
                    for ft in result[1:]:
                        n_row.extend(ft)
                    csv_out.writerow(n_row)
                print('\r', int((i+1)*100.0/tasks_count), '% completed.', end='')
            print('\nEnd.')


def parse_args():
    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('required')
    required_args.add_argument('--tags_csv', '-i', type=str, help='Csv file containing tags', required=True)
    required_args.add_argument('--samples', '-s', type=str, help='Directory containing audio samples', required=True)
    parser.add_argument('--out_csv', '-o', type=str, default='data-set.csv', help='Output csv file')

    return parser.parse_args()


def main():
    args = parse_args()
    run(args.tags_csv, args.samples, args.out_csv)


if __name__ == '__main__':
    main()
