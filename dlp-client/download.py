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

from datetime import datetime

build_dir = "build"
server_dir = "/www/wuteri.ch/dlp"
#server_dir = "/home/pi/projects/dlp/dlp-web-server"

def log(msg):
    preamble = f"[{datetime.now().strftime('%H:%M:%S:%f')}]"
    sys.stdout.write(f"{preamble} {msg}")
    sys.stdout.flush()

def fs_format(name):
    return "".join(c for c in name if (c.isalpha() or c.isdigit() or c==' ') and c in string.printable).rstrip().replace("  ", " ").replace(" ", "-")

def prepare_dir(scope):
    if not os.path.exists(f"{server_dir}/{build_dir}"):
        os.mkdir(f"{server-dir}/{build_dir}")

    if not os.path.exists(f"{server_dir}/content/{scope}"):
        os.mkdir(f"{server_dir}/content/{scope}")

    exec_cmd(["df", "-h"])

def find_downloaded_file():
    path = f"{server_dir}/{build_dir}"
    log(f"Looking for file in {path}\n")
    for f in os.listdir(path):
        log(f"{f}\n")
        if f != 'yt-dlp':
            return f

def get_name_from_file(f):
        return "-".join(fs_format(os.path.splitext(f)[0]).split("-")[0:-1])

def move_files(scope, final_type):
    if final_type == "any":
        final_type = Path(find_downloaded_file()).suffix.split(".")[-1]

    for f in os.listdir(build_dir):
        if f.endswith(final_type):
            log(f"Installing {f}\n") 
            exec_cmd(["cp", f"{build_dir}/{f}", f"{server_dir}/content/{scope}/{f}"])
            exec_cmd(["chmod", "777", f"{server_dir}/content/{scope}", "-R"])

def cleanup_dir():
    files_to_prune = list(filter(lambda x: x.name != 'yt-dlp', Path(f"{server_dir}/{build_dir}").iterdir()))
    for f in files_to_prune:
        f.unlink()

def prune_files():
    files_to_prune = list(reversed(sorted(Path(f"{server_dir}/content").iterdir(), key=os.path.getmtime)))[20:]

    if len(files_to_prune) > 0:
        log(f"Pruning {len(files_to_prune)} files ... ")
        for f in files_to_prune:
            f.unlink()
        log(f"Done!\n")

def exec_cmd(cmd):
    pretty_cmd = " ".join(cmd)
    log(f"Executing command: {pretty_cmd}\n")
    subprocess.run(cmd, stderr=subprocess.STDOUT)

def convert_video(scope, video_file, final_type):
    title = f"{get_name_from_file(video_file)}.{final_type}"
    existing_file = Path(f"{server_dir}/content/{scope}/{title}")
    if not existing_file.exists():
        log(f"Converting video to .{final_type} ... \n")
        video_options = ["-preset", "ultrafast"] if final_type is "mp4" else []
        exec_cmd([f"/usr/bin/ffmpeg", "-i", video_file] + video_options + [title])
        log("Done!\n")

def download_and_process_video(scope, url, final_type):
    cwd = os.getcwd()
    os.chdir(build_dir)
    acquire_yt_dlp()
    log(f"Downloading video: [{url}] as {final_type} ... \n")
    exec_cmd(["./yt-dlp", url, "--no-playlist"])
    log("Done downloading!\n")

    if final_type != "any":
        video_file = find_downloaded_file()
        convert_video(scope, video_file, final_type)
    else:
        video_file = find_downloaded_file()
        renamed_file = f"{get_name_from_file(video_file)}{Path(video_file).suffix}"
        exec_cmd(["mv", video_file, renamed_file])

    os.chdir(cwd)

yt_binary_name = "yt-dlp"
yt_dlp_download_url="https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux_armv7l"
yt_dlp_ttl = 60 * 60 * 24
def acquire_yt_dlp():

    existing_yt_dlp = Path(yt_binary_name)
    if existing_yt_dlp.exists():
        log(f"Found yt-dlp (age={time.time() - os.path.getmtime(yt_binary_name)}s)\n")

    if not existing_yt_dlp.exists() or time.time() - os.path.getmtime(yt_binary_name) > yt_dlp_ttl:
        yt_dlp_tmp_file = f"{yt_binary_name}.tmp"
        log("Downloading ty-dlp\n")
        exec_cmd(["wget", yt_dlp_download_url, "-O", yt_dlp_tmp_file])
        if Path(yt_dlp_tmp_file).exists():
            exec_cmd(["chmod", "775", yt_dlp_tmp_file])
            exec_cmd(["touch", yt_dlp_tmp_file])
            exec_cmd(["mv", yt_dlp_tmp_file, yt_binary_name])

        else: 
            log("Could not acquire yt-dlp binary\n")

def process_scope(in_scope):
    if not in_scope is None and len(in_scope.strip()) > 0:
        return in_scope.strip()

    return "global"

def main(video_url, final_type, scope):
    resolved_scope = process_scope(scope)
    log(f"Executing download url: {video_url}, type: {final_type}, scope: {resolved_scope}\n")
    prepare_dir(resolved_scope)
    download_and_process_video(resolved_scope, video_url, final_type)
    move_files(resolved_scope, final_type)
    cleanup_dir()
    log("Done adding video!\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        log("Expected usage: ./download.py <url> <type> [scope]\n")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)


