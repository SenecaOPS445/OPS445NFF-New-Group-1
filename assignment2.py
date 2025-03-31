#!/usr/bin/env python3
#seneca id: jshopkins

import sys
import os
import argparse
import subprocess

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
    
    if target[-1:] == "/": #Strips trailing / if passed in as part of target
        target = target[:-1]

    working_dir = cwd(target)

    target_obj = strip_leading_path(target)

    destination = create_backup_directory(target,destination)

    create_backup_dir = subprocess.run(["mkdir", destination]) #makes the directory

    final_dest = destination + target_obj + tar_or_gz(compression)

    backup_process = subprocess.run(["tar", "-czvf", final_dest, target_obj], env={"GZIP":"-"+str(compression), **dict(subprocess.os.environ)}, cwd=working_dir)

    print(backup_process.stdout)
    
    return

def create_backup_directory(targ,dest):
    "Checkes destination directory for folders of the same name that already exsist, iterates through them to find a valid backup directory name"    
    dir_name = strip_leading_path(targ) 

    copy_num = 0

    while os.path.exists(str(dest) + "/" + str(copy_num) + "-" + str(dir_name)): #loop for checking if a backup folder of the same already exists
        copy_num += 1

    dir_name = str(copy_num) + "-" + dir_name # creates the folder name with the format #-target
    
    dest = dest + str("/") + dir_name  + str("/") #assemble full file path for the mkdir command
    
    return dest #return the final directory path to be used by the tar command

def strip_leading_path(path):
    "Returns string following final / in the path"
    return path.split("/")[len(path.split("/"))-1]

def cwd(targ):
    "Create the cwd property for the TAR process so it does not archive the entire filepath."
    while targ[-1:] != "/": #strips characters off the end that aren't a / leaving the path to the parent directory of the target
        targ = targ[:-1]

    return targ

def tar_or_gz(zip):
    "properly sets file extension as .tar or .tar.gz depending on compression level"
    if zip == 0:
        return ".tar"
    else:
        return ".tar.gz"

def file_or_dir(targ):
    if os.path.isfile(targ):
        return "P"
    if os.path.isdir(targ):
        return "D"


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

    if os.access(destination + strip_leading_path(strip_tar_gz(target)), os.F_OK):
        print("The file/dir you are trying to restore already exists in the destination directory.")
        tmp_input = input("Would you like to overwrite the existing file, or create a new file? [overwrite/new]:")
        tmp_input = tmp_input.lower()
        while tmp_input != "overwrite" and tmp_input != "new":
            tmp_input = input("Invalid input. Please enter either \"overwrite\" or \"new\", or press ctrl+c to exit script:")
            tmp_input = tmp_input.lower()

        if tmp_input == "overwrite":
            backup_process = subprocess.run(["tar", "-xzvf", target], cwd=destination)
            print(backup_process.stdout)
        
        if tmp_input == "new":
            return()
        
    restore_name = strip_leading_path(target) 

    restore_name = restore_name.replace('.tar.gz', '') # strips occurences of .tar.gz

    restore_name = restore_name.replace('.tar', '') # strips occurences of .tar 

    restore_dir = destination + restore_name + "_restored" # path where restore of backup will be placed
    
    subprocess.run(["mkdir", "-p", restore_dir]) # Create directory for restoration

    backup_process = subprocess.run(["tar", "-xzvf", target, "-C", restore_dir]) # Extract backup to directory
    
    print(f"Restored backup to {restore_dir}")

def strip_tar_gz(targ):
        if targ[-3:] == ".gz":
            targ = targ [:-3]
        if targ[:-4] == ".tar":
            targ = targ [:-4]
        return targ

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