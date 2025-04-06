#!/usr/bin/env python3
#seneca id: jshopkins

import sys
import os
import argparse
import subprocess

def create_backup(target: str, destination: str, compression: int, hash: bool, note: str):
    """
    Responsible: Jonathan Hopkins
    Refactored: Michael Popov
    Function: Creates backup of target file or directory using the tar and gzip.
    Also handles extra steps of creating hash, adding note, and naming the directory as directed by user input
    """

    target = os.path.abspath(target)

    if destination is None:
        destination = os.path.dirname(target)

    if path_exists(target) == False:
        print("Error: Target file/directory does not exist")
        return

    if read_access(target) == False:
        print("Error: Cannot read target file/directory")
        return

    if write_access(destination) == False:
        print("Error: Cannot write to destination directory")
        return
    
    if target[-1:] == "/": #Strips trailing / if passed in as part of target
        target = target[:-1]

    working_dir = cwd(target)

    target_obj = f"{strip_leading_path(target)}"

    destination = create_backup_directory(target,destination)

    backup_dir = subprocess.run(["mkdir", destination]) #makes the directory

    if note:
        add_note(note,destination)

    final_dest = f"{destination}/{target_obj}{tar_or_gz(compression)}"

    backup_process = subprocess.run(["tar", "-czvf", final_dest, target_obj], env={"GZIP":f"-{compression}", **dict(subprocess.os.environ)}, cwd=working_dir)

    print(backup_process.stdout)
    
    if hash:
        create_hash(f"{target_obj}{tar_or_gz(compression)}",destination)

    return

def create_backup_directory(targ: str,dest: str):
    """
    Responsible: Jonathan Hopkins
    Function:Checkes destination directory for folders of the same name that already exsist, iterates through them to find a valid backup directory name
    """
    dir_name = strip_leading_path(targ) 

    copy_num = 0

    while os.path.exists(f"{dest}/{copy_num}-{dir_name}"): #loop for checking if a backup folder of the same already exists
        copy_num += 1
    
    dest = f"{dest}/{copy_num}-{dir_name}/" #assemble full file path for the mkdir command
    
    return dest #return the final directory path to be used by the tar command


def restore_backup(target: str, destination: str):#, compression, hash, note, directory_name):
    """
    Responsible: Michael Popov
    Refactored: Jonathan Hopkins
    Function: Restores a target .tar.gz file to destination
    """ 

    if destination is None:
        destination = os.path.dirname(target)

    if "/" not in target[0]:
        target = os.path.abspath(target)

    restore_name = strip_leading_path(target) 

    restore_name = strip_tar_gz(restore_name) # strips occurences of .tar.gz

    restore_dir = f"{destination}/{restore_name}_restored" # path where restore of backup will be placed

    if not os.access(target,os.F_OK):
        print("Error: Target file does not exist")
        return
    
    if not os.access(target,os.R_OK):
        print("Error: Cannot restore target backup")
        return
    
    if not os.access(destination,os.W_OK):
        print("Error: Cannot restore to destination directory")
        return

    if os.access(restore_dir, os.F_OK):
        print("The file/dir you are trying to restore already exists in the destination directory.")
        tmp_input = input("Would you like to overwrite the existing file, create a new file, or exit? [(o)verwrite/(n)ew/e(x)it]:")
        tmp_input = tmp_input.lower()

        while tmp_input not in ["o","n","x","overwrite","new","exit"]:
            tmp_input = input("Invalid input. Please enter either \"(o)verwrite\", \"(n)ew\", or \"(e)xit\".")
            tmp_input = tmp_input.lower()

        if tmp_input in ["o","overwrite"]:
            backup_process = subprocess.run(["tar", "-xzvf", target], cwd=restore_dir)
            print(backup_process.stdout)
        
        if tmp_input in ["n","new"]:
            restore_name = input("Enter a new directory name: ")
            restore_dir = f"{destination}/{restore_name}_restored"
            while os.access(restore_dir, os.F_OK):
                restore_name = input("Directory already exists, enter a different directory name: ")
                restore_dir = f"{destination}/{restore_name}_restored"

            restore_dir = f"{destination}/{restore_name}_restored" # path where restore of backup will be placed
            subprocess.run(["mkdir", "-p", restore_dir]) # Create directory for restoration
            subprocess.run(["tar", "-xzvf", target, "-C", restore_dir]) # Extract backup to directory
            return
        
        if tmp_input == "exit":
            print("Exiting...")
            exit()
    
    hash_list = check_for_hash(target)

    if len(hash_list) > 0:
        print(f"Hash file {hash_list[0]} is present with backup file.")
        verify_input = input("Would you like to verify file integrity? [y/n]:")
        verify_input = verify_input.lower()

        while verify_input not in ["y","n","no","yes"]:
            verify_input = input("Please enter valid input [y/n]:")
            verify_input = verify_input.lower()

        if verify_input in ["y","yes"]:
            if verify_hash(f"{cwd(target)}{hash_list[0]}") == False:
                cont = input("File integrity is compromised. Would you like to continue with the restore regardless [y/n]:")
                cont = verify_input.lower()
            
                while cont not in ["y","n","no","yes"]:
                    cont = input("Please enter valid input [y/n]:")
                    cont = verify_input.lower()
                
                if cont in ["n","no"]:
                    exit()
                

            
    subprocess.run(["mkdir", "-p", restore_dir]) # Create directory for restoration

    subprocess.run(["tar", "-xzvf", target, "-C", restore_dir]) # Extract backup to directory
    
    print(f"Restored backup to {restore_dir}")

def verify_hash(hash: str):
    """
    Responsible: Roye Chin
    Refactored: Jonathan Hopkins
    Function: Verify file integrity of backup file by comparing it against a hash file.
    """
    verify = subprocess.run(["sha256sum","-c","--quiet",hash], capture_output=True, text=True, cwd=cwd(hash))
    if verify.stderr:
        print(verify.stderr)
        return False
    else:
        print("File integrity confirmed.")
        return True


    """
    hash_file = backup_file + ".hash"

    if not os.path.isfile(backup_file):
        print("Error: Backup file does not exist.")
        return

    if not os.path.isfile(hash_file):
        print("Error: Hash file does not exist.")
        return

    # Read stored hash
    with open(hash_file, "r") as f:
        stored_hash = f.read().strip()

    # Compute current hash
    with open(backup_file, "rb") as f:
        file_data = f.read()
        current_hash = hashlib.sha256(file_data).hexdigest()

    # Compare hashes
    if current_hash == stored_hash:
        print(" Hash matches. Backup is valid.")
    else:
        print(" Hash mismatch. Backup may be corrupted.")
    """


def check_for_hash(targ: str):
    """
    Responsible: Jonathan Hopkins
    Function: checks target directory for all files ending with .sha and returns a list of the file names
    """
    targ = cwd(targ) #use cwd to strip file name from path
    cmd_output = subprocess.run(["ls", targ], capture_output=True, text=True)
    files = cmd_output.stdout.splitlines()
    sha_files = []
    for each in files:
        if each[-7:] == ".sha256":
            sha_files.append(each)
    return sha_files

def create_hash(file_to_hash: str, working_dir: str):
    """
    Responsible: Roye Chin
    Refactored: Jonathan Hopkins
    Function: 
    """

    hash = subprocess.run(["sha256sum", file_to_hash], cwd=working_dir, capture_output=True, text=True)
    
    hash = f"{hash.stdout.split()[0]}  {hash.stdout.split()[1]}"

    hash_file = f"{strip_tar_gz(file_to_hash)}.sha256"

    subprocess.run(["touch", hash_file], cwd=working_dir)

    f = open(f"{working_dir}{hash_file}","w")

    f.write(hash)

    f.close()

    """
    hash = hashlib.sha256()
    with open(target, "rb") as file: # rb = read binary
        while hash.update(file.read(4096)):
            pass 
    hash_file_path = os.path.join(destination, os.path.basename(target) + ".sha256")
    with open(hash_file_path, "w") as hash_file:
        hash_file.write(hash.hexdigest())
    print("Hash file created at", hash)
    """



def add_note(note: str, dest: str):
    """
    Responsible: Rojina Bhandari
    Function: Adds a note to the backup folder
    """
    note_path = os.path.join(dest,"note.txt")
    with open(note_path,"w") as note_file:
        note_file.write(note)
    print (f"Note added to {note_path}")


def strip_leading_path(path: str) -> str:
    """
    Responsible: Jonathan Hopkins
    Function: Returns string following final / in the path
    """
    return path.split("/")[len(path.split("/"))-1]

def cwd(targ: str) -> str:
    """
    Responsible: Jonathan Hopkins
    Function: Create the cwd property for the TAR process so it does not archive the entire filepath.
    """
    while targ[-1:] != "/": #strips characters off the end that aren't a / leaving the path to the parent directory of the target
        targ = targ[:-1]

    return targ

def strip_tar_gz(targ: str):
    """
    Responsible: Jonathan Hopkins
    Function: strips .tar and .gz from the end of a target file. 
    """
    if targ[-3:] == ".gz":
        targ = targ [:-3]
    if targ[-4:] == ".tar":
        targ = targ [:-4]
    return targ

def tar_or_gz(zip: int) -> str:
    """
    Responsible: Jonathan Hopkins
    Function: Return file extension of .tar or .tar.gz depending on compression level
    """
    if zip == 0:
        return ".tar"
    else:
        return ".tar.gz"


def path_exists(path: str) -> bool:
    if not os.access(path,os.F_OK):
        return False
    else:
        return True

def write_access(path: str) -> bool:
    if not os.access(path,os.W_OK):
        return False
    else:
        return True

def read_access(path: str) -> bool:
    if not os.access(path,os.R_OK):
        return False
    else:
        return True

def interactive_menu():
    '''
    Responsible: Shikshya Sharma
    Function: Create an interavtive menu to guide the user through the backup process if agruments are not provided
    '''

    print("\nBackup Utility Menu")
    print("-------------------")
    print("1. Backup")
    print("2. Restore")
    print("3. Verify")
    print("4. Exit")

    
    inter_menu = input("Enter your choice (1–4): ")
    while inter_menu not in ["1","2","3","4"]:
        inter_menu = input("Error: Invalid selection (1–4): ")


    if inter_menu == "1":
        print("\n--- Backup Setup ---")
        
        target = input("Enter the path to file/directory that you to back up: ")
        if target[0:1] == "~":
            target = os.path.expanduser(target)
        while path_exists(target) == False or read_access(target) == False:
            target = input("Invalid path. Please enter a valid file or directory path: ")

        destination = input("Destination directory for the backup: ")
        if destination[0:1] == "~":
            destination = os.path.expanduser(destination)
        while path_exists(destination) == False or write_access(destination) == False:
            destination = input("Invalid directory. Please enter an existing directory: ")

        opt_hash = False
        opt_zip = 6
        opt_note = False
        menu_controller = [0,0,0]

        while menu_controller[2] == 0:
            menu_controller = [0,0,0]
            print("\nAdditional Options:")
            print("-------------------")
            print(f"1. Create Hash: {str(opt_hash)}")
            print(f"2. Compression Level: {opt_zip}")
            print(f"3. Add note: {str(opt_note)}")
            print("4. Proceed")

            menu_controller = backup_opt_menu()
            if menu_controller[0] == 1:
                opt_hash = not opt_hash
            if menu_controller[0] == 2:
                opt_zip = menu_controller[1]
            if menu_controller[0] == 3:
                opt_note = menu_controller[1]
            if menu_controller[0] == 4:
                menu_controller[2] = 1
        
        create_backup(target,destination,opt_zip,opt_hash,opt_note)

    if inter_menu == "2":
        print("\n--- Restore Setup ---")

        target = input("Enter the path to backup you want to restore from: ").strip()
        if target[0:1] == "~":
            target = os.path.expanduser(target)
        while path_exists(target) == False or read_access(target) == False:
            target = input("Invalid path. Please enter a valid file path: ").strip()

        destination = input("Enter the directory you want to restore the backup to: ").strip()
        if destination[0:1] == "~":
            destination = os.path.expanduser(destination)
        while path_exists(destination) == False or write_access(destination) == False:
            destination = input("Invalid directory. Please enter an existing directory: ").strip()

        restore_backup(target,destination)
    
    if inter_menu == "3":
        print("\n--- Verification Setup ---")

        target = input("Enter the path to backup file you want to verify: ").strip()
        if target[0:1] == "~":
            target = os.path.expanduser(target)
        while path_exists(target) == False or read_access(target) == False:
            target = input("Invalid path. Please enter a valid file path: ").strip()
        
        verify_hash(target)

    if inter_menu == "4":
        return



def backup_opt_menu() -> list:
    opt_menu = input("Select additional options, or proceed with backup: ")

    while opt_menu not in ["1","2","3","4"]:
        opt_menu == input("Error: Invalid selection (1–4): ")
    
    if opt_menu == "1":
        return [1,0,0]
    
    if opt_menu == "2":
        hash = input("Please input desire level of compression (0-9): ")
        while hash not in ["0","1","2","3","4","5","6","7","8","9"]:
            hash = input("Error: Invalid selection (0-9): ")
        return [2,hash,0]
    if opt_menu == "3":
        note = input("Enter the note you would like to add to the backup:\n")
        if note:
            return [3,note,0]
        else:
            return [3,False,0]
    if opt_menu == "4":
        return [0,0,4]

    

    




def main():
    """
    Responsible: Jonathan Hopkins
    Function: Parses the arguments provided to assignment2.py
    """

    parser = argparse.ArgumentParser(description="A utility to create or restore backups locally")
    parser.add_argument("target", nargs="?", help="specify the /path/to/target")
    parser.add_argument("destination", nargs="?", help="specify the /path/to/destionation")
    parser.add_argument("-b", "--backup", help="create a backup", action="store_true")
    parser.add_argument("-r", "--restore", help="restore from backup", action="store_true")
    parser.add_argument("-v", "--verify", help="verify backup integrity", action="store_true")
    #parser.add_argument("-d", "--dir", help="name the directory the backup will be stored in")
    #didn't make the cut
    parser.add_argument("--hash", help="create a hash of the backup", action="store_true")
    parser.add_argument("-n", "--note", help="add to the note file")
    parser.add_argument("-z", "--zip", type=int, choices=range(0, 10), help="Compression level (0-9)", default = 6)
    

    args = parser.parse_args()

    if not args.target:
        interactive_menu()
        return
    
    if args.backup:
        create_backup(args.target, args.destination, args.zip, args.hash, args.note)

    if args.restore:
        restore_backup(args.target, args.destination)

    if args.verify:
        verify_hash(args.target)

    else:
        ("specify a valid action")
        return
    
if __name__ == "__main__":
    main()