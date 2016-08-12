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
		prompt_head = ''
		prompt_tail = ''
		
		if display_menu: 
			print(header_line)

			for index, record in enumerate(records):
				print(generate_line_item_display(index + 1, record[record_name], box_width))

		if total > 0:
			if display_menu: print(separator_line)

			prompt_head += allowed_key('1') + ' to ' + allowed_key(str(total)) + ' or '

		if 'S' in options:
			if display_menu: print(generate_line_item_display('S', 'Search', box_width))
				
			prompt_tail += allowed_key('S') + ' or '

		if 'W' in options:
			if display_menu: print(generate_line_item_display('W', 'Write to text file', box_width))

			prompt_tail += allowed_key('W') + ' or '

		if 'B' in options:
			if display_menu: print(generate_line_item_display('B', 'Back', box_width))

			prompt_tail += allowed_key('B') + ' or '
		
		prompt_tail += allowed_key('Q')
		
		if display_menu:
			print(generate_line_item_display('Q', 'Quit', box_width))
			print(footer_line)
			
		user_selection = input(' ' * 3 + 'select (' + prompt_head + prompt_tail + '): ')
		print()
		
		# allowed keys based on 'options'
		if not user_selection.isdigit():
			if user_selection == 'Q' or user_selection == 'q':
				sys.exit()

			if 'B' in options:
				if user_selection == 'B' or user_selection == 'b':
					user_selection = 0
					break
			
			if 'W' in options:
				if user_selection == 'W' or user_selection == 'w':
					user_selection = -1
					break

			if 'S' in options:
				if user_selection == 'S' or user_selection == 's':
					user_selection = -2
					break
					
		else:
			if int(user_selection) > 0 and int(user_selection) <= total:
				break
		
		display_menu = False			# don't re-display menu - only show the prompt

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

def get_db_search(text):
	con = lite.connect(input_pathfile)

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()    
		cur.execute('SELECT * FROM ' + db_name_fields + ' WHERE ' + db_col_value + ' LIKE \"%' + text + '%\"')
	
	return cur.fetchall()

def get_db_entries(table, column, row_id):
	con = lite.connect(input_pathfile)
	
	with con:
		con.row_factory = lite.Row
		cur = con.cursor()    
		cur.execute('SELECT * FROM ' + table + ' WHERE ' + column + ' = \"' + row_id + '\"')
		
	return cur.fetchall()

def get_db_table(table):
	con = lite.connect(input_pathfile)
	
	with con:
		con.row_factory = lite.Row
		cur = con.cursor()    
		cur.execute('SELECT * FROM ' + table)

	return cur.fetchall()

def main(argv):
	global db_tab_types, db_tab_fields, input_pathfile
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
	print()
	
	if not os.path.exists(input_pathfile):
		print('! File not found! [{}]'.format(input_pathfile))
		sys.exit(1)
	
	# field types
	db_tab_types = get_db_table(db_name_types)

	# categories
	db_tab_categories = get_db_table(db_name_categories)

	current_view = 'categories'
	previous_view = current_view

	while True:
		if current_view == 'categories':
			# query user
			clear_display()
			print(' ' * 2 + script_details + '\n')
			category_selection = menu(db_name_categories, db_tab_categories, db_col_name, 'S', False)

			if category_selection == -2:
				previous_view = current_view
				current_view = 'search'
			else:
				current_view = 'entries'
	
		if current_view == 'search':
			search_text = input(' ' * 3 + 'enter search word: ')
			print()

			db_search = get_db_search(search_text)

			search_selection = menu('Search results', db_search, db_col_value, 'B', False)

			if search_selection == 0:
				current_view = previous_view
			else:
				current_view = 'entries'
	
		if current_view == 'entries':
			row = db_tab_categories[int(category_selection) - 1]
			selected_category_id = row[db_col_id]
			db_category = row[db_col_name]
			db_tab_entry = get_db_entries(db_name_entries, db_col_category_id, selected_category_id)

			# query user
			clear_display()
			print(' ' * 2 + script_details + '\n')
			entry_selection = menu(db_category, db_tab_entry, db_col_name, 'SB', False)

			if entry_selection == 0:
				current_view = 'categories'
			elif entry_selection == -2:
				previous_view = current_view
				current_view = 'search'
			else:
				current_view = 'entry'
					
		if current_view == 'entry':
			row = db_tab_entry[int(entry_selection) - 1]
			selected_entry_id = row[db_col_id]
			db_entry = row[db_col_name]
			db_tab_fields = get_db_entries(db_name_fields, db_col_entry_id, selected_entry_id)
			field_content = ''
			header_line, footer_line = generate_lines_full_width_display(db_entry)
			
			for field in db_tab_fields:
				if field[db_col_type_id]:
					for field_types in db_tab_types:
						if field_types[db_col_id] == field[db_col_type_id]:
							field_content += "{}:\n\t{}\n".format(field_types[db_col_name], field[db_col_value])
							break
				else:
					# appears that notes don't have a field type ID
					field_content = field[db_col_value]

			clear_display()
			print(' ' * 2 + script_details + '\n')
			print(header_line)
			print(field_content)
			print(footer_line)
			print()

			prompt_only = False
			
			# single entry loop
			while True:
				# query user
				user_selection = menu('', '', '', 'WB', prompt_only)

				if user_selection == -1:
					write_entry_to_file(db_entry, field_content)
					print()
					prompt_only = True
				elif user_selection == 0:
					current_view = 'entries'
					break

if __name__ == '__main__':
	main(sys.argv[1:])
