import sys
import os
from pathlib import Path
import math

char_line = 0
char_col = 0

argsN = len(sys.argv) - 1

if argsN > 1:
	print("This command cannot take more than 1 argument!")
	exit(0)

if argsN == 0:
	print("This command takes a file as argument!")
	exit(0)

if not os.path.isfile(sys.argv[1]):
	print("This is not a file!")
	exit(0)

file = sys.argv[1]
fileContent = Path(file).read_text()
cols = 0
lines = 0

def file_update():
	NLs = 0
	global cols
	global lines

	for i in range(0, len(fileContent)):
		NLs += 1
		if NLs > cols:
			cols = NLs
		if fileContent[i] == '\n':
			NLs = 0
			lines += 1

	lines += 1


file_update()

# Conversion of index to coordinates
# from https://stackoverflow.com/a/66443805/19549720

def index_to_coordinates(s, index):
	global char_line
	global char_col
	if not len(s):
		return 1, 1
	sp = s[:index+1].splitlines(keepends=True)
	char_line = str(len(sp))
	char_col = str(len(sp[-1]))

# Empty EOF

for i in range(0, len(fileContent)):
	if i == len(fileContent) - 1:
		if fileContent[i] == '\n':
			index_to_coordinates(fileContent, i)
			print("Empty EOF error detected at line " + char_line + " and column " + char_col +"!")
			with open(file, 'w') as f :
				patch = fileContent[:i] + fileContent[i + 1:]
				i -= 1
				while patch[i] == '\n':
					patch = patch[:i] + patch[i + 1: ]
					i -= 1
				f.write(patch)
				file_update()

# Space before NewLine

for i in range(0, len(fileContent)):
	if fileContent[i] == '\n':
		if fileContent[i - 1] == ' ':
			index_to_coordinates(fileContent, i - 1)
			print("Space Before NewLine error detected at line " + char_line + " and column " + char_col +"!")
			with open(file, 'w') as f :
				patch = fileContent[:i - 1] + fileContent[i:]
				i -= 1
				while patch[i - 1] == ' ':
					patch = patch[:i - 1] + patch[i:]
					i -= 1
				f.write(patch)
				file_update()

# Multiple Spaces

for i in range(0, len(fileContent)):
	if fileContent[i] == ' ':
		if fileContent[i + 1] == ' ':
			index_to_coordinates(fileContent, i + 1)
			print("Multiple Space error detected at line " + char_line + " and column " + char_col +"!")
			with open(file, 'w') as f :
				patch = fileContent[:i + 1] + fileContent[i + 2:]
				while patch[i + 1] == ' ':
					# print(patch[i + 1] == ' ')
					# does not patch all the way idk why
					patch = patch[:i + 1] + patch[i + 2:]
				f.write(patch)
				file_update()