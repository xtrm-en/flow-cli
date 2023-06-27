import os
import signal
import time
import sys
import subprocess

def signal_handler(signal_number, frame):
	exit(0)

signal.signal(signal.SIGINT, signal_handler)

#replace to info
print("\n"*4, flush=False)
print("\033[2J\033[0;0Hrunning")

while True:
	process = subprocess.run(["fart", "check"], capture_output=True)
	sys.__stdout__.write("\033[0;0H")
	print("\n"*4, flush=False)
	print(process.stdout.decode(), flush=False)
	sys.__stdout__.flush()