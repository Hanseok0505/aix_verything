import argparse
from app.db import init_db
from app.indexer import index_folder

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    args = ap.parse_args()
    init_db()
    print(index_folder(args.root))

if __name__ == "__main__":
    main()
