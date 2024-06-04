#!/usr/bin/python3

import os
import subprocess

server_dir = "/www/wuteri.ch/misc"
build_dir = "build"

# http://wuteri.ch/misc/chasing-the-sunshine.mp3

if __name__ == "__main__":
    for f in os.listdir(build_dir):
        if f.endswith(".mp3")
            subprocess.run(["mv", f, f"{server_dir}/{f}"])


