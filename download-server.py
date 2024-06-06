#!/usr/bin/python3

import base64
import sys
from download import main as dl_main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        log("Expected usage: ./download.py <url>\n")
    else:
        dl_main(base64.b64decode(sys.argv[1]))
