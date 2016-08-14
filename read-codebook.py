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

script_file = 'read-codebook.py'
script_details = script_file + ' (2016-08-14)'

colour_white_fg = '\033[97m'
colour_light_fg = '\033[38;5;250m'
colour_yellow_fg = '\033[33;40m'
colour_green_bright = '\033[1;32;40m'
colour_red_bright = '\033[1;31;40m'
colour_reset = '\033[0m'

colour_grey_fg = '\033[38;5;246m'
colour_orange_fg = '\033[38;5;214m'
colour_dark_grey_bg = '\033[48;5;234m'
colour_bright = '\033[1m'

colours_menu_box = colour_light_fg + colour_dark_grey_bg
colours_menu_title = colour_orange_fg + colour_bright + colour_dark_grey_bg

colours_single_entry_title = colour_white_fg + colour_bright + colour_dark_grey_bg
colours_single_entry_header = colour_grey_fg + colour_dark_grey_bg
colours_single_entry_name = colour_light_fg + colour_dark_grey_bg
colours_single_entry_value = colour_orange_fg + colour_dark_grey_bg
colours_single_entry_footer = colour_grey_fg + colour_dark_grey_bg

def draw_menu(title, table, column, options, prompt_only):
	global box_width, prebox_space

	box_width = 31		# Set a minimum menu box size - this is the overall width including box chars.
						# Note! menu option messages such as 'Write to text file' are not length tested!
						# This must be allowed for when adjusting this figure.

	prebox_space = 1	# space before left border
	display_menu = True
	total = len(table)
	prompt_template = (' ' * prebox_space) + ' select ({}): '

	menu_header, menu_separator, menu_footer = generate_menu_lines(title, table, column, options, prompt_template)
	display_menu != prompt_only

	while True:
		prompt_head = ''
		prompt_tail = ''

		if display_menu:
			print(menu_header)

			for index, record in enumerate(table):
				print(generate_menu_line_item(index + 1, record[column]))

		if total > 0:
			if display_menu: print(menu_separator)

			prompt_head += allowed_item_key('1') + ' to ' + allowed_item_key(str(total)) + ' or '

		if 'S' in options:
			if display_menu: print(generate_menu_line_option('S', 'Search'))

			prompt_tail += allowed_option_key('S') + ' or '

		if 'W' in options:
			if display_menu: print(generate_menu_line_option('W', 'Write to text file'))

			prompt_tail += allowed_option_key('W') + ' or '

		if 'F' in options:
			if display_menu: print(generate_menu_line_option('F', 'Favorites'))

			prompt_tail += allowed_option_key('F') + ' or '

		if 'B' in options:
			if display_menu: print(generate_menu_line_option('B', 'Back'))

			prompt_tail += allowed_option_key('B') + ' or '

		prompt_tail += allowed_option_key('Q')

		if display_menu:
			print(generate_menu_line_option('Q', 'Quit'))
			print(menu_footer)

		try:
			user_selection = input(prompt_template.format(prompt_head + prompt_tail))
			print()
		except KeyboardInterrupt:
			print('\n')
			sys.exit()

		# allowed keys based on 'options'
		if user_selection.isdigit():
			if int(user_selection) > 0 and int(user_selection) <= total: break
		else:
			if user_selection.upper() == 'Q': sys.exit()

			if 'B' in options:
				if user_selection.upper() == 'B':
					user_selection = 0
					break

			if 'F' in options:
				if user_selection.upper() == 'F':
					user_selection = -3
					break

			if 'W' in options:
				if user_selection.upper() == 'W':
					user_selection = -1
					break

			if 'S' in options:
				if user_selection.upper() == 'S':
					user_selection = -2
					break

		display_menu = False			# don't re-display menu - only show prompt

	return user_selection

def allowed_item_key(text):

	return colour_orange_fg + colour_bright + colour_dark_grey_bg + text + colour_reset

def allowed_option_key(text):

	return colour_yellow_fg + colour_bright + colour_dark_grey_bg + text + colour_reset

def calc_line_item_width(index, text):

	return len(str(index) + text)

def generate_menu_line_item(index, text):

	return (' ' * prebox_space) + colours_menu_box + '│' + (' ' * row_index_space) + '(' + allowed_item_key(str(index)) + colour_reset + colours_menu_box + ')' + (' ' * row_item_space) + text + (' ' * (box_width - calc_line_item_width(index, text) - row_min_length)) + (' ' * row_trailing_space) + '│' + colour_reset

def generate_menu_line_option(char, text):

	return (' ' * prebox_space) + colours_menu_box + '│' + (' ' * row_index_space) + '(' + allowed_option_key(char) + colour_reset + colours_menu_box + ')' + (' ' * row_item_space) + text + (' ' * (box_width - calc_line_item_width(char, text) - row_min_length)) + (' ' * row_trailing_space) + '│' + colour_reset

def generate_menu_lines(title, records, record_index, options, prompt_template):
	global box_width, prebox_space, row_index_space, row_item_space, row_trailing_space, row_min_length

	index = 0
	row_index_space = 1		# space between the left border and the index parentheses
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
		item_width = calc_line_item_width(index, record[record_index])
		if (item_width + row_min_length) > box_width: box_width = item_width + row_min_length

	prompt_length = (len(options) + 1) * 5							# each option char also has 4 other chars i.e. ' or S' = 5 chars
	prompt_length += len(prompt_template) - 2	 					# subtract placeholder chars {}
	if index > 0: prompt_length += len('1 to ' + str(index + 1))	# add length of index chars from '1 to n'
	prompt_length += 3							 					# number of chars to allow for user input
	prompt_length -= prebox_space

	if title_min_length > box_width: box_width = title_min_length
	if prompt_length > box_width: box_width = prompt_length

	if title:
		menu_header = (' ' * prebox_space) + colours_menu_box + '┌' + ('─' * title_left_border) + '┤' + (' ' * title_space) + colours_menu_title + title + colour_reset + colours_menu_box + (' ' * title_space) + '├' + '─' * (box_width - title_min_length) + '┐' + colour_reset
		menu_separator = (' ' * prebox_space) + colours_menu_box + '├' + ('─' * (box_width - 2)) + '┤' + colour_reset
		menu_footer = (' ' * prebox_space) + colours_menu_box + '└' + ('─' * (box_width - 2)) + '┘' + colour_reset
	else:
		menu_header = (' ' * prebox_space) + colours_menu_box + '┌' + ('─' * (box_width - 2)) + '┐' + colour_reset
		menu_separator = ''
		menu_footer = (' ' * prebox_space) + colours_menu_box + '└' + ('─' * (box_width - 2)) + '┘' + colour_reset

	return menu_header, menu_separator, menu_footer

def get_screen_size():
	rows_str, columns_str = os.popen('stty size', 'r').read().split()

	return int(rows_str), int(columns_str)

def write_entry_to_file(entry_name, entry_fields):
	output_pathfile = entry_name.replace(' ', '_').replace('/', '_').replace('\\', '_').replace('?', '_')
	output_pathfile += '.txt'
	text = ''

	for field in entry_fields:
		if field['type_id']:
			if text: text += '\n'
			field_name_line, field_value_line = generate_field_file(field['name'], field['value'])
			text += field_name_line + field_value_line
		else:
			# appears that notes don't have a field type ID
			text = field['value']
			break

	if not os.path.exists(output_pathfile):
		with open(output_pathfile, 'w') as text_file:
			text_file.write(text + '\n')

		print(" * {} *".format(colour_green_bright + 'written to file' + colour_reset))
	else:
		print(" ! {} !".format(colour_red_bright + 'could not write (file already exists)' + colour_reset))

	return

def clear_display():
	print('\033c')
	print(' ' * 2 + script_details + '\n')

	return

def get_db_favorites():
	con = lite.connect(database_pathfile)

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute('SELECT * FROM entries WHERE is_favorite = \"1\"')

	return cur.fetchall()

def get_db_search(text):
	con = lite.connect(database_pathfile)

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute('SELECT * FROM fields JOIN entries ON fields.entry_id = entries.id WHERE value LIKE ?', ('%' + text + '%',))

	return cur.fetchall()

def get_db_fields_from_entry(entry_id):
	con = lite.connect(database_pathfile)

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()

		# try joining fields to field types first. This will return none for notes as they don't have a field type set.
		cur.execute('SELECT * FROM fields JOIN types ON fields.type_id = types.id WHERE entry_id = ?', (entry_id,))
		result = cur.fetchall()

		if len(result) == 0:		# this may be a note, so try query again without join
			cur.execute('SELECT * FROM fields WHERE entry_id = ?', (entry_id,))
			result = cur.fetchall()

	return result

def get_db_entries_from_category(category_id):
	con = lite.connect(database_pathfile)

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute('SELECT * FROM entries WHERE category_id = ? ORDER BY name', (category_id,))

	return cur.fetchall()

def get_db_categories():
	con = lite.connect(database_pathfile)

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute('SELECT id, name FROM categories ORDER BY name')

	return cur.fetchall()

def db_exists():
	if os.path.exists(database_pathfile):
		return True
	else:
		print('\n! File not found! [{}]'.format(database_pathfile))
		return False

def generate_field_screen(name, value, columns):
	name_border = 2		# number of spaces between left side of screen and name display
	value_border = 6	# number of spaces between left side of screen and value display
	name_line = (' ' * name_border) + name + ':' + (' ' * (columns - name_border - len(name) - 1))
	value_line = (' ' * value_border) + value + (' ' * (columns - value_border - len(value)))
	name_coloured = colours_single_entry_name + name_line + colour_reset
	value_coloured = colours_single_entry_value + value_line + colour_reset

	return name_coloured + value_coloured

def generate_field_file(name, value):
	value_border = 8

	name_line = name + ':\n'
	value_line = (' ' * value_border) + value

	return name_line, value_line

def generate_single_entry_screen(entry_name, entry_fields):
	rows, columns = get_screen_size()
	header = colours_single_entry_header + ('═' * 8) + '╣ ' + colours_single_entry_title + entry_name + colour_reset + colours_single_entry_header + ' ╠' + '═' * (columns - 8 - 4 - len(entry_name)) + colour_reset
	content = ''
	footer = colours_single_entry_footer + ('═' * columns) + colour_reset

	for field in entry_fields:
		if field['type_id']:
			if content: content += '\n'
			content += generate_field_screen(field['name'], field['value'], columns)
		else:
			# appears that notes don't have a field type ID
			content = field['value'] + '\n'
			break

	return header + content + footer

def check_opts(argv):
	global database_pathfile

	database_pathfile = ''
	help_message = '\nUsage: ./' + script_file + ' -i [inputfile]'

	try:
		opts, args = getopt.getopt(argv,'hvi:',['help','version','input-file='])
	except getopt.GetoptError:
		print(help_message)
		return 2

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			print(help_message)
			return 1
		elif opt in ('-v', '--version'):
			return 1
		elif opt in ('-i', '--input-file'):
			database_pathfile = arg

	if not database_pathfile:
		print(help_message)
		return 2

	if not db_exists(): return 3

	return 0

def main(argv):
	print(script_details)

	result = check_opts(argv)

	if result > 0: return result

	all_categories = get_db_categories()
	menu_stack = []
	current_menu = 'categories'

	while True:
		if current_menu == 'categories':
			clear_display()
			category_index = draw_menu('categories', all_categories, 'name', 'SF', False)
			menu_stack.append(current_menu)

			if category_index == -2:
				current_menu = 'search'
			elif category_index == -3:
				current_menu = 'favorites'
			else:
				current_menu = 'entries'

		if current_menu == 'entries':
			category_row = all_categories[int(category_index) - 1]
			category_entries = get_db_entries_from_category(category_row['id'])
			clear_display()
			entry_index = draw_menu(category_row['name'], category_entries, 'name', 'SBF', False)

			if entry_index == 0:
				current_menu = menu_stack.pop()
			elif entry_index == -2:
				menu_stack.append(current_menu)
				current_menu = 'search'
			elif entry_index == -3:
				menu_stack.append(current_menu)
				current_menu = 'favorites'
			else:
				entry_row = category_entries[int(entry_index) - 1]
				entry_id = entry_row['id']
				menu_stack.append(current_menu)
				current_menu = 'fields'

		if current_menu == 'search':
			try:
				search_text = input(' ' * 3 + 'enter search text: ')
				current_menu = 'search results'
			except KeyboardInterrupt:
				current_menu = menu_stack.pop()

		if current_menu == 'search results':
			search_entries = get_db_search(search_text)
			clear_display()
			entry_index = draw_menu('Search results for \"' + search_text + '\"', search_entries, 'name', 'B', False)

			if entry_index == 0:
				current_menu = menu_stack.pop()
			else:
				entry_row = search_entries[int(entry_index) - 1]
				entry_id = entry_row['entry_id']
				menu_stack.append(current_menu)
				current_menu = 'fields'

		if current_menu == 'favorites':
			favorites_entries = get_db_favorites()
			clear_display()
			favorite_index = draw_menu('Favorites', favorites_entries, 'name', 'B', False)

			if favorite_index == 0:
				current_menu = menu_stack.pop()
			else:
				entry_row = favorites_entries[int(favorite_index) - 1]
				entry_id = entry_row['id']
				menu_stack.append(current_menu)
				current_menu = 'fields'

		if current_menu == 'fields':
			entry_name = entry_row['name']
			entry_fields = get_db_fields_from_entry(entry_id)
			content_text = generate_single_entry_screen(entry_name, entry_fields)

			clear_display()
			print(content_text)
			print()

			prompt_only = False

			while True:
				user_selection = draw_menu('', '', '', 'WB', prompt_only)

				if user_selection == -1:
					write_entry_to_file(entry_name, entry_fields)
					print()
					prompt_only = True
				elif user_selection == 0:
					current_menu = menu_stack.pop()
					break

if __name__ == '__main__':
	result = main(sys.argv[1:])
	exit(result)

