import os
import signal
import sys
import subprocess
from fart.commands import create
import pty


# output_bytes = []

# def read(fd):
#     data = os.read(fd, 1024)
#     output_bytes.append(data)
#     return data

# pty.spawn(["fart", "check"], read)
# output = str(output_bytes).pty.spawn("")

def print(o: object, flush: bool = False, end: str = "\n") -> None:
	sys.__stdout__.write(str(o) + end)
	if flush: sys.__stdout__.flush()
# print(output)

def signal_handler(signal_number, frame):
	cols = os.get_terminal_size().columns
	sys.__stdout__.write("\r" + " " * cols + "\r" + "\033[2J" + "\033[0;0H" + "\033[?25h")
	sys.__stdout__.flush()
	exit(0)

def watch(_, __):

	signal.signal(signal.SIGINT, signal_handler)

	#replace to info
	print("\n"*4, flush=False)
	print("\033[2J\033[0;0Hrunning")
	print("\033[?25l")

	while True:
		process = subprocess.run(["fart", "check"], capture_output=True)
		sys.__stdout__.write("\033[0;0H")
		print("\n"*4, flush=False)
		print(process.stdout.decode(), flush=False)
		print("\033[0J")
		sys.__stdout__.flush()

create("watch", "watch the fart checks command", lambda _: None, watch)
