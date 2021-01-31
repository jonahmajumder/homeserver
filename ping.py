import os
import sys
import subprocess

def ping(ip, count=1, timeout=1):
    cmdargs = ['ping', ip, '-c', str(count), '-t', str(timeout)]
    return subprocess.run(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)