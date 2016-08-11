#!/usr/bin/python3
# -*- coding: utf-8 -*-

# read-codebook.py

# Copyright (C) 2016 Teracow Software

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

# If you find this code useful, please let me know. :) teracow@gmail.com

# Traverse the codebook dB structure and locate individual entries

import os
import sys
import getopt
import sqlite3 as lite

script_details = 'read-codebook.py (2016-08-12)'

db_name_categories = 'categories'
db_name_entries = 'entries'
db_name_fields = 'fields'
db_name_types = 'types'						# field data types - password, email, number, etc ...

db_col_id = 'id'
db_col_category_id = 'category_id'
db_col_entry_id = 'entry_id'
db_col_type_id = 'type_id'
db_col_name = 'name'
db_col_value = 'value'

colour_white_bright = '\033[1;37;40m'
colour_yellow_bright = '\033[1;33;40m'
colour_green_bright = '\033[1;32;40m'
colour_red_bright = '\033[1;31;40m'
colour_reset = '\033[0m'

def menu(title, records, record_name, options, prompt_only):
	total = len(records)
	header_line, separator_line, footer_line, box_width = generate_lines_variable_width_display(title, records, record_name)

	if prompt_only:
		display_menu = False
	else:
		display_menu = True

	while True:
		if display_menu: 
			print(header_line)

			for index, record in enumerate(records):
				print(generate_line_item_display(index + 1, record[record_name], box_width))

		if total > 0:
			if display_menu: print(separator_line)

			prompt_head = allowed_key('1') + ' to ' + allowed_key(str(total)) 
		else:
			prompt_head = ''

		if options == 'B':
			if display_menu: print(generate_line_item_display('B', 'Back', box_width))

			prompt_tail = ' or ' + allowed_key('B')
		elif options == 'W':
			if display_menu:
				print(generate_line_item_display('W', 'Write to text file', box_width))
				print(generate_line_item_display('B', 'Back', box_width))

			prompt_tail = allowed_key('W') + ' or ' + allowed_key('B')
		else:
			prompt_tail = ''

		prompt_tail += ' or ' + allowed_key('Q')
		
		if display_menu:
			print(generate_line_item_display('Q', 'Quit', box_width))
			print(footer_line)
			
		user_selection = input(' ' * 3 + 'select (' + prompt_head + prompt_tail + '): ')
		print()

		display_menu = False
		
		# allowed keys based on 'options'
		if not user_selection.isdigit():
			if user_selection == 'Q' or user_selection == 'q':
				sys.exit()

			if options == 'B':
				if user_selection == 'B' or user_selection == 'b':
					user_selection = 0
					break
			elif options == 'W':
				if user_selection == 'W' or user_selection == 'w':
					user_selection = -1
					break
				elif user_selection == 'B' or user_selection == 'b':
					user_selection = 0
					break
					
		else:
			if int(user_selection) > 0 and int(user_selection) <= total:
				break
		
	return user_selection

def allowed_key(text):

	return colour_yellow_bright + text + colour_reset

def bold_title(text):
	
	return colour_white_bright + text + colour_reset
	
def calc_text_display_width(index, text):
	
	return len('(' + str(index) + ') ' + text + ' ')

def generate_line_item_display(index, text, box_width):

	return ' │ ({}) {} │'.format(allowed_key(str(index)), text + ' ' * (box_width - calc_text_display_width(index, text)))
	
def generate_lines_variable_width_display(title, records, record_name):
	box_width = 32			# set a minimum size
	index_space = 1			# this is the space between the left border and the index parentheses - only used to calculate box width
	
	# find longest display item so box width can be calculated
	for index, record in enumerate(records):
		item_width = calc_text_display_width(index, record[record_name])
		
		if item_width > box_width:
			box_width = item_width
	
	if title:
		header_line = ' ┌' + '─' * 4 + '┤ ' + bold_title(title) + ' ├' + '─' * (box_width - 4 - 4 - len(title) + index_space) + '┐'
		separator_line = ' ├' + '─' * ((box_width) + index_space) + '┤'
		footer_line = ' └' + '─' * ((box_width) + index_space) + '┘'
	else:
		header_line = ' ┌' + '─' * ((box_width) + index_space) + '┐'
		separator_line = ''
		footer_line = ' └' + '─' * ((box_width) + index_space) + '┘'
						
	return header_line, separator_line, footer_line, box_width

def generate_lines_full_width_display(title):
	rows_str, columns_str = os.popen('stty size', 'r').read().split()
	columns = int(columns_str)
	
	header_line = '═' * 8 + '╣ ' + bold_title(title) + ' ╠' + '═' * (columns - 8 - 4 - len(title))
	footer_line = '═' * columns
						
	return header_line, footer_line

def write_entry_to_file(filename, content):
	output_pathfile = filename.replace(' ', '_').replace('/', '_').replace('\\', '_').replace('?', '_')
	output_pathfile += '.txt'

	if not os.path.exists(output_pathfile):
		with open(output_pathfile, 'w') as text_file:
			text_file.write(content + '\n')

		print(" * {} *".format(colour_green_bright + 'written to file' + colour_reset))
	else:
		print(" ! {} !".format(colour_red_bright + 'could not write (file already exists)' + colour_reset))
	
	return
	
def clear_display():
	print('\033c')
	
	return
	
def main(argv):
	global db_tab_types, db_tab_fields
	help_message = './read-codebook.py -i <inputfile>'
	input_pathfile = ''

	try:
		opts, args = getopt.getopt(argv,'hvi:',['help','version','input-file='])
	except getopt.GetoptError:
		print(help_message)
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			print(help_message)
			sys.exit()
		elif opt in ('-v', '--version'):
			print(script_details)
			sys.exit()
		elif opt in ('-i', '--input-file'):
			input_pathfile = arg

	if not input_pathfile:
		print(help_message)
		sys.exit(1)
	
	print(script_details)
	
	con = lite.connect(input_pathfile)
	
	with con:
		con.row_factory = lite.Row
		cur = con.cursor()    
	
		# retrieve field types
		cur.execute('SELECT * FROM ' + db_name_types)
		db_tab_types = cur.fetchall()

		# retrieve categories
		cur.execute('SELECT * FROM ' + db_name_categories)
		db_tab_categories = cur.fetchall()

		# categories loop
		while True:
			# query user
			clear_display()
			print(' ' * 2 + script_details + '\n')
			user_selection = menu(db_name_categories, db_tab_categories, db_col_name, '', False)

			if user_selection == 0:
				break
			else:
				row = db_tab_categories[int(user_selection) - 1]
				selected_category_id = row[db_col_id]
				db_category = row[db_col_name]
				
				cur.execute('SELECT * FROM ' + db_name_entries + ' WHERE ' + db_col_category_id + ' = \"' + selected_category_id + '\"')
				db_tab_entry = cur.fetchall()

				# entries loop
				while True:
					# query user
					clear_display()
					print(' ' * 2 + script_details + '\n')
					user_selection = menu(db_category, db_tab_entry, db_col_name, 'B', False)

					if user_selection == 0:
						break
					else:
						row = db_tab_entry[int(user_selection) - 1]
						selected_entry_id = row[db_col_id]
						db_entry = row[db_col_name]
						
						cur.execute('SELECT * FROM ' + db_name_fields + ' WHERE ' + db_col_entry_id + ' = \"' + selected_entry_id + '\"')
						db_tab_fields = cur.fetchall()

						content = ''
						
						for field in db_tab_fields:
							if field[db_col_type_id]:
								for field_types in db_tab_types:
									if field_types[db_col_id] == field[db_col_type_id]:
										content += "{}:\n\t{}\n".format(field_types[db_col_name], field[db_col_value])
										break
							else:
								# appears that notes don't have a field type ID
								content = field[db_col_value]

						header_line, footer_line = generate_lines_full_width_display(db_entry)
						
						clear_display()
						print(' ' * 2 + script_details + '\n')
						print(header_line)
						print(content)
						print(footer_line)
						print()

						prompt_only = False
						
						# single entry loop
						while True:
							# query user
							user_selection = menu('', '', '', 'W', prompt_only)

							if user_selection == -1:
								write_entry_to_file(db_entry, content)
								print()
								prompt_only = True
							elif user_selection == 0:
								break

if __name__ == '__main__':
	main(sys.argv[1:])
