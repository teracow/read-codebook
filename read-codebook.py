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

script_details = 'read-codebook.py (2016-08-10)'
db_name_categories = 'categories'
db_name_entries = 'entries'
db_name_fields = 'fields'
db_name_types = 'types'						# field data types - password, email, number, etc ...
db_col_id = 'id'
db_col_category_id = 'category_id'
db_col_entry_id = 'entry_id'
db_col_name = 'name'
db_col_value = 'value'
db_col_type_id = 'type_id'

def menu(title, records, mode):
	total = len(records)

	while True:
		print()
		
		if title:
			print(" --- {} ---".format(title))

		for index, record in enumerate(records):
			print(" ({}) {}".format(index + 1, record[db_col_name]))

		if total > 0:
			prompt_head = '1 to ' + str(total) + ' or '
		else:
			prompt_head = ''
			
		if mode == 'B':
			print(" (B) <Back>")
			prompt_tail = 'B'
		elif mode == 'W':
			print(" (W) <Write this to a file>")
			print(" (B) <Back>")
			prompt_tail = 'W,B'
		else:
			print(" (Q) <Quit>")
			prompt_tail = 'Q'

		print()
		user_selection = input(' Select (' + prompt_head + prompt_tail + '): ')

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

def write_entry_to_file(db_entry):
	# yes, ugly, but hopefully catches the important ones ... I'll prettify it later
	safername = db_entry.replace(' ', '_')
	safername = safername.replace('/', '_')
	safername = safername.replace('\\', '_')
	safername = safername.replace('?', '_')
	outpathfile = safername + '.txt'

	print()
	if not os.path.exists(outpathfile):
		with open(outpathfile, 'w') as text_file:
			for field in db_tab_fields:
				if field[db_col_type_id]:
					for field_types in db_tab_types:
						if field_types[db_col_id] == field[db_col_type_id]:
							text_file.write("{}:\n\t{}\n".format(field_types[db_col_name], field[db_col_value]))
							break
				else:
						# appears that notes don't have a field type ID
						text_file.write(field[db_col_value] + '\n')
		print(" * entry written to file *")
	else:
		print(" ! could not write as file already exists !")
	
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

						print()
						print(" ------> entry: {} <------".format(db_entry))

						for field in db_tab_fields:
							if field[db_col_type_id]:
								for field_types in db_tab_types:
									if field_types[db_col_id] == field[db_col_type_id]:
										print(" {}:\n\t{}\n".format(field_types[db_col_name], field[db_col_value]))
										break
							else:
									# appears that notes don't have a field type ID
									print("{}".format(field[db_col_value]))

						while True:
							# query user
							user_selection = menu('', '', 'W')

							if user_selection == -1:
								write_entry_to_file(db_entry)
							elif user_selection == 0:
								break

if __name__ == '__main__':
	main(sys.argv[1:])
