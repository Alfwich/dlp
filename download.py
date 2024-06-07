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

def fs_format(name):
    return "".join(c for c in name if (c.isalpha() or c.isdigit() or c==' ') and c in string.printable).rstrip().replace("  ", " ").replace(" ", "-")

def prepare_dir():
    # Ensure we are starting from a clean build dir
    if os.path.exists(build_dir):
        cleanup_dir()

    os.mkdir(build_dir)

def cleanup_dir():
    shutil.rmtree(build_dir)

def find_processed_file():
    for f in os.listdir("."):
        return f

def get_name_from_file(f):
        return "-".join(fs_format(os.path.splitext(f)[0]).split("-")[0:-1])

def move_files(final_type):
    for f in os.listdir(build_dir):
        if f.endswith(final_type):
            log(f"Installing {f}\n") 
            subprocess.run(["cp", f"{build_dir}/{f}", f"{server_dir}/{f}"])

def prune_files():
    files_to_prune = list(filter(lambda x: x.suffix == ".mp3" or x.suffix == ".mp4", reversed(sorted(Path(server_dir).iterdir(), key=os.path.getmtime))))[20:]

    if len(files_to_prune) > 0:
        log(f"Pruning {len(files_to_prune)} files ... ")
        for f in files_to_prune:
            f.unlink()
        log(f"Done!\n")

def exec_cmd(cmd):
    pretty_cmd = " ".join(cmd)
    log(f"Executing command: {pretty_cmd}\n")
    subprocess.run(cmd, stderr=subprocess.STDOUT)

def download_video(url, final_type):
    cwd = os.getcwd()
    os.chdir(build_dir)
    log(f"Downloading video: [{url}] ... \n")
    exec_cmd([f"/usr/local/bin/yt-dlp", url, "--no-playlist"])
    log("Done!\n")
    video_file = find_processed_file()
    title = f"{get_name_from_file(video_file)}.{final_type}"
    log(f"Converting video to .{final_type} ... \n")
    exec_cmd([f"/usr/bin/ffmpeg", "-i", video_file, "--codec", "copy", title])
    log("Done!\n")
    os.chdir(cwd)

def main(video_url, final_type):
    log(f"Executing download url: {video_url}, type: {final_type}\n")
    prepare_dir()
    download_video(video_url, final_type)
    move_files(final_type)
    prune_files()
    cleanup_dir()
    log("Done!\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        log("Expected usage: ./download.py <url> <type>\n")
    else:
        main(sys.argv[1], sys.argv[2])


