import argparse
import logging
import os
import time
from pathlib import Path

import daemon

from para import Category, monitor, run_command

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest='command', required=True)

clean_parser = subparsers.add_parser('clean')

index_parser = subparsers.add_parser('index', help='Create index files')
index_parser.add_argument('--title', type=str, default='Para', help='Kdb title')
index_parser.add_argument('path', type=lambda p: Path(p), nargs='?', default=os.getcwd(), help='Path of kdb root')

clean_parser = subparsers.add_parser('clean', help='Remove index files')
clean_parser.add_argument('path', type=lambda p: Path(p), nargs='?', default=os.getcwd(), help='Path of kdb root')

run_parser = subparsers.add_parser('run', help='Run as para as service')
run_parser.add_argument('--title', type=str, default='Para', help='Kdb title')
run_parser.add_argument('--on-start', type=str, action='append', help='Commands to run on start')
run_parser.add_argument('--on-stop', type=str, action='append', help='Commands to run on stop')
run_parser.add_argument('--daemonize', '-d', action='store_true', help='Run in the background')
run_parser.add_argument('path', type=lambda p: Path(p), nargs='?', default=os.getcwd(), help='Path of kdb root')


def run_monitor(args):
    active = []
    active.append(monitor(path=args.path, name=args.title))
    active.extend(run_command(command) for command in args.on_start or [])

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('Interrupt')
        (thread.stop() for thread in active if thread.is_alive())

    active.extend(run_command(command, sync=True) for command in args.on_stop or [])
    (thread.join() for thread in active)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.command in ('index', 'run'):
        root = Category.scan(path=args.path, name=args.title)
        root.render_indexes()

    if args.command == 'clean':
        root = Category.scan(path=args.path)
        root.remove_indexes()

    if args.command == 'run':
        if args.daemonize:
            with daemon.DaemonContext():
                run_monitor(args)
        else:
            run_monitor(args)
