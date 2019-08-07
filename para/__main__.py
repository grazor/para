import argparse
import os
from pathlib import Path

from para import Category

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest='command', required=True)

clean_parser = subparsers.add_parser('clean')

index_parser = subparsers.add_parser('index')
index_parser.add_argument('--title', type=str, default='Para', help='Kdb title')
index_parser.add_argument('path', type=lambda p: Path(p), nargs='?', default=os.getcwd(), help='Path of kdb root')

clean_parser = subparsers.add_parser('clean')
clean_parser.add_argument('path', type=lambda p: Path(p), nargs='?', default=os.getcwd(), help='Path of kdb root')

if __name__ == "__main__":
    args = parser.parse_args()

    if args.command == 'index':
        root = Category.scan(path=args.path, name=args.title)
        root.render_indexes()
    if args.command == 'clean':
        root = Category.scan(path=args.path)
        root.remove_indexes()
