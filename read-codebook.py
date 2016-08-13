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

script_details = 'read-codebook.py (2016-08-13)'

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

def menu(title, table, column, options, prompt_only):
	global box_width, prebox_space
	
	box_width = 30			# Set a minimum menu box size - this is the overall width including box chars.
							# Note! menu option messages such as 'Write to text file' are not length tested!
							# This must be allowed for when adjusting this figure.

	prebox_space = 1		# space before left border
	total = len(table)
	header_line, separator_line, footer_line = generate_lines_variable_width_display(title, table, column)

	if prompt_only:
		display_menu = False
	else:
		display_menu = True

	while True:
		prompt_head = ''
		prompt_tail = ''

		if display_menu:
			print(header_line)

			for index, record in enumerate(table):
				print(generate_line_item_display(index + 1, record[column]))

		if total > 0:
			if display_menu: print(separator_line)

			prompt_head += allowed_key('1') + ' to ' + allowed_key(str(total)) + ' or '

		if 'S' in options:
			if display_menu: print(generate_line_item_display('S', 'Search'))

			prompt_tail += allowed_key('S') + ' or '

		if 'W' in options:
			if display_menu: print(generate_line_item_display('W', 'Write to text file'))

			prompt_tail += allowed_key('W') + ' or '

		if 'B' in options:
			if display_menu: print(generate_line_item_display('B', 'Back'))

			prompt_tail += allowed_key('B') + ' or '

		prompt_tail += allowed_key('Q')

		if display_menu:
			print(generate_line_item_display('Q', 'Quit'))
			print(footer_line)

		try:
			user_selection = input((' ' * prebox_space) + 'select (' + prompt_head + prompt_tail + '): ')
			print()
		except KeyboardInterrupt:
			print('\n')
			sys.exit()

		# allowed keys based on 'options'
		if user_selection.isdigit():
			if int(user_selection) > 0 and int(user_selection) <= total:
				break
		else:
			if user_selection.upper() == 'Q':
				sys.exit()

			if 'B' in options:
				if user_selection.upper() == 'B':
					user_selection = 0
					break

			if 'W' in options:
				if user_selection.upper() == 'W':
					user_selection = -1
					break

			if 'S' in options:
				if user_selection.upper() == 'S':
					user_selection = -2
					break

		display_menu = False			# don't re-display menu - only show the prompt

	return user_selection

def allowed_key(text):

	return colour_yellow_bright + text + colour_reset

def bold_title(text):

	return colour_white_bright + text + colour_reset

def calc_text_display_width(index, text):

	return len(str(index) + text)

def generate_line_item_display(index, text):

	return (' ' * prebox_space) + '│' + (' ' * row_index_space) + '(' + allowed_key(str(index)) + ')' + (' ' * row_item_space) + text + (' ' * (box_width - calc_text_display_width(index, text) - row_min_length)) + (' ' * row_trailing_space) + '│'

def generate_lines_variable_width_display(title, records, record_index):
	global box_width, prebox_space, row_index_space, row_item_space, row_trailing_space, row_min_length

	row_index_space = 1		# space between the left border and the index parentheses - only used to calculate box width
	row_item_space = 1		# space between index parentheses and the displayed item
	row_trailing_space = 1	# space between item and right border
	row_min_length = row_index_space + 2 + row_item_space + row_trailing_space + 2		# 2 x parentheses and 2 x box chars

	title_left_border = 4	# chars from left border to start of title bookend
	title_box_chars = 4		# number of fixed characters needed to form title
	title_space = 1			# space between bookends and title on left and right
	title_extra_spaces = title_space * 2
	title_min_length = len(title) + title_box_chars + title_extra_spaces + title_left_border

	# find longest display item so box width can be recalculated
	for index, record in enumerate(records):
		item_width = calc_text_display_width(index, record[record_index])

		if (item_width + row_min_length) > box_width:
			box_width = item_width + row_min_length

	if title_min_length > box_width:
		box_width = title_min_length

	if title:
		header_line = (' ' * prebox_space) + '┌' + ('─' * title_left_border) + '┤' + (' ' * title_space) + bold_title(title) + (' ' * title_space) + '├' + '─' * (box_width - title_min_length) + '┐'
		separator_line = (' ' * prebox_space) + '├' + ('─' * (box_width - 2)) + '┤'
		footer_line = (' ' * prebox_space) + '└' + ('─' * (box_width - 2)) + '┘'
	else:
		header_line = (' ' * prebox_space) + '┌' + ('─' * (box_width - 2)) + '┐'
		separator_line = ''
		footer_line = (' ' * prebox_space) + '└' + ('─' * (box_width - 2)) + '┘'

	return header_line, separator_line, footer_line

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
	con = lite.connect(database_pathfile)

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()
		# SELECT * FROM fields JOIN entries ON fields.entry_id = entries.id WHERE value LIKE "%email%"
		cur.execute('SELECT * FROM ' + db_name_fields + ' JOIN ' + db_name_entries + ' ON ' + db_name_fields + '.' + db_col_entry_id + ' = ' + db_name_entries + '.' + db_col_id + ' WHERE value LIKE \"%' + text + '%\"')

	return cur.fetchall()

def get_db_fields_from_entry(entry_id):
	con = lite.connect(database_pathfile)

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()

		# try joining fields to field types first. This will return none for notes as they don't have a field type set.
		# SELECT * FROM fields JOIN types ON fields.type_id = types.id WHERE entry.id = "328658"
		cur.execute('SELECT * FROM ' + db_name_fields + ' JOIN ' + db_name_types + ' ON ' + db_name_fields + '.' + db_col_type_id + ' = ' + db_name_types + '.' + db_col_id + ' WHERE ' + db_col_entry_id + ' = \"' + entry_id + '\"')
		result = cur.fetchall()

		if len(result) == 0:		# this may be a note, so try query again without join
			# SELECT * FROM fields WHERE entry_id = "328456"
			cur.execute('SELECT * FROM ' + db_name_fields + ' WHERE ' + db_col_entry_id + ' = \"' + entry_id + '\"')
			result = cur.fetchall()

	return result

def get_db_entries_from_category(category_id):
	con = lite.connect(database_pathfile)

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute('SELECT * FROM ' + db_name_entries + ' WHERE ' + db_col_category_id + ' = \"' + category_id + '\"' + ' ORDER BY ' + db_col_name)

	return cur.fetchall()

def get_db_categories():
	con = lite.connect(database_pathfile)

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute('SELECT ' + db_col_id + ', ' + db_col_name + ' FROM ' + db_name_categories + ' ORDER BY ' + db_col_name)

	return cur.fetchall()

def main(argv):
	global types_table, database_pathfile
	help_message = './read-codebook.py -i <inputfile>'
	database_pathfile = ''

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
			database_pathfile = arg

	if not database_pathfile:
		print(help_message)
		sys.exit(1)

	print(script_details)
	print()

	if not os.path.exists(database_pathfile):
		print('! File not found! [{}]'.format(database_pathfile))
		sys.exit(1)

	all_categories = get_db_categories()
	previous_views_stack = []
	current_view = 'categories'

	while True:
		if current_view == 'categories':
			clear_display()
			print(' ' * 2 + script_details + '\n')
			category_index = menu(db_name_categories, all_categories, db_col_name, 'S', False)

			previous_views_stack.append(current_view)

			if category_index == -2:
				current_view = 'search'
			else:
				category_row = all_categories[int(category_index) - 1]
				category_entries = get_db_entries_from_category(category_row[db_col_id])
				current_view = 'entries'

		if current_view == 'entries':
			clear_display()
			print(' ' * 2 + script_details + '\n')
			entry_index = menu(category_row[db_col_name], category_entries, db_col_name, 'SB', False)

			if entry_index == 0:
				current_view = previous_views_stack.pop()
			elif entry_index == -2:
				previous_views_stack.append(current_view)
				current_view = 'search'
			else:
				entry_row = category_entries[int(entry_index) - 1]
				entry_id = entry_row[db_col_id]
				previous_views_stack.append(current_view)
				current_view = 'fields'

		if current_view == 'search':
			try:
				search_text = input(' ' * 3 + 'enter search text: ')
				search_entries = get_db_search(search_text)
				current_view = 'search results'
			except KeyboardInterrupt:
				current_view = previous_views_stack.pop()

		if current_view == 'search results':
			clear_display()
			print(' ' * 2 + script_details + '\n')
			entry_index = menu('Search results for \"' + search_text + '\"', search_entries, db_col_name, 'B', False)

			if entry_index == 0:
				current_view = previous_views_stack.pop()
			else:
				entry_row = search_entries[int(entry_index) - 1]
				entry_id = entry_row[db_col_entry_id]
				previous_views_stack.append(current_view)
				current_view = 'fields'

		if current_view == 'fields':
			entry_name = entry_row[db_col_name]
			entry_fields = get_db_fields_from_entry(entry_id)
			field_content = ''
			header_line, footer_line = generate_lines_full_width_display(entry_name)

			for field in entry_fields:
				if field[db_col_type_id]:
					field_content += "{}:\n\t{}\n".format(field[db_col_name], field[db_col_value])
				else:
					# appears that notes don't have a field type ID
					field_content = field[db_col_value]
					break

			clear_display()
			print(' ' * 2 + script_details + '\n')
			print(header_line)
			print(field_content)
			print(footer_line)
			print()

			prompt_only = False

			while True:
				user_selection = menu('', '', '', 'WB', prompt_only)

				if user_selection == -1:
					write_entry_to_file(entry_name, field_content)
					print()
					prompt_only = True
				elif user_selection == 0:
					current_view = previous_views_stack.pop()
					break

if __name__ == '__main__':
	main(sys.argv[1:])
