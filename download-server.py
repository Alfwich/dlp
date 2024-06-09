#!/usr/bin/python3

import base64
import sys
from download import main as dl_main

def log(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        log("Expected usage: ./download-server.py <url> <type>\n")
    else:
        url = base64.b64decode(sys.argv[1]).decode("utf-8")
        desired_type = base64.b64decode(sys.argv[2]).decode("utf-8")

        dl_main(url, desired_type)
