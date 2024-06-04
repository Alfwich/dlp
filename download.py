#!/usr/bin/python3

import subprocess
import sys
import os

# yt-dlp https://www.youtube.com/watch?v=ibVm6HgNTjM -o tester
# ffmpeg -i 'Pinkzebra - Chasing The Sunshine [4Ov9Xj7Knu0].mkv' test.mp3

build_dir = "build"

def prepare_dir():
    try:
        os.mkdir(build_dir)
    except OSError as error:
        pass

def find_processed_file(name):

    for f in os.listdir("."):
        if f.startswith(f"{name}."):
            return f

def download_video(url, name):
    prepare_dir()
    os.chdir(build_dir)
    subprocess.run([f"yt-dlp", url, "-o", name])
    video_name = find_processed_file(name)
    subprocess.run([f"ffmpeg", "-i", video_name, f"{name}.mp3"])
    print(f"Video downloaded in build/{name}.mp3")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Expected usage: python download.py <url> <file-name>")
    else:
        download_video(sys.argv[1], sys.argv[2])

