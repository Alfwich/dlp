#!/usr/bin/python3

import subprocess
import sys
import os
import urllib.request
import json
import urllib


build_dir = "build"
server_dir = "/www/wuteri.ch/misc"

def get_title_from_url(url):
    params = {"format": "json", "url": url}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        print(data['title'])
        return "".join(c for c in data['title'] if c.isalpha() or c.isdigit() or c==' ').rstrip().replace("  ", " ").replace(" ", "-")

def prepare_dir():
    try:
        os.mkdir(build_dir)
    except OSError as error:
        pass

def find_processed_file(name):

    for f in os.listdir("."):
        if f.startswith(f"{name}."):
            return f

def move_files():
    for f in os.listdir(build_dir):
        if f.endswith(".mp3"):
            subprocess.run(["cp", f"{build_dir}/{f}", f"{server_dir}/{f}"])

def make_index():
    index_lines = []
    for f in os.listdir(server_dir):
        if f.endswith(".mp3"):
            index_lines.append(f"<li style=\"font-size: 30px; padding-bottom: 10px\"><a href=\"http://wuteri.ch/misc/{f}\">{f}</a></li>")

    with open(f"{server_dir}/index.html", "w") as f:
        f.write("<html><head></head>\n")
        f.write("<h1>Available Videos</h1>\n")
        f.write("<ul>\n")
        for line in index_lines:
            f.write(line)
        f.write("</ul>\n")
        f.write("</html>")

def download_video(url):
    prepare_dir()
    cwd = os.getcwd()
    os.chdir(build_dir)
    title = get_title_from_url(url)
    print(f"Downloading video: {title}")
    subprocess.run([f"yt-dlp", url, "-o", title])
    video_name = find_processed_file(title)
    print("Converting video to .mp3")
    subprocess.run([f"ffmpeg", "-i", video_name, f"{title}.mp3"])
    print(f"Video downloaded in build/{title}.mp3")
    os.chdir(cwd)


if __name__ == "__main__":
    if len(sys.argv) < 2 or not os.geteuid() == 0:
        print("Expected usage: sudo ./download.py <url>")
    else:
        download_video(sys.argv[1])
        move_files()
        make_index()

