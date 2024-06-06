#!/usr/bin/python3

import subprocess
import sys
import os
import urllib.request
import json
import urllib
import shutil

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
        return "".join(c for c in data['title'] if c.isalpha() or c.isdigit() or c==' ').rstrip().replace("  ", " ").replace(" ", "-")

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

def make_index():
    with open(f"{server_dir}/index.html", "w") as f:
        log(f"Building index at {server_dir}/index.html ... ")
        f.write("<html><head></head>\n")
        f.write("<h1>Available Videos</h1>\n")
        f.write("<ul>\n")
        for music_file in os.listdir(server_dir):
            if music_file.endswith(".mp3"):
                f.write(f"<li style=\"font-size: 30px; padding-bottom: 10px\"><a href=\"http://wuteri.ch/misc/{music_file}\">{music_file}</a></li>")
        f.write("</ul>\n")
        f.write("</html>")

    log("Done!\n")

def download_video(url):
    cwd = os.getcwd()
    os.chdir(build_dir)
    title = get_title_from_url(url)
    log(f"Downloading video: {title}... ")
    subprocess.run([f"yt-dlp", url, "-o", title], stdout=subprocess.PIPE)
    log("Done!\n")
    video_name = find_processed_file(title)
    log("Converting video to .mp3 ... ")
    subprocess.run([f"ffmpeg", "-i", video_name, f"{title}.mp3"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    log("Done!\n")
    os.chdir(cwd)

def main(video_url):
    print(video_url)
    prepare_dir()
    download_video(video_url)
    move_files()
    make_index()
    cleanup_dir()
    log("Done!\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        log("Expected usage: ./download.py <url>\n")
    else:
        main(sys.argv[1])


