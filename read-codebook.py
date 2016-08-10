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

script_details = 'read-codebook.py (2016-08-11)'

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

def menu(title, records, mode):
	total = len(records)

	if title:
		header_template = '────────┤ {} ├────────'
		header_line = header_template.format(colour_white_bright + title + colour_reset)
		separator_line = ' ├' + '─' * (len(header_template) - 2 + len(title))
		footer_line = ' └' + '─' * (len(header_template) - 2 + len(title))
	else:
		header_template = '────────────────────────────'
		header_line = header_template
		separator_line = ' ├' + '─' * (len(header_template))
		footer_line = ' └' + '─' * (len(header_template))

	while True:
		print(' ┌' + header_line)

		for index, record in enumerate(records):
			print(" │ ({}) {}".format(colour_yellow_bright + str(index + 1) + colour_reset, record[db_col_name]))

		if total > 0:
			prompt_head = colour_yellow_bright + '1' + colour_reset + ' to ' + colour_yellow_bright + str(total) + colour_reset + ' or '
			print(separator_line)
		else:
			prompt_head = ''

		if mode == 'B':
			print(" │ ({}) <{}>".format(colour_yellow_bright + 'B' + colour_reset, 'Back'))
			prompt_tail = colour_yellow_bright + 'B' + colour_reset
		elif mode == 'W':
			print(" │ ({}) <{}>".format(colour_yellow_bright + 'W' + colour_reset, 'Write to a text file'))
			print(" │ ({}) <{}>".format(colour_yellow_bright + 'B' + colour_reset, 'Back'))
			prompt_tail = colour_yellow_bright + 'W' + colour_reset + ',' + colour_yellow_bright + 'B' + colour_reset
		else:
			print(" │ ({}) <{}>".format(colour_yellow_bright + 'Q' + colour_reset, 'Quit'))
			prompt_tail = colour_yellow_bright + 'Q' + colour_reset

		print(footer_line)
		user_selection = input('   select (' + prompt_head + prompt_tail + '): ')
		print()

		# choose permissible actions based on 'mode'
		if not user_selection.isdigit():
			if mode == 'B':
				if user_selection == 'B' or user_selection == 'b':
					user_selection = 0
					break
			elif mode == 'W':
				if user_selection == 'W' or user_selection == 'w':
					user_selection = -1
					break
				elif user_selection == 'B' or user_selection == 'b':
					user_selection = 0
					break
			elif mode == 'Q':
				if user_selection == 'Q' or user_selection == 'q':
					user_selection = 0
					break
		else:
			if int(user_selection) > 0 and int(user_selection) <= total:
				break
			
	return user_selection

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
			user_selection = menu(db_name_categories, db_tab_categories, 'Q')

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
					user_selection = menu(db_category, db_tab_entry, 'B')

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

						print()
						entry_display_template = '════════╣ {} ╠════════'
						entry_display = entry_display_template.format(colour_white_bright + db_entry + colour_reset)
						print(entry_display)
						print(content)
						print('═' * (len(entry_display_template) - 2 + len(db_entry)))
						print()

						# single entry loop
						while True:
							# query user
							user_selection = menu('', '', 'W')

							if user_selection == -1:
								write_entry_to_file(db_entry, content)
							elif user_selection == 0:
								break

if __name__ == '__main__':
	main(sys.argv[1:])
