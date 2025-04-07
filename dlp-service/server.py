#!/usr/bin/python3

import subprocess
import multiprocessing as mp
import os
import sys
import shutil
import time

from datetime import datetime

dlp_directory = "/www/dlp-client"
web_server_dir = "/www/wuteri.ch/dlp"
web_server_ingest_dir = f"{web_server_dir}/ingest"


def log(msg):
    preamble = f"[{datetime.now().strftime('%H:%M:%S:%f')}]"
    sys.stdout.write(f"{preamble} {msg}")
    sys.stdout.flush()


def exec_cmd(cmd, data, writer):
    pretty_cmd = " ".join(cmd)
    log(f"Executing command: {pretty_cmd}, data: {data}\n")
    subprocess.run(cmd, input=data, stdout=writer, stderr=writer)


def worker_proc(q):
    os.chdir(web_server_dir)
    while True:
        data = q.get()

        if data == "quit":
            return

        log(f"Starting job id: {data[0]}\n")
        os.mkdir(f"{web_server_dir}/processing/{data[0]}")
        with open(f"{web_server_dir}/processing/{data[0]}/log.txt", "wb") as writer:
            exec_cmd(["python3", f"{dlp_directory}/server-hook.py"], data[1], writer)

        with open(f"{web_server_dir}/processing/{data[0]}/done", "wb") as writer:
            writer.write(bytes("1", "utf-8"))

        log(f"Finished job id: {data[0]}\n")

        # cleanup after allowing loading agent to read
        time.sleep(5)

        shutil.rmtree(f"{web_server_dir}/processing/{data[0]}")


if __name__ == "__main__":
    ctx = mp.get_context('spawn')
    queue = ctx.Queue()

    workers = []
    for i in range(3):
        worker = ctx.Process(target=worker_proc, args=(queue,))
        worker.start()
        workers.append(worker)

    print("Starting main loop")
    while True:
        print("Checking for ingest files")
        ingest_files = os.listdir(web_server_ingest_dir)
        for f in ingest_files:
            full_file_name = f"{web_server_ingest_dir}/{f}"
            print(f"Found ingest file {f}")
            with open(full_file_name, 'rb') as in_file:
                job_id = f
                data = in_file.read()
                print(f"    Started job {job_id}, with data: {data}")
                queue.put((job_id, data))

            os.remove(full_file_name)
        time.sleep(5)
