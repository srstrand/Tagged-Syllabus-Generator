#!/usr/bin/python3

#import libraries
#================
#to use some terminal commands (e.g., 'clear')
import os

import re
import sys
#================

#TODO
#How to close list when at the end of the file??
#Figure out what to do about extraneous line breaks in the middle of paragraphs
#================

#Function defs
def buildList(prefix,tabCount,listLevel,line):
	#Strip the bullet/digit and space, create list item
	line = re.sub(r'(^\s*)(?:\+|\-|\*|\d+\.)(?: |\t)(.*)',r'\1\t<li>\2</li>',line)

	#new unordered list or sublist
	if tabCount[i] == len(listLevel):
		listLevel.append(prefix)
		tabs = tabCount[i] #len(listLevel)

		line = re.sub(r'(^\s*)(.*)',r'\t'*tabs+r'<'+prefix+r'l>\n\1\2',line)

	return line

def listWrapup(tabCount,listLevel,line):
	#Fails if last line of file is a bulleted entry!
	if emptyLine:
		#Get rid of the '\n'
		line = ""
		tabs = 0
		while listLevel:
			prefix = listLevel.pop()
			tabs = len(listLevel)#tabCount[i]-j

			#The '*' operator allows one to specify a variable-number of occurrences in the replacement string
			#Since we found an empty line, create closing entries for all open lists. We do this by working backward from the last opened list. regex was the wrong tool for this one!
			line = line+"\t"*tabs+"</"+prefix+"l>\n"
		#After conclusion of all open lists, reinsert the empty line
		line = line + "\n"
	else:
		for j in range(tabCount[i],tabCount[i-1]):
			prefix = listLevel.pop()
			tabs = j+1

			#The '*' operator allows one to specify a variable-number of occurrences in the replacement string
			line = re.sub(r'(^\s*)(.*)',r'\t'*tabs+r'</'+prefix+r'l>\n\1\2',line)
	return line


#start a table
def tableHead(line):
	return '<table>\n\t<thead>\n\t' + tableEntries('h style="font-weight:bold;"',line) + '\n\t</thead>\n\t<tbody>\n\t'

#create a normal row in the table
def tableBody(line):
	return tableEntries("d",line)


#Create a row in the table; process table entries separated by pipes; 'data' is either 'h' or 'd' for '<th>' or '<td>', depending on whether or not the current line is a header
def tableEntries(data,line):
	columnText = line.split("|")
	line = ''
	while columnText:
		entry = columnText.pop(0)

		#if not empty and not white space, then create column entry
		if entry and not re.match(r'\s+$',entry):
			line = line + "\t\t<t" + data +">" + entry + "</t" + data + ">\n"
	return "<tr>\n" + line + "\n\t</tr>\n\t"

#close up the current table
def tableClose(line):
	return line + "\n\t</tbody>\n</table>\n\n"

def insertHeaderInfo(key):
	return headersDict[key] if headersDict.get(key) else "[missing " + key + "]"
#================

listLevel = []
i = 0
tabCount = [0]
meta = False
headersDict = {}
mathMode = False

fileName = "Syllabus-Template"

with open(fileName + ".md","r") as f:
	with open(fileName + ".html","w") as g:
		for line in f:
			i += 1
			#search line
			#Process Hierarchy:
				# metadata
				# Headings
				# lists
				# tables
				# strong
				# emphasis
				# strikethrough
				# links
				# math mode characters
				# escaped characters: \$, \%

			#Should we wrap the line in <p> tags? Only if it isn't a heading, list, or table
			p = True
			tabCount.append(0)

		#Get metadata
			#Change formatting of metadata section to match yaml, standard markdown
			if re.match(r'-{3}',line):
				if meta:
					meta = False
				else:
					meta = True
				continue

			if meta:
				key, val = line.split(": ")
				headersDict[key] = val.rstrip()
				continue

			#Keep track of indentation level
			linex = line.expandtabs(4)
			tabCount[i] = 0 if linex.isspace() else (len(linex) - len(linex.lstrip())) // 4

			#create a tuple of the #s appearing in a line; this determines the 'heading' level in HTML
			matches = tuple(re.findall(r'\#',line))
			if matches:
				p = False
				#store the number of #s as a string for concatentation
				level=str(len(matches))

				#if markdown found, replace in 'line'
				#you can also use '\g<n>' to match the nth saved group
				#Match all #s and trailing space, then store the rest of the text
				line = re.sub(r'\#+ (.*)',r'<h'+level+r'>\1</h'+level+r'>',line)
				
				#write new 'line' out to file
				g.write(line)

				#Stop processing the current line
				continue

		#Lists!
			#Unordered first
			if re.match(r'^\s*(?:\+|\-|\*)(?: |\t)',line):
				p = False
				line = buildList("u",tabCount,listLevel,line)

			#Now Ordered
			if re.match(r'^\s*\d+\.(?: |\t)',line):
				p = False
				line = buildList("o",tabCount,listLevel,line)

			#end of previous list(s); loop to close all completed lists
			emptyLine = re.match(r'^\s*$',line)
			if listLevel and (emptyLine or tabCount[i-1] > tabCount[i]):
				line = listWrapup(tabCount,listLevel,line)

			if emptyLine:
				p = False

		#Tables!
			if re.match(r'\s*\|',line):
				p = False
				nextline = ''
				try:
					nextline = next(f)
				except Exception as e:
					print(e)
					line = tableClose(tableBody(line))
					g.write(line)
					break

				if re.search(r'(?:-){3,}',nextline):
					#start a table
					line = tableHead(line)

				elif re.search(r'^\s*$',nextline):
					#close up the current table
					line = tableClose(tableEntries("d",line))

				else:
					#process 'line' and 'nextline' as rows in the table
					line = tableBody(line)
					nextline = tableBody(nextline)

					line = line + nextline

			if p:
				line = "<p>" + line.rstrip() + " </p>\n"

		#Match formatting markup
			#Match a double **, for 'strong'
			matches = tuple(re.findall(r'(?:\*{2}|_{2})',line))
			if matches:
				for x in matches:
					#if markdown found, replace in 'line'
					#you can also use '\g<n>' to match the nth saved group
					#Match double *s or _s for 'strong'
					line = re.sub(r'^(.*)\*{2}(.*?)\*{2}(.*)$',r'\1<strong>\2</strong>\3',line)
					
			#Match a double __, for 'strong'
			matches = tuple(re.findall(r'_{2}',line))
			if matches:
				for x in matches:
					#if markdown found, replace in 'line'
					#you can also use '\g<n>' to match the nth saved group
					#Match double *s or _s for 'strong'
					line = re.sub(r'^(.*)_{2}(.*?)_{2}(.*)$',r'\1<strong>\2</strong>\3',line)
					
			#Match a single * not followed by a space, for 'emphasis'
			matches = tuple(re.findall(r'\*(?! )',line))
			if matches:
				for x in matches:
					#if markdown found, replace in 'line'
					#you can also use '\g<n>' to match the nth saved group
					#Match single *s for 'emphasis'
					line = re.sub(r'^(.*)\*(?! )(.*?)\*(.*)$',r'\1<em>\2</em>\3',line)
				
			#Match a single _, for 'emphasis'
			matches = tuple(re.findall(r'_',line))
			if matches:
				for x in matches:
					#if markdown found, replace in 'line'
					#you can also use '\g<n>' to match the nth saved group
					#Match single *s for 'emphasis'
					line = re.sub(r'^(.*)_(.*?)_(.*)$',r'\1<em>\2</em>\3',line)
				
			#Match a ~~, for 'strikethrough'
			matches = tuple(re.findall(r'\~{2}',line))
			if matches:
				for x in matches:
					#if markdown found, replace in 'line'
					#you can also use '\g<n>' to match the nth saved group
					#Match double ~~s for 'strikethrough'
					line = re.sub(r'^(.*)\~{2}(.*?)\~{2}(.*)$',r'\1<s>\2</s>\3',line)
				
		#Match links
			matches = tuple(re.findall(r'\]\(',line))
			if matches:
				for x in matches:
					#if markdown found, replace in 'line'
					#you can also use '\g<n>' to match the nth saved group

					#Match: after left bracket, capture one or more non-bracket characters that are followed by a right bracket left parenthesis; then capture everything (non-greedy) after that right bracket left parenthesis up to the next right parenthesis
					line = re.sub(r'\[([^\]]+)(?=\]\()\]\(([^\)]+)\)',r'<a href="\2">\1</a>',line)

			#Now match raw links appearing in the line
			if re.search(r'.*(?<!")http',line):
				line = re.sub(r'(?<!")(http[^ ]+)',r'<a href="\1">\1</a>',line)

		#Finally, detect any LaTeX-style math modes, and convert escaped characters
			#Match exactly two literal dollar signs ('display math mode')
			if re.search(r'\${2}',line):
				line = re.sub(r'\${2}([^\$]+)\${2}',r'\\[ \1 \\]',line)

			#Match single dollar signs ('inline math mode')
			if re.search(r'\$',line):
				line = re.sub(r'\$([^\$]+)\$',r'\\( \1 \\)',line)

			#Replace escaped dollar signs with regular ones
			if re.search(r'\\\$',line):
				line = re.sub(r'\\\$',r'$',line)
				
			#Turn everything after a literal percent into an HTML comment
			if re.search(r'(?<!\\)\%',line):
				line = re.sub(r'(?<!\\)\%(.*)',r'<!--\1-->',line)
				
			#Replace escaped percent signs with regular ones
			if re.search(r'\\\%',line):
				line = re.sub(r'\\\%',r'%',line)

			#Detect math mode in the line
			if re.search(r'\\\(|\\\[',line): mathMode = True
				
			#write new 'line' out to file
			g.write(line)

#Just in case the file ended on a list item
if listLevel:
	with open(fileName + ".html","a") as g:
		emptyLine = True
		line = ''
		g.write(listWrapup(tabCount,listLevel,line))


#include mathjax header if math mode found in document
mathjax = '\t<script type="text/javascript" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">\n\t</script>' if mathMode else ''
#Define the HTML header
header = ("<!DOCTYPE html>\n\n"
	"<html lang='en'>\n"
	"<head>\n"
	"	<title>"+insertHeaderInfo('title')+"</title>\n"
	'	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"> \n'
	'	<meta name="viewport" content="width=device-width, initial-scale=1">\n'
	'	<meta name="instructor" content="'+insertHeaderInfo('instructor')+'">\n'
	'	<meta name="course" content="'+insertHeaderInfo('course')+'">\n'
	'	<meta name="term" content="'+insertHeaderInfo('term')+'">\n'
	'	<meta name="author" content="Steve Strand">\n'
	'	<meta name="description" content="Syllabus for '+insertHeaderInfo('course')+', '+insertHeaderInfo('term')+'">\n'
	#'\t	<link type="text/css" rel="stylesheet" href="CSS/teaching.css">\n'
	'	<style>\n'
	'		body, input {\n'
	'			background-color: #222;\n'
	'			color: #fff;\n'
	'			max-width: 940px;\n'
	'			font-size: 1.4vw;\n'
	'			margin-left: 15px\n\t\t}\n'
	'		a { color: cyan;}\n'
	'		tr:nth-child(even) {background-color: #626262;}\n'
	'	</style>\n'
	+ mathjax +
	'	\n'
	"</head>\n\n"
	"<body>\n"
	"<h1>" + insertHeaderInfo('title') + "</h1>"
	)

#Write out header and closing tags
with open(fileName + ".html","r") as f: data = f.read()
with open(fileName + ".html","w") as g:
	g.write(header+data+"\n</body>\n</html>")