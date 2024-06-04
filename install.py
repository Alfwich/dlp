#!/usr/bin/python3

import os
import subprocess

server_dir = "/www/wuteri.ch/misc"
build_dir = "build"

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

if __name__ == "__main__":
    move_files()
    make_index()


