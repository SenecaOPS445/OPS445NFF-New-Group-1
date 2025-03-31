#!/usr/bin/env python3
#seneca id: rbhandari17

import os
import argparse
import subprocess

def create_backup(target, destination, compression, dir_name, note):
    if not os.access(target, os.F_OK):
        print("Error: Target directory does not exist")
        return
    
    if not os.access(target, os.R_OK):
        print("Error: Cannot back up specified file/directory")
        return
    
    if not os.access(destination, os.W_OK):
        print("Error: Cannot back up to specified directory")
        return
    
    if target.endswith("/"):
        target = target[:-1]

    working_dir = os.path.dirname(target)
    target_obj = os.path.basename(target)
    destination = create_backup_directory(destination, dir_name or target_obj)

    os.makedirs(destination, exist_ok=True)
    final_dest = os.path.join(destination, f"{target_obj}{tar_or_gz(compression)}")

    subprocess.run(["tar", "-czvf", final_dest, target], env={"GZIP": f"-{compression}"}, cwd=working_dir)

    if note:
        note_path = os.path.join(destination, "note.txt")
        with open(note_path, "w") as note_file:
            note_file.write(note)
        print(f"Note added at {note_path}")

    print(f"Backup created at {final_dest}")

def create_backup_directory(dest, dir_name):
    copy_num = 0
    while os.path.exists(os.path.join(dest, f"{copy_num}-{dir_name}")):
        copy_num += 1
    return os.path.join(dest, f"{copy_num}-{dir_name}")

def tar_or_gz(compression):
    return ".tar" if compression == 0 else ".tar.gz"

def main():
    parser = argparse.ArgumentParser(description="A utility to create backups locally")
    parser.add_argument("target", help="specify the /path/to/target")
    parser.add_argument("destination", help="specify the /path/to/destination")
    parser.add_argument("-b", "--backup", help="create a backup", action="store_true")
    parser.add_argument("-d", "--dir", help="name the directory the backup will be stored in")
    parser.add_argument("-n", "--note", help="add a note to the backup")
    parser.add_argument("-z", "--zip", type=int, choices=range(0, 10), help="Compression level (0-9)", default=6)
    
    args = parser.parse_args()

    if args.backup:
        create_backup(args.target, args.destination, args.zip, args.dir, args.note)
    else:
        print("Specify a valid action")

if __name__ == "__main__":
    main()
