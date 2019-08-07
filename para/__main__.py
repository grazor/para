import argparse
import logging
import os
import daemon
from pathlib import Path

from para import Category, monitor

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
run_parser.add_argument('--sync-command', type=str, default=None, help='A command to mount a remote drive')
run_parser.add_argument('--preview-command', type=str, default=None, help='A command to run markdown server')
run_parser.add_argument('--daemonize', '-d', action='store_true', help='Run in the background')
run_parser.add_argument('path', type=lambda p: Path(p), nargs='?', default=os.getcwd(), help='Path of kdb root')

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
                monitor(path=args.path, name=args.title)
        else:
            monitor(path=args.path, name=args.title)
