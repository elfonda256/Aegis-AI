#!/usr/bin/env python3
import os
import sys
import pty
import select
import subprocess
import time

HOST = os.environ.get("SERVER_HOST", "103.56.206.89")
USER = os.environ.get("SERVER_USER", "efi")
PASS = os.environ.get("SERVER_PASS", "")

def run_remote(cmd, sudo=False):
    if sudo:
        remote_cmd = f"echo {PASS} | sudo -S {cmd}"
    else:
        remote_cmd = cmd

    ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", f"{USER}@{HOST}", remote_cmd]
    
    master, slave = pty.openpty()
    proc = subprocess.Popen(
        ssh_cmd,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        close_fds=True
    )
    os.close(slave)
    
    output = []
    password_sent = False
    
    while True:
        r, _, _ = select.select([master], [], [], 1.0)
        if master in r:
            try:
                data = os.read(master, 1024)
            except OSError:
                break
            if not data:
                break
            text = data.decode("utf-8", errors="replace")
            output.append(text)
            if "password:" in text.lower() and not password_sent:
                os.write(master, (PASS + "\n").encode())
                password_sent = True
        elif proc.poll() is not None:
            # Check remaining output
            try:
                while True:
                    data = os.read(master, 1024)
                    if not data:
                        break
                    output.append(data.decode("utf-8", errors="replace"))
            except OSError:
                pass
            break
            
    os.close(master)
    proc.wait()
    full_output = "".join(output)
    return proc.returncode, full_output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: remote_exec.py [--sudo] <command>")
        sys.exit(1)
    
    is_sudo = False
    args = sys.argv[1:]
    if args[0] == "--sudo":
        is_sudo = True
        args = args[1:]
    
    cmd = " ".join(args)
    code, out = run_remote(cmd, sudo=is_sudo)
    print(out)
    sys.exit(code)
