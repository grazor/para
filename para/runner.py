import logging
import shlex
import subprocess
from threading import Thread


class CommandThread(Thread):
    def __init__(self, command, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command = command

    def run(self):
        logging.info(f"Running command {self.command}")
        args = shlex.split(self.command)
        self.process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        if self.process:
            self.process.stop()
        logging.info(f"Finished command {self.command}")


def run_sync(command):
    logging.info(f"Running command {command}")
    args = shlex.split(command)
    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    logging.info(f"Finished command {command}")


def run_command(command, sync=False):
    if sync:
        thread = Thread(target=run_sync, args=(command,))
    else:
        thread = CommandThread(command)
    thread.run()
    return thread
