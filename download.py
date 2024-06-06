#!/usr/bin/python3

import subprocess
import sys
import os
import urllib.request
import json
import urllib
import shutil
import string

from pathlib import Path

build_dir = "build"
server_dir = "/www/wuteri.ch/misc"

def log(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

def get_title_from_url(url):
    params = {"format": "json", "url": url}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())

        return "".join(c for c in data['title'] if (c.isalpha() or c.isdigit() or c==' ') and c in string.printable).rstrip().replace("  ", " ").replace(" ", "-")

def prepare_dir():
    # Ensure we are starting from a clean build dir
    if os.path.exists(build_dir):
        cleanup_dir()

    os.mkdir(build_dir)

def cleanup_dir():
    shutil.rmtree(build_dir)

def find_processed_file(name):
    for f in os.listdir("."):
        if f.startswith(f"{name}."):
            return f

def move_files():
    for f in os.listdir(build_dir):
        if f.endswith(".mp3"):
            log(f"Installing {f}\n") 
            subprocess.run(["cp", f"{build_dir}/{f}", f"{server_dir}/{f}"])

def prune_files():
    files_to_prune = list(filter(lambda x: x.suffix == ".mp3", reversed(sorted(Path(server_dir).iterdir(), key=os.path.getmtime))))[10:]

    if len(files_to_prune) > 0:
        log(f"Pruning {len(files_to_prune)} files ... ")
        for f in files_to_prune:
            f.unlink()
        log(f"Done!\n")

def make_index():
    music_files = list(map(lambda x: x.name, filter(lambda x: x.suffix == ".mp3", reversed(sorted(Path(server_dir).iterdir(), key=os.path.getmtime)))))
    with open(f"{server_dir}/data.js", "w") as f:
        array = json.dumps(music_files)
        f.write(f"_data={array};")

    log("Done!\n")

def download_video(url):
    cwd = os.getcwd()
    os.chdir(build_dir)
    title = get_title_from_url(url)
    log(f"Downloading video: {title}... ")
    subprocess.run([f"/usr/local/bin/yt-dlp", url, "--no-playlist", "-o", title])
    log("Done!\n")
    video_name = find_processed_file(title)
    log("Converting video to .mp3 ... ")
    subprocess.run([f"/usr/bin/ffmpeg", "-i", video_name, f"{title}.mp3"], stderr=subprocess.STDOUT)
    log("Done!\n")
    os.chdir(cwd)

def main(video_url):
    prepare_dir()
    download_video(video_url)
    move_files()
    prune_files()
    make_index()
    cleanup_dir()
    log("Done!\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        log("Expected usage: ./download.py <url>\n")
    else:
        main(sys.argv[1])


