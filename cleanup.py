import platform
import subprocess as sp
import os
import shutil

# Cleans system junk files, adapting to the host OS

# Handling Sudo Passwords
def cmd_with_pw(pw, cmd):
    # Will try running this to bring the other commands that need a sudo password
    try:
        proc = sp.Popen(cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        
        # Write the password to the stdin
        proc.stdin.write(pw.encode() + b"\n")
        proc.stdin.close()
        
        # Wait for the process to finish, capture output
        output, err = proc.communicate()
        
        if proc.returncode == 0:
            return output.decode()
        else:
            raise sp.CalledProcessError(proc.returncode, cmd, output=output, stderr=err)
    except sp.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}: \n{e.stderr.decode()}")
        raise

def junkclean():
    print("Checking for your OS, will run the appropriate cleanup process.")
    os_name = platform.system() # Detects the OS
    
    if os_name == "Linux" or os_name == "Darwin":
        password = input("Please enter your sudo password: ")
    
    if os_name == "Windows":
        del_path = [
            os.path.join(os.environ["SYSTEMDRIVE"], "*.tmp"),
            os.path.join(os.environ["SYSTEMDRIVE"], "*._mp"),
            os.path.join(os.environ["SYSTEMDRIVE"], "*.log"),
            os.path.join(os.environ["SYSTEMDRIVE"], "*.gid"),
            os.path.join(os.environ["SYSTEMDRIVE"], "*.chk"),
            os.path.join(os.environ["SYSTEMDRIVE"], "*.old"),
            os.path.join(os.environ["SYSTEMDRIVE"], "*.old"),
            os.path.join(os.environ["SYSTEMDRIVE"], "recycled", "*.*"),
            os.path.join(os.environ["WINDIR"], "*.bak"),
            os.path.join(os.environ["WINDIR"], "prefetch", "*.*"),
            os.path.join(os.environ["WINDIR"], "temp"),
            os.path.join(os.environ["USERPROFILE"], "cookies", "*.*"),
            os.path.join(os.environ["USERPROFILE"], "recent", "*.*"),
            os.path.join(os.environ["USERPROFILE"], "Local Settings", "Temporary Internet Files", "*.*"),
            os.path.join(os.environ["USERPROFILE"], "Local Settings", "Temp", "*.*"),
            os.path.join(os.environ["USERPROFILE"], "recent", "*.*"),
        ]

        # Delete the files
        for path in del_path:
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    
        # Delete empty directories
        for path in del_path:
            if os.path.isdir(path) and not os.listdir(path):
                os.rmdir(path)
                
        # Run Disk Clean
        sp.run(["cleanmgr.exe"], shell=True)
        
        print("Junk files cleaned and system disk cleaned.")
    elif os_name == "Linux":
        distro = input("Please enter a choice for your distro base: 1 for Debian based (apt), 2 for Fedora (dnf) or 3 for Arch (pacman). Press 4 for none of the above, this will do a default process: \n\n")
        distro = int(distro)
        if distro == 1:
            cmd_with_pw(password, "sudo apt autoremove")
            cmd_with_pw(password, "sudo apt autoremove purge")
            cmd_with_pw(password, "sudo apt clean")
        elif distro == 2:
            cmd_with_pw(password, "sudo dnf autoremove")
            cmd_with_pw(password, "sudo dnf clean")
        elif distro == 3:
            cmd_with_pw(password, "sudo pacman -Rns")
            cmd_with_pw(password, "sudo pacman -Sc")
        
        cmd_with_pw(password, "sudo rm -rf /var/tmp/*") # Clearing temp files
        cmd_with_pw(password, "sudo rm -rf /tmp/*")
        
        cmd_with_pw(password, "sudo logrotate -f /etc/logrotate.conf") # Clearing logs
    elif os_name == "Darwin":
        has_brew = input("Does your system have brew installed? Y/N: ")
        
        if has_brew == "Y" or has_brew == "y":
            brew = True
        else:
            brew = False
            
        if brew:
            sp.run(["brew", "cleanup"], shell=True) # Cleans unused packages
            
        cmd_with_pw(password, "sudo purge") # Cleans temp files
        cmd_with_pw(password, "sudo mdutil -E /Volumes/*") # Cleans logs
        cmd_with_pw(password, "sudo kextcache -invalidate") # Cleans old kernel versions
    else:
        print("Unsupported OS")
    
    print("It may be best to reboot after this process.")
    reboot = input("Would you like to reboot? 1 for yes, 2 for no: ")
    reboot = int(reboot)

    if reboot == 1:
        if os_name == "Windows":
            sp.run(["shutdown", "-r", "-t" "0"], shell=True)
        elif os_name == "Linux":
            cmd_with_pw(password, "sudo reboot")
        elif os_name == "Darwin":
            cmd_with_pw(password, "sudo shutdown -r now")
        
if __name__ == "__main__":
    junkclean()