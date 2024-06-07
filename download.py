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
        final_name = "-".join(fs_format(os.path.splitext(f)[0]).split("-")[0:-1])
        return {"raw": f, "final": final_name}

def move_files():
    for f in os.listdir(build_dir):
        if f.endswith(".mp3"):
            log(f"Installing {f}\n") 
            subprocess.run(["cp", f"{build_dir}/{f}", f"{server_dir}/{f}"])

def prune_files():
    files_to_prune = list(filter(lambda x: x.suffix == ".mp3", reversed(sorted(Path(server_dir).iterdir(), key=os.path.getmtime))))[100:]

    if len(files_to_prune) > 0:
        log(f"Pruning {len(files_to_prune)} files ... ")
        for f in files_to_prune:
            f.unlink()
        log(f"Done!\n")

def download_video(url, final_type):
    cwd = os.getcwd()
    os.chdir(build_dir)
    log(f"Downloading video: [{url}] ... ")
    subprocess.run([f"/usr/local/bin/yt-dlp", url, "--no-playlist"])
    log("Done!\n")
    title = find_processed_file()
    log(f"Converting video to .{final_type} ... ")
    subprocess.run([f"/usr/bin/ffmpeg", "-i", title["raw"], f'{title["final"]}.{final_type}'], stderr=subprocess.STDOUT)
    log("Done!\n")
    os.chdir(cwd)

def main(video_url, final_type):
    prepare_dir()
    download_video(video_url, final_type)
    move_files()
    prune_files()
    cleanup_dir()
    log("Done!\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        log("Expected usage: ./download.py <url> <type>\n")
    else:
        main(sys.argv[1], sys.argv[2])


