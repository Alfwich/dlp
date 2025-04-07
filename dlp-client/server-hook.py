#!/usr/bin/python3

import base64
import sys
import json

from download import main_payload as dl_main_payload
from download import log

if __name__ == "__main__":
    if len(sys.argv) > 1:
        log("Expected usage: cat input.json | ./download-server.py\n")
    else:
        json_payload = ""
        for line in sys.stdin:
            json_payload += line
        args = json.loads(json_payload)

        for k in args:
            args[k] = base64.b64decode(args[k]).decode("utf-8")

        dl_main_payload(args)
