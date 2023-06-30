import sys
import os
import math
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


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
fileLen = len(file)
user = os.environ.get("USER", default = "marvin")
userLen = len(user)
email = os.environ.get("EMAIL", default = "marvin@student.42.fr") + ">"
emailLen = len(email)

if fileLen > 42:
	print("File name is to long, stripping additionnal characters")
	file = file[:42]
	fileLen = len(file)

if userLen > 10:
	print("User is to long, stripping additionnal characters")
	user = user[:10]
	userLen = len(user)

if emailLen > 25:
	print("Email is to long, stripping additionnal characters")
	email = email[:25]
	emailLen = len(email)


asciiArt = [
	"         :::      ::::::::   */",
	"       :+:      :+:    :+:   */",
	"      +:+ +:+         +:+    */",
	"    +:+ +:+         +:+      */",
	"  +#+  +:+       +#+         */",
	"+#+#+#+#+#+   +#+            */",
	"     #+#    #+#              */",
	"    ###   ########.fr        */"
]

now = datetime.now()

date = now.strftime("%Y/%m/%d")
hour = now.strftime("%H:%M:%S")

headerCreated ="""/* ************************************************************************** */
/*                                                                            */
/*                                               """ + asciiArt[0] +"""
/*""" + 3 * ' ' + file + (42 - fileLen) * ' ' +"""  """ + asciiArt[1] + """
/*                                               """ + asciiArt[2] + """
/*   By: """ + user + """ <""" + email + """""" + (36 - (emailLen + userLen)) * ' ' + """  """ + asciiArt[3] +"""
/*                                               """ + asciiArt[4] + """
/*   Created: """ + str(date) + """ """ + str(hour) + """ by """ + user + (9 - userLen) * ' ' +"""   """ + asciiArt[5] + """
/*   Updated: """ + str(date) + """ """ + str(hour) + """ by """ + user + (9 - userLen) * ' ' +"""   """ + asciiArt[6] + """
/*                                               """ + asciiArt[7] + """
/* ************************************************************************** */
"""

headerModified ="""
/*   Updated: """+ str(date) + """ """ + str(hour) + """ by """ + user + (10 - userLen) * ' ' +"""   """ + asciiArt[6] + """
"""

print(headerCreated)
@dataclass
class NormErrorData:
	type: str
	line: int
	column: int
	message: str

def norminette() -> dict[str, list[NormErrorData]]:
	errors: dict[str, list[NormErrorData]] = {}
	last_error_file: Optional[str] = None

	process = subprocess.Popen(["norminette"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	while True:
		output = process.stdout.readline()
		if output == b"" and process.poll() is not None:
			break
		if output:
			line = output.decode("utf-8").strip()
			# TODO: Notice!
			# Notice: GLOBAL_VAR_DETECTED  (line:   6, col:   1):     Global variable present in file. Make sure it is a reasonable choice.
			if line.startswith("Error: "):
				if last_error_file is None:
					continue

				tokens = [token.strip() for token in line[7:].replace("\t", " ").split(" ") if len(token.strip()) > 0]
				message: str = " ".join(tokens[5:])
				errors[last_error_file].append(
					NormErrorData(
						tokens[0],
						int(tokens[2].split(",")[0]),
						int(tokens[4].split(")")[0]),
						message,
					)
				)
			else:
				if line.endswith("OK!"):
					last_file_errors = None
				elif line.endswith("Error!"):
					last_error_file = line[:-8]
					errors[last_error_file] = []
	return errors

def errors_update():
	global errors
	errors = norminette().get('test.c')

if not list(norminette().items()) == "[]":
	errors_update()

#rreplace
# from https://stackoverflow.com/a/2556252/19549720

def rreplace(str, old, new, occurrence):
	li = str.rsplit(old, occurrence)
	return new.join(li)

def EMPTY_LINE_EOF():

	for e in errors[::-1]:
		if e.type == 'EMPTY_LINE_EOF':
			with open(file, 'r') as f:
				lines = f.readlines()
				del lines[(e.line - 1)]
			with open(file, 'w') as f:
				f.writelines(lines)
	errors_update()


def SPC_BEFORE_NL():

	for e in errors:
		if e.type == 'SPC_BEFORE_NL':
			with open(file, 'r') as f:
				lines = f.readlines()
				lines[e.line - 1] = rreplace(lines[e.line - 1], ' ', '', 1)
			with open(file, 'w') as f:
				f.writelines(lines)
	errors_update()

def INVALID_HEADER():
	for e in errors:
		if e.type == 'INVALID_HEADER':
			with open(file, 'r') as f:
				lines = f.readlines()
				errorLine = list(lines[e.line - 1])
				print(errorLine)
				errorLine[e.column - 1] = errorLine[e.column - 1].replace(' ', '\t')
				lines[e.line - 1] = ''.join(errorLine)
				print(errorLine)
			with open(file, 'w') as f:
				f.writelines(lines)
	errors_update()

# for i in range(0, len(fileContent)):
# 	if fileContent[i] == '\n' and i + 1 < len(fileContent) and fileContent[i + 1] == ' ':
# 		index_to_coordinates(fileContent, i + 1)
# 		print("SPC_INSTEAD_TAB error detected at line " + char_line + " and column " + char_col + "!")
# 		with open(file, 'w') as f :
# 			if fileContent[i + 2] == '\t':
# 				patch = fileContent[:i + 1] + '\t' + fileContent[i + 3:]
# 			else:
# 				patch = fileContent[:i + 1] + '\t' + fileContent[i + 2:]
# 			f.write(patch)
# 			file_update()

# # MIXED_SPACE_TAB

# for i in range(0, len(fileContent)):
# 	if fileContent[i] == '\t' and fileContent[i + 1] == ' ':
# 		index_to_coordinates(fileContent, i + 1)
# 		print("MIXED_SPACE_TAB error detected at line" + char_line + " and column " + char_col + "!")
# 		with open(file, 'w') as f :
# 			patch = fileContent[:i + 1] + fileContent[i + 2:]
# 			while patch[i + 1] == ' ':
# 				patch = patch[:i + 1] + patch[i + 2:]
# 			f.write(patch)
# 			file_update()

# # CONSECUTIVE_SPC

# for i in range(0, len(fileContent) - 1):
# 	if not i >= len(fileContent) and fileContent[i] == ' ' and fileContent[i + 1] == ' ':          #not i >= len(fileContent) and i dont fuckin know why IT GOES FUTHER
# 			index_to_coordinates(fileContent, i)
# 			print("CONSECUTIVE_SPC error detected at line " + char_line + " and column " + char_col +"!")
# 			with open(file, 'w') as f :
# 				j = i + 1
# 				count = 0
# 				while fileContent[j] == ' ':
# 					j += 1
# 					count += 1
# 				patch = fileContent[:i + 1] + fileContent[j:]
# 				f.write(patch)
# 			fileContent = Path(file).read_text()

checks = [
	EMPTY_LINE_EOF,
	SPC_BEFORE_NL,

]

for i in range(0, 10):
	errors_update()
	for c in checks:
		c()