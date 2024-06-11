#!/usr/bin/python3

import hashlib
import random
import json
import subprocess
import multiprocessing as mp
import os
import json
import sys
import base64
import shutil
import time

from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

dlp_directory = "/usr/www/yt-download"
web_server_dir = "/www/wuteri.ch/dlp"

def log(msg):
    preamble = f"[{datetime.now().strftime('%H:%M:%S:%f')}]"
    sys.stdout.write(f"{preamble} {msg}")
    sys.stdout.flush()

def exec_cmd(cmd, writer):
    pretty_cmd = " ".join(cmd)
    log(f"Executing command: {pretty_cmd}\n")
    subprocess.run(cmd, stdout=writer, stderr=writer)

def worker_proc(q):
    os.chdir(web_server_dir)
    while True:
        data = q.get()

        if data is "quit":
            return

        payload = json.loads(data[1][1:])

        url = payload["url"];
        desired_type = payload["type"]
        scope = payload["scope"]

        log(f"Starting job id: {data[0]}\n")
        os.mkdir(f"{web_server_dir}/processing/{data[0]}")
        with open(f"{web_server_dir}/processing/{data[0]}/log.txt", "wb") as writer:
            exec_cmd(["python3", f"{dlp_directory}/server-hook.py", url, desired_type, scope], writer)

        with open(f"{web_server_dir}/processing/{data[0]}/done", "wb") as writer:
            writer.write(bytes("1", "utf-8"))

        log(f"Finished job id: {data[0]}\n")

        # cleanup after allowing loading agent to read
        time.sleep(5)

        shutil.rmtree(f"{web_server_dir}/processing/{data[0]}")

def get_next_id():
    result = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
    return result[:15]

class Server:
    ctx = None
    queue = None
    workers = [] 

    def __init__(self):
        self.ctx = mp.get_context('spawn')
        self.queue = self.ctx.Queue()
        for i in range(3):
            self.workers.append(self.ctx.Process(target=worker_proc, args=(self.queue,)))

        for worker in self.workers:
            worker.start()

    def __del__(self):
        for worker in self.workers:
            self.queue.put("quit")

        for worker in self.workers:
            worker.join()

    def do_work(self, job_id, data):
        self.queue.put((job_id, data))

class Serv(BaseHTTPRequestHandler):
    def do_GET(self):
        job_id = get_next_id()
        server.do_work(job_id, self.path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(job_id, "utf-8"))

if __name__ == "__main__":
    global server
    server = Server()
    config = ('localhost', 4141)
    print(f"Serving on {config}")
    httpd = HTTPServer(config, Serv)
    httpd.serve_forever()
