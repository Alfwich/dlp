#!/usr/bin/python3

import subprocess
import sys
import os
import string
import time
import hashlib
import random

from pathlib import Path
from datetime import datetime

server_dir = "/www/wuteri.ch/dlp"
target_dir = f"{server_dir}/target"
content_dir = f"{server_dir}/content"


def log(msg):
    preamble = f"[{datetime.now().strftime('%H:%M:%S:%f')}]"
    sys.stdout.write(f"{preamble} {msg}")
    sys.stdout.flush()


def fs_format(name):
    return "".join(c for c in name if (c.isalpha() or c.isdigit() or c == ' ') and c in string.printable).rstrip().replace("  ", " ").replace(" ", "-").strip().lstrip("-")


def prepare_dir(working_dir, scope):
    Path(working_dir).mkdir(parents=True, exist_ok=True)
    Path(f"{content_dir}/{scope}").mkdir(parents=True, exist_ok=True)
    exec_cmd(["df", "-h"])


def find_downloaded_file(working_dir):
    log(f"Looking for file in {working_dir}\n")
    for f in os.listdir(working_dir):
        log(f"found: {f}\n")
        return f


def get_name_from_file(f):
    return "-".join(fs_format(os.path.splitext(f)[0]).split("-")[0:-1])


def move_files(working_dir, scope, final_type):
    if final_type == "any":
        final_type = Path(working_dir).suffix.split(".")[-1]

    for f in os.listdir(working_dir):
        if f.endswith(final_type):
            log(f"Installing {f}\n")
            exec_cmd(["cp", f"{working_dir}/{f}", f"{content_dir}/{scope}/{f}"])
            exec_cmd(["chmod", "777", f"{content_dir}/{scope}", "-R"])


def cleanup_dir(working_dir, scope):
    files_to_prune = list(Path(working_dir).iterdir())

    for f in files_to_prune:
        f.unlink()

    Path(working_dir).rmdir()


def prune_files():
    files_to_prune = list(reversed(sorted(Path(f"{content_dir}").iterdir(), key=os.path.getmtime)))[20:]

    if len(files_to_prune) > 0:
        log(f"Pruning {len(files_to_prune)} files ... ")
        for f in files_to_prune:
            f.unlink()
        log(f"Done!\n")


def exec_cmd(cmd):
    pretty_cmd = " ".join(cmd)
    log(f"Executing command: {pretty_cmd}\n")
    subprocess.run(cmd, stderr=subprocess.STDOUT)


def get_args_file_additions(args):
    result = []

    if "start" in args and len(args["start"]) > 0:
        result.append(f'start_{args["start"]}s')

    if "duration" in args and len(args["duration"]) > 0:
        result.append(f'dur_{args["duration"]}s')

    if len(result) > 0:
        return "." + ".".join(result)

    return ""


def convert_video(working_dir, scope, video_file, final_type, args):
    args_file_additions = get_args_file_additions(args)
    title = f"{get_name_from_file(video_file)}{args_file_additions}.{final_type}"
    source_file_name = f"{working_dir}/{video_file}"
    dest_file = f"{content_dir}/{scope}/{title}"

    if not Path(dest_file).exists():
        log(f"Converting video to .{final_type} ... \n")
        video_options = ["-preset", "ultrafast"] if final_type is "mp4" else []
        start_options = ["-ss", args["start"]] if "start" in args and len(args["start"]) > 0 else []
        duration_options = ["-t", args["duration"]] if "duration" in args and len(args["duration"]) > 0 else []
        exec_cmd([f"{target_dir}/ffmpeg"] + start_options + ["-i", source_file_name] + duration_options + video_options + [title])
        log("Done!\n")


def download_and_process_video(working_dir, scope, url, final_type, args):
    cwd = os.getcwd()
    os.chdir(working_dir)
    acquire_yt_dlp()
    log(f"Downloading video: [{url}] as {final_type} ... \n")
    exec_cmd([f"{target_dir}/yt-dlp", url, "--no-playlist", "--ffmpeg-location", f"{target_dir}/ffmpeg"])
    log("Done downloading!\n")

    if final_type != "any":
        video_file = find_downloaded_file(working_dir)
        convert_video(working_dir, scope, video_file, final_type, args)
    else:
        video_file = find_downloaded_file(working_dir)
        renamed_file_name = get_name_from_file(video_file)
        renamed_file = f"{renamed_file_name}{Path(video_file).suffix}"
        exec_cmd(["mv", video_file, renamed_file])

    os.chdir(cwd)


yt_binary_name = "yt-dlp"
yt_dlp_download_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux"
yt_dlp_ttl = 60 * 60 * 24


def acquire_yt_dlp():

    yt_dlp_path = f"{target_dir}/{yt_binary_name}"
    existing_yt_dlp = Path(yt_dlp_path)
    if existing_yt_dlp.exists():
        age = time.time() - os.path.getmtime(yt_dlp_path)
        log(f"Found yt-dlp (age={age}s)\n")

    if not existing_yt_dlp.exists() or time.time() - os.path.getmtime(yt_dlp_path) > yt_dlp_ttl:
        yt_dlp_tmp_file = f"{yt_binary_name}.tmp"
        log("Downloading yt-dlp\n")
        exec_cmd(["wget", yt_dlp_download_url, "-O", yt_dlp_tmp_file])

        if Path(yt_dlp_tmp_file).exists():
            exec_cmd(["chmod", "775", yt_dlp_tmp_file])
            exec_cmd(["touch", yt_dlp_tmp_file])
            exec_cmd(["mv", yt_dlp_tmp_file, yt_dlp_path])

        else:
            log("Could not acquire yt-dlp binary\n")


def process_scope(in_scope):
    if not in_scope is None and len(in_scope.strip()) > 0:
        return in_scope.strip()

    return "global"


def new_working_dir(scope):
    result = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
    return f"{target_dir}/{scope}/{result[:15]}"


def main_payload(args):
    log(f"Starting job with args: {args}\n")
    main(args.get("url"), args.get("type"), args.get("scope"), args)


def main(video_url, final_type, scope, args={}):
    resolved_scope = process_scope(scope)
    working_dir = new_working_dir(resolved_scope)
    log(f"Executing download url: {video_url}, type: {final_type}, working_dir: {working_dir}\n")
    prepare_dir(working_dir, resolved_scope)
    download_and_process_video(working_dir, resolved_scope, video_url, final_type, args)
    move_files(working_dir, resolved_scope, final_type)
    cleanup_dir(working_dir, resolved_scope)
    log("Done adding video!\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        log("Expected usage: ./download.py <url> <type> [scope]\n")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
