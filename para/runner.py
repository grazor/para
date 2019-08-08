import logging
import shlex
import subprocess
from threading import Thread


class CommandThread(Thread):
    def __init__(self, command, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command = command

    def run(self):
        logging.info(f'Running command {self.command}')
        args = shlex.split(self.command)
        self.process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(f'Finished command {self.command}')

    def stop(self):
        if self.process:
            self.process.stop()


def run_command(command):
    thread = CommandThread(command)
    thread.run()
    return thread
