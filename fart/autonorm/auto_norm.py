import sys
import os
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

email = os.environ.get("EMAIL", default = "marvin@student.42.fr")
emailLen = len(email)

usermail = user + " <" + email + ">"
usermailLen = len(usermail)

if fileLen > 42:
	print("File name is to long, stripping additionnal characters")
	file = file[:42]
	fileLen = len(file)

if usermailLen > 36:
	print("User and mail is to long, stripping additionnal characters")
	usermail = usermail[:36]

if userLen > 10:
	print("User is too long, stripping additionnal characters")
	user = user[:10]

asciiArt = [
		"        :::      ::::::::    */",
		"      :+:      :+:    :+:    */",
		"    +:+ +:+         +:+      */",
		"  +#+  +:+       +#+         */",
		"+#+#+#+#+#+   +#+            */",
		"     #+#    #+#              */",
		"    ###   ########.fr        */"
]

now = datetime.now()

date = now.strftime("%Y/%m/%d")
hour = now.strftime("%H:%M:%S")

global headerCreated



headerCreated ="""/* ************************************************************************** */
/*                                                                            */
/*                                               """ + asciiArt[0] +"""
/*""" + 3 * ' ' + file + (42 - fileLen) * ' ' +"""  """ + asciiArt[1] + """
/*                                               """ + asciiArt[2] + """
/*   By: """ + usermail + """  """ + (36 - usermailLen) * ' ' + """  """ + asciiArt[3] +"""
/*                                               """ + asciiArt[4] + """
/*   Created: """ + str(date) + """ """ + str(hour) + """ by """ + user + (10 - userLen) * ' ' +"""  """ + asciiArt[5] + """
/*   Updated: """ + str(date) + """ """ + str(hour) + """ by """ + user + (10 - userLen) * ' ' +"""  """ + asciiArt[6] + """
/*                                                                            */
/* ************************************************************************** */
"""

global headerModified

headerModified ="""
/*   Updated: """+ str(date) + """ """ + str(hour) + """ by """ + user + (10 - userLen) * ' ' +"""   """ + asciiArt[6] + """
"""

@dataclass
class NormErrorData:
	type: str
	line: int
	column: int
	message: str


def norminette() -> dict[str, list[NormErrorData]]:
	errors: dict[str, list[NormErrorData]] = {}
	last_error_file: Optional[str] = None

	process = subprocess.Popen(["norminette.py"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
	result: dict[str, list[NormErrorData]] = norminette()
	errors = result[file] if file in result else []

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

def SPC_BEFORE_NL():

	for e in errors:
		if e.type == 'SPC_BEFORE_NL':
			with open(file, 'r') as f:
				lines = f.readlines()
				lines[e.line - 1] = rreplace(lines[e.line - 1], ' ', '', 1)
			with open(file, 'w') as f:
				f.writelines(lines)

def INVALID_HEADER():

	for e in errors:
		if e.type == 'INVALID_HEADER':
			with open(file, 'r') as f:
				txt = f.read()
			with open(file, 'w') as f:
				f.write(headerCreated)
			with open(file, 'a') as f:
				f.write('\n' + txt)

def BRACE_SHOULD_EOL():

	for e in errors:
		if e.type == 'BRACE_SHOULD_EOL':
			with open(file, 'r') as f:
				lines = f.readlines()
				lines[e.line - 1] = lines[e.line - 1] + '\n'
			with open(file, 'w') as f:
				f.writelines(lines)

def SPACE_BEFORE_FUNC():

	for e in errors:
		if e.type == 'SPACE_BEFORE_FUNC':
			with open(file, 'r') as f:
				lines = f.readlines()
				lines[e.line - 1] = lines[e.line - 1][:e.column - 1] + '\t' + lines[e.line - 1][e.column:]
			with open(file, 'w') as f:
				f.writelines(lines)

def RETURN_PARENTHESIS():

	for e in errors:
		if e.type == 'RETURN_PARENTHESIS':
			with open(file, 'r') as f:
				lines = f.readlines()
				n = lines[e.line - 1 ].find('n')
				lines[e.line - 1] = lines[e.line - 1][:n + 1] + ' (' + lines[e.line - 1][n + 2:]
				semicolon = lines[e.line - 1 ].find(';')
				lines[e.line - 1] = lines[e.line - 1][:semicolon] + ')' + lines[e.line - 1][semicolon:]
			with open(file, 'w') as f:
				f.writelines(lines)

def SPACE_REPLACE_TAB():
	for e in errors:
		if e.type == 'SPACE_REPLACE_TAB':
			with open(file, 'r') as f:
				lines = f.readlines()
				target = lines[e.line- 1]
				first_char = target.strip()[0]
				first_char_index = target.index(first_char)
				if first_char_index != 0 and lines[e.line - 1][0] != '\t' and lines[e.line - 1][0] == ' ':
					lines[e.line - 1] = '\t' + lines[e.line - 1][first_char_index:]
				elif lines[e.line - 1][0] == '\t':
					lines[e.line - 1] = lines[e.line - 1][:e.column - 4] + '\t' + lines[e.line - 1][e.column - 3:]
				else:
					lines[e.line - 1] = lines[e.line - 1][:e.column - 1] + '\t' + lines[e.line - 1][e.column:]
			with open(file, 'w') as f:
				f.writelines(lines)
			break

def NL_AFTER_VAR_DECL():
	for e in errors:
		if e.type == 'NL_AFTER_VAR_DECL':
			with open(file, 'r') as f:
				lines = f.readlines()
				lines[e.line - 2] = lines[e.line - 2] + '\n'
			with open(file, 'w') as f:
				f.writelines(lines)

def NL_AFTER_PREPROC():
	for e in errors:
		if e.type == 'NL_AFTER_PREPROC':
			with open(file, 'r') as f:
				lines = f.readlines()
				lines[e.line - 2] = lines[e.line - 2] + '\n'
			with open(file, 'w') as f:
				f.writelines(lines)

def NEWLINE_PRECEDES_FUNC():
	for e in errors:
		if e.type == 'NEWLINE_PRECEDES_FUNC':
			with open(file, 'r') as f:
				lines = f.readlines()
				lines[e.line - 2] = lines[e.line - 2] + '\n'
			with open(file, 'w') as f:
				f.writelines(lines)

def NO_ARGS_VOID():
	for e in errors:
		if e.type == 'NO_ARGS_VOID':
			with open(file, 'r') as f:
				lines = f.readlines()
				first_parenthesis = lines[e.line - 1].find('(')
				second_parenthesis = lines[e.line - 1].find(')')
				lines[e.line - 1] = lines[e.line - 1][:first_parenthesis] + "(void" + lines[e.line - 1][second_parenthesis:]
			with open(file, 'w') as f:
				f.writelines(lines)

def CONSECUTIVE_SPC():
	for e in errors:
		if e.type == 'CONSECUTIVE_SPC':
			with open(file, 'r') as f:
				lines = f.readlines()
				tab_count = lines[e.line - 1].count('\t')
				e.column -= tab_count * 4
				lines[e.line - 1] = lines[e.line - 1][:e.column] + lines[e.line - 1][e.column + 1:]
			with open(file, 'w') as f:
				f.writelines(lines)

def SPC_BFR_OPERATOR():
	for e in errors:
		if e.type == 'SPC_BFR_OPERATOR':
			with open(file, 'r') as f:
				lines = f.readlines()
				tab_count = lines[e.line - 1].count('\t')
				e.column -= tab_count * 4
				lines[e.line - 1] = lines[e.line - 1][:e.column] + lines[e.line - 1][e.column] + ' ' + lines[e.line - 1][e.column + 1:]
				lines[e.line - 1] = lines[e.line - 1][:e.column - 1] + lines[e.line - 1][e.column - 1] + ' ' + lines[e.line - 1][e.column:]
			with open(file, 'w') as f:
				f.writelines(lines)

def TOO_FEW_TAB():
	for e in errors:
		if e.type == 'TOO_FEW_TAB':
			with open(file, 'r') as f:
				lines = f.readlines()
				lines[e.line - 1] = '\t' + lines[e.line - 1]
			with open(file, 'w') as f:
				f.writelines(lines)

def TOO_MANY_TAB():
	for e in errors:
		if e.type == 'TOO_MANY_TAB':
			with open(file, 'r') as f:
				lines = f.readlines()
				lines[e.line - 1] = lines[e.line - 1][:0] + lines[e.line - 1][1:]
			with open(file, 'w') as f:
				f.writelines(lines)

def SPACE_EMPTY_LINE():
	for e in errors:
		if e.type == 'SPACE_EMPTY_LINE':
			with open(file, 'r') as f:
				lines = f.readlines()
				lines[e.line - 1] = lines[e.line - 1][:0] + '\n'
			with open(file, 'w') as f:
				f.writelines(lines)

def BRACE_NEWLINE():
	for e in errors:
		if e.type == 'BRACE_NEWLINE':
			with open(file, 'r') as f:
				lines = f.readlines()
				last_parenthesis = lines[e.line - 1].rfind(')')
				wrong_brace = lines[e.line - 1].find('{')
				lines[e.line - 1] = lines[e.line - 1][:last_parenthesis] + lines[e.line - 1][last_parenthesis] + '\n' + lines[e.line - 1][wrong_brace:]
			with open(file, 'w') as f:
				f.writelines(lines)
			exit(0)

checks = [
	EMPTY_LINE_EOF,
	SPC_BEFORE_NL,
	INVALID_HEADER,
	BRACE_SHOULD_EOL,
	SPACE_BEFORE_FUNC,
	RETURN_PARENTHESIS,
	SPACE_REPLACE_TAB,
	NL_AFTER_PREPROC,
	NL_AFTER_VAR_DECL,
	NEWLINE_PRECEDES_FUNC,
	NO_ARGS_VOID,
	CONSECUTIVE_SPC,
	SPC_BFR_OPERATOR,
	TOO_FEW_TAB,
	TOO_MANY_TAB,
	SPACE_EMPTY_LINE,
	BRACE_NEWLINE
]

for i in range(0, 10):
	for c in checks:
		errors_update()
		c()