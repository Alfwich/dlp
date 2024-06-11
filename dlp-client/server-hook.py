#!/usr/bin/python3

import base64
import sys

from download import main as dl_main
from download import log 

if __name__ == "__main__":
    if len(sys.argv) < 3:
        log("Expected usage: ./download-server.py <url> <type> [scope]\n")
    else:
        url = base64.b64decode(sys.argv[1]).decode("utf-8")
        desired_type = base64.b64decode(sys.argv[2]).decode("utf-8")
        scope = base64.b64decode(sys.argv[3]).decode("utf-8") if len(sys.argv) > 3 else ""

        dl_main(url, desired_type, scope)
