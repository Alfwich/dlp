#!/usr/bin/python3

import subprocess
import sys
import os
import urllib.request
import json
import urllib
import shutil
import string
import time
import stat

from pathlib import Path

build_dir = "build"
server_dir = "/www/wuteri.ch/misc"

def log(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

def fs_format(name):
    return "".join(c for c in name if (c.isalpha() or c.isdigit() or c==' ') and c in string.printable).rstrip().replace("  ", " ").replace(" ", "-")

def prepare_dir():
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)


def cleanup_dir():
    files_to_prune = list(filter(lambda x: x.name != 'yt-dlp', Path(f"{server_dir}/{build_dir}").iterdir()))
    for f in files_to_prune:
        f.unlink()


def find_processed_file():
    for f in os.listdir("."):
        if f != 'yt-dlp':
            return f

def get_name_from_file(f):
        return "-".join(fs_format(os.path.splitext(f)[0]).split("-")[0:-1])

def move_files(final_type):
    for f in os.listdir(build_dir):
        if f.endswith(final_type):
            log(f"Installing {f}\n") 
            subprocess.run(["cp", f"{build_dir}/{f}", f"{server_dir}/content/{f}"])

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
    acquire_yt_dlp()
    log(f"Downloading video: [{url}] as {final_type} ... \n")
    exec_cmd(["./yt-dlp", url, "--no-playlist"])
    log("Done!\n")
    video_file = find_processed_file()
    title = f"{get_name_from_file(video_file)}.{final_type}"
    existing_file = Path(f"{server_dir}/content/{title}")
    if not existing_file.exists():
        log(f"Converting video to .{final_type} ... \n")
        video_options = ["--codec", "copy"] if final_type is "mp4" else []
        exec_cmd([f"/usr/bin/ffmpeg", "-i", video_file] + video_options + [title])
        log("Done!\n")
    else:
        log(f"Found existing content file, aborting.\n")
    os.chdir(cwd)

yt_binary_name = "yt-dlp"
yt_dlp_download_url="https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux_armv7l"
yt_dlp_ttl = 60 * 60 * 24
def acquire_yt_dlp():

    existing_yt_dlp = Path(yt_binary_name)
    if existing_yt_dlp.exists():
        log(f"Found yt-dlp (age={time.time() - os.path.getmtime(yt_binary_name)}s)\n")
    if not existing_yt_dlp.exists() or time.time() - os.path.getmtime(yt_binary_name) > yt_dlp_ttl:
        log("Downloading ty-dlp\n")
        exec_cmd(["wget", yt_dlp_download_url, "-O", "yt-dlp"])
        exec_cmd(["chmod", "775", "yt-dlp"])
        exec_cmd(["touch", "yt-dlp"])

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


