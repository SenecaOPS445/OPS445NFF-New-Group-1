#!/usr/bin/env python3
#seneca id: jshopkins

import sys
import os
import argparse
import subprocess
import hashlib
def create_backup(target, destination, compression):# hash, note, directory_name):
    if not os.access(target,os.F_OK):
        print("Error: Target directory does not exist")
        return
    
    if not os.access(target,os.R_OK):
        print("Error: Cannot back up specified file/directory")
        return
    
    if not os.access(destination,os.W_OK):
        print("Error: Cannot back up to specified directory")
        return
    
    
    dir_name = target.split("/")[len(target.split("/"))-1]

    #working_directory = target - dir_name #need to remove the target from the full directory path to get a cwd variable for subprocess.os

    copy_num = 1

    if os.path.exists(str(destination)+str(dir_name)): #loop for checking if a backup folder already exists
        while os.path.exists(str(destination) + str(copy_num) + "-" + str(dir_name)):
            copy_num += 1
        dir_name = str(copy_num) + "-" + dir_name
    
    destination = destination + str("/") + dir_name  + str("/")
    
    
    create_backup_dir = subprocess.run(["mkdir", destination])

    create_hash(target, destination)
    
    final_dest = destination + target.split("/")[len(target.split("/"))-1]
    
    if compression == 0:
        final_dest = final_dest + str(".tar")
    else:
        final_dest = final_dest + str(".tar.gz")

    backup_process = subprocess.run(["tar", "-czvf", final_dest, target], env={"GZIP":"-"+str(compression), **dict(subprocess.os.environ)})
    print(backup_process.stdout)
    return


def create_hash(target, destination):
    hash = hashlib.sha256()
    with open(target, "rb") as file: # rb = read binary
        while hash.update(file.read(4096)):
            pass 
    hash_file_path = os.path.join(destination, os.path.basename(target) + ".sha256")
    with open(hash_file_path, "w") as hash_file:
        hash_file.write(hash.hexdigest())
    print("Hash file created at", hash)  
    

def verify_backup(target, hash):
    if not os.access(target,os.F_OK):
        print("Error: Target file does not exist")
        return
    
    if not os.access(target,os.R_OK):
        print("Error: Cannot verify target backup")
        return

    if hash == create_hash(target):
        print("Backup is verified")
    else:
        print("Backup is not verified")
    return


def restore_backup(target, destination):#, compression, hash, note, directory_name):
    if not os.access(target,os.F_OK):
        print("Error: Target file does not exist")
        return
    
    if not os.access(target,os.R_OK):
        print("Error: Cannot restore target backup")
        return
    
    if not os.access(destination,os.W_OK):
        print("Error: Cannot restore to destination directory")
        return


    backup_process = subprocess.run(["tar", "-xzvf",destination, target])
    print(backup_process.stdout)


def main():
    parser = argparse.ArgumentParser(description="A utility to create or restore backups locally")
    parser.add_argument("target", nargs="?", help="specify the /path/to/target")
    parser.add_argument("destination", nargs="?", help="specify the /path/to/destionation")
    parser.add_argument("-b", "--backup", help="create a backup", action="store_true")
    parser.add_argument("-r", "--restore", help="restore from backup", action="store_true")
    parser.add_argument("-v", "--verify", help="verify backup integrity", action="store_true")
    parser.add_argument("-d", "--dir", help="name the directory the backup will be stored in", action="store_true")
    parser.add_argument("--hash", help="create a hash of the backup", action="store_true")
    parser.add_argument("-n", "--note", help="add to the note file", action="store_true")
    parser.add_argument("-z", "--zip", type=int, choices=range(0, 10), help="Compression level (0-9)", default = 6)
    

    args = parser.parse_args()

    if not args.target:
        print("Create an interactive menu")
        return
    
    if args.backup:
        create_backup(args.target, args.destination, args.zip)

    if args.restore:
        restore_backup(args.target, args.destination)

    else:
        ("specify a valid action")
        return

        
if __name__ == "__main__":
    main()
