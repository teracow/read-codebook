#!/usr/bin/python3
# -*- coding: utf-8 -*-

# read-codebook.py

# Copyright (C) 2016 Teracow Software

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

# If you find this code useful, please let me know. :) teracow@gmail.com

# Traverse the codebook dB structure and locate individual entries

import sqlite3 as lite
import sys, getopt

script_details = 'read-codebook.py (2016-08-09)'
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

def menu(title, items, option):
	while True:
		print()
		print("*** {} ***".format(title))

		acc = 0
		for record in items:
			acc += 1
			print(" ({}) {}".format(acc, record[db_col_name]))

		if option == 'B':
			print(" (B) <Back>")
			print()
			prompt = 'Select ( 1 - ' + str(acc) + ' or B ): '
		else:
			print(" (Q) <Quit>")
			print()
			prompt = 'Select ( 1 - ' + str(acc) + ' or Q ): '

		user_selection = input(prompt)

		if not user_selection.isdigit():
			user_selection = 0
			break
			
		if int(user_selection) <= acc:
			break
			
	return user_selection

def main(argv):
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

						for field in db_tab_fields:
							if field[db_col_type_id]:
								for field_types in db_tab_types:
									if field_types[db_col_id] == field[db_col_type_id]:
										print(" {:30}: {}".format(field_types[db_col_name], field[db_col_value]))
										break
							else:
									# appears that notes don't have a field type ID
									print("{}".format(field[db_col_value]))


if __name__ == '__main__':
	main(sys.argv[1:])
