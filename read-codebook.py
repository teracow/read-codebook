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
script_date = '2016-08-16'

# text colours
colour_white_fg = '\033[97m'
colour_light_fg = '\033[38;5;250m'
colour_yellow_fg = '\033[33;40m'
colour_green_fg = '\033[32;40m'
colour_red_fg = '\033[31;40m'

# background colours
colour_grey_fg = '\033[38;5;246m'
colour_orange_fg = '\033[38;5;214m'
colour_dark_grey_bg = '\033[48;5;234m'

# colour modifiers
colour_bold = '\033[1m'
colour_reset = '\033[0m'

# colour scheme
colours_menu_box = colour_light_fg + colour_dark_grey_bg
colours_menu_title = colour_orange_fg + colour_bold + colour_dark_grey_bg
colours_menu_item = colour_light_fg + colour_dark_grey_bg

colours_single_entry_title = colour_white_fg + colour_bold + colour_dark_grey_bg
colours_single_entry_header = colour_grey_fg + colour_dark_grey_bg
colours_single_entry_name = colour_light_fg + colour_dark_grey_bg
colours_single_entry_value = colour_orange_fg + colour_dark_grey_bg
colours_single_entry_footer = colour_grey_fg + colour_dark_grey_bg

colours_prompt = colour_light_fg + colour_bold

script_details = '{} ({})'.format(colour_light_fg + colour_bold + script_file + colour_reset, script_date)

colours_write_ok = colour_green_fg + colour_bold
colours_write_fail = colour_red_fg + colour_bold

prebox_space = 1        # space before left border

def draw_menu(title, table, column, options, prompt_only = False):
    global box_width

    box_width = len(script_file) + len(script_date) + 5
    # Set a minimum menu box size - this is the overall width including box chars.
    # Note! menu option messages such as 'Write to text file' are not length tested!
    # This must be allowed for when adjusting this figure.

    display_menu = True
    total = len(table)
    header, separator, footer = generate_menu_lines(title, table, column)
    if prompt_only: display_menu = False

    while True:
        if display_menu:
            print(header)

            for index, record in enumerate(table):
                print(generate_menu_line_item(index + 1, record[column]))

            if total > 0: print(separator)
            if 'S' in options: print(generate_menu_line_option('S', 'Search'))
            if 'W' in options: print(generate_menu_line_option('W', 'Write to text file'))
            if 'F' in options: print(generate_menu_line_option('F', 'Favorites'))
            if 'M' in options: print(generate_menu_line_option('M', 'Main menu'))
            if 'B' in options: print(generate_menu_line_option('B', 'Back'))

            print(generate_menu_line_option('Q', 'Quit'))
            print(footer)
            print()

        try:
            user_selection = input(generate_menu_prompt())
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

            if 'W' in options:
                if user_selection.upper() == 'W':
                    user_selection = -1
                    break

            if 'S' in options:
                if user_selection.upper() == 'S':
                    user_selection = -2
                    break

            if 'F' in options:
                if user_selection.upper() == 'F':
                    user_selection = -3
                    break

            if 'M' in options:
                if user_selection.upper() == 'M':
                    user_selection = -4
                    break

        display_menu = False            # for any other char - only re-show prompt

    return user_selection

def generate_menu_lines(title, records, record_index):
    global box_width, prebox_space, row_index_space, row_item_space, row_trailing_space, row_min_length

    index = 0
    row_index_space = 1     # space between the left border and the index parentheses
    row_item_space = 1      # space between index parentheses and the displayed item
    row_trailing_space = 1  # space between item and right border
    row_min_length = row_index_space + 2 + row_item_space + row_trailing_space + 2      # 2 x parentheses and 2 x box chars

    title_left_border = 4   # chars from left border to start of title bookend
    title_box_chars = 4     # number of fixed characters needed to form title
    title_space = 1         # space between bookends and title on left and right
    title_extra_spaces = title_space * 2
    title_min_length = len(title) + title_box_chars + title_extra_spaces + title_left_border

    # find longest display item so box width can be recalculated
    for index, record in enumerate(records):
        item_width = calc_line_item_width(index, record[record_index])
        if (item_width + row_min_length) > box_width: box_width = item_width + row_min_length

    if title_min_length > box_width: box_width = title_min_length

    if title:
        menu_header = (' ' * prebox_space) + colours_menu_box + '┌' + ('─' * title_left_border) + '┤' + (' ' * title_space) + colours_menu_title + title + colour_reset + colours_menu_box + (' ' * title_space) + '├' + '─' * (box_width - title_min_length) + '┐' + colour_reset
        menu_separator = (' ' * prebox_space) + colours_menu_box + '├' + ('─' * (box_width - 2)) + '┤' + colour_reset
        menu_footer = (' ' * prebox_space) + colours_menu_box + '└' + ('─' * (box_width - 2)) + '┘' + colour_reset
    else:
        menu_header = (' ' * prebox_space) + colours_menu_box + '┌' + ('─' * (box_width - 2)) + '┐' + colour_reset
        menu_separator = ''
        menu_footer = (' ' * prebox_space) + colours_menu_box + '└' + ('─' * (box_width - 2)) + '┘' + colour_reset

    return menu_header, menu_separator, menu_footer

def generate_menu_line_item(index, text):

    return (' ' * prebox_space) + colours_menu_box + '│' + (' ' * row_index_space) + '(' + allowed_item_key(str(index)) + colour_reset + colours_menu_box + ')' + (' ' * row_item_space) + colours_menu_item + text + (' ' * (box_width - calc_line_item_width(index, text) - row_min_length)) + (' ' * row_trailing_space) + colour_reset + colours_menu_box + '│' + colour_reset

def generate_menu_line_option(char, text):

    return (' ' * prebox_space) + colours_menu_box + '│' + (' ' * row_index_space) + '(' + allowed_option_key(char) + colour_reset + colours_menu_box + ')' + (' ' * row_item_space) + text + (' ' * (box_width - calc_line_item_width(char, text) - row_min_length)) + (' ' * row_trailing_space) + '│' + colour_reset

def calc_line_item_width(index, text):

    return len(str(index) + text)

def generate_menu_prompt():

    return (' ' * prebox_space) + colours_prompt + ' select:' + colour_reset + ' '

def generate_search_prompt():

    return (' ' * prebox_space) + colours_prompt + ' enter text to search for: ' + colour_reset + ' '

def allowed_item_key(text):

    return colour_orange_fg + colour_bold + colour_dark_grey_bg + text + colour_reset

def allowed_option_key(text):

    return colour_yellow_fg + colour_bold + colour_dark_grey_bg + text + colour_reset

def get_screen_size():
    rows_str, columns_str = os.popen('stty size', 'r').read().split()

    return int(rows_str), int(columns_str)

def reset_display():
    print('\033c')
    print((' ' * prebox_space) + ' ' + script_details + '\n')

    return

def get_db_categories():
    con = lite.connect(database_pathfile)
    base_sql = 'SELECT  id          AS category_id,\
                        name        AS category_name\
                FROM categories '

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute(base_sql + 'ORDER BY category_name')

    return cur.fetchall()

def get_db_entries_from_category(category_id):
    con = lite.connect(database_pathfile)
    base_sql = 'SELECT  categories.id       AS category_id,\
                        categories.name     AS category_name,\
                        entries.id          AS entry_id,\
                        entries.name        AS entry_name,\
                        entries.type        AS entry_type\
                FROM categories\
                        JOIN entries        ON entries.category_id = categories.id '

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute(base_sql + 'WHERE category_id = ? ORDER BY entry_name', (category_id,))

    return cur.fetchall()

def get_db_fields_from_entry(entry_id):
    con = lite.connect(database_pathfile)
    base_sql = 'SELECT  entry_id,\
                        entries.name        AS entry_name,\
                        entries.type        AS entry_type,\
                        entries.is_favorite AS favorite,\
                        types.name          AS field_name,\
                        fields.value,\
                        types.mode          AS data_type\
                FROM entries\
                        JOIN fields         ON fields.entry_id = entries.id\
                LEFT    JOIN types          ON types.id = fields.type_id '

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute(base_sql + 'WHERE entry_id = ?', (entry_id,))

    return cur.fetchall()

def get_db_search(text):
    con = lite.connect(database_pathfile)
    base_sql = 'SELECT  entries.id          AS entry_id,\
                        entries.name        AS entry_name,\
                        entries.type        AS entry_type,\
                        fields.value\
                FROM entries\
                        JOIN fields         ON fields.entry_id = entries.id\
                LEFT    JOIN types          ON types.id = fields.type_id '

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute(base_sql + 'WHERE value LIKE ?', ('%' + text + '%',))

    return cur.fetchall()

def get_db_favorites():
    con = lite.connect(database_pathfile)
    base_sql = 'SELECT  entries.id          AS entry_id,\
                        entries.name        AS entry_name,\
                        entries.type        AS entry_type,\
                        entries.is_favorite AS favorite\
                FROM entries '

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute(base_sql + 'WHERE favorite = 1 ORDER BY entry_name')

    return cur.fetchall()

def generate_single_entry_screen(entry_name, entry_fields):
    rows, columns = get_screen_size()
    header = colours_single_entry_header + ('═' * 8) + '╣ ' + colours_single_entry_title + entry_name + colour_reset + colours_single_entry_header + ' ╠' + '═' * (columns - 8 - 4 - len(entry_name)) + colour_reset
    content = ''
    footer = colours_single_entry_footer + ('═' * columns) + colour_reset

    for field in entry_fields:
        if field['data_type'] == 'note' or field['entry_type'] == 1:
            content += generate_note_screen(field['value'], columns)
            break
        elif field['entry_type'] == 0:
            content += generate_field_screen(field['field_name'], field['value'], columns)
        else:
            content += generate_note_screen(field['value'], columns)
            break

    return header + content + footer

def generate_note_screen(value, columns):
    name = 'Note'
    name_border = 2     # spaces between left side of screen and name display
    value_border = 6    # spaces between left side of screen and value display
    name_line = (' ' * name_border) + name + ':' + (' ' * (columns - name_border - len(name) - 1))
    value_line = ''

    for line in value.splitlines():
        value_line += (' ' * value_border) + line + (' ' * (columns - value_border - len(line)))

    name_coloured = colours_single_entry_name + name_line + colour_reset
    value_coloured = colours_single_entry_value + value_line + colour_reset

    return name_coloured + value_coloured

def generate_field_screen(name, value, columns):
    name_border = 2     # spaces between left side of screen and name display
    value_border = 6    # spaces between left side of screen and value display
    name_line = (' ' * name_border) + name + ':' + (' ' * (columns - name_border - len(name) - 1))
    value_line = (' ' * value_border) + value + (' ' * (columns - value_border - len(value)))
    name_coloured = colours_single_entry_name + name_line + colour_reset
    value_coloured = colours_single_entry_value + value_line + colour_reset

    return name_coloured + value_coloured

def generate_note_file(value):
    value_line = ''

    for line in value.splitlines():
        value_line += line + '\n'

    return value_line

def generate_field_file(name, value):
    name_line = name + ':\n'
    value_line = value + '\n\n'

    return name_line + value_line

def write_entry_to_file(entry_name, entry_fields):
    output_pathfile = entry_name.replace(' ', '_').replace('/', '_').replace('\\', '_').replace('?', '_')
    output_pathfile += '.txt'
    content = ''

    for field in entry_fields:
        if field['data_type'] == 'note' or field['entry_type'] == 1:
            content += generate_note_file(field['value'])
            break
        elif field['entry_type'] == 0:
            content += generate_field_file(field['field_name'], field['value'])
        else:
            content += generate_note_file(field['value'])
            break

    if not os.path.exists(output_pathfile):
        with open(output_pathfile, 'w') as text_file:
            text_file.write(content)

        print(" * {} *\n".format(colours_write_ok + 'written to file' + colour_reset))
    else:
        print(" ! {} !\n".format(colours_write_fail + 'could not write (file already exists)' + colour_reset))

    return

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

def db_exists():
    if os.path.exists(database_pathfile):
        return True
    else:
        print('\n! File not found! [{}]'.format(database_pathfile))
        return False

def main(argv):
    print(script_details)

    result = check_opts(argv)

    if result > 0: return result

    all_categories = get_db_categories()
    menu_stack = []
    current_menu = 'categories'

    while True:
        if current_menu == 'categories':
            reset_display()
            category_menu_index = draw_menu('categories', all_categories, 'category_name', 'SF')
            menu_stack.append(current_menu)

            if category_menu_index == -2:
                current_menu = 'search'
            elif category_menu_index == -3:
                current_menu = 'favorites'
            else:
                current_menu = 'entries'

        if current_menu == 'entries':
            category_row = all_categories[int(category_menu_index) - 1]
            category_entries = get_db_entries_from_category(category_row['category_id'])
            reset_display()
            entry_menu_index = draw_menu(category_row['category_name'], category_entries, 'entry_name', 'SBFM')

            if entry_menu_index == 0:
                current_menu = menu_stack.pop()
            elif entry_menu_index == -2:
                menu_stack.append(current_menu)
                current_menu = 'search'
            elif entry_menu_index == -3:
                menu_stack.append(current_menu)
                current_menu = 'favorites'
            elif entry_menu_index == -4:
                menu_stack = []
                current_menu = 'categories'
            else:
                entry_row = category_entries[int(entry_menu_index) - 1]
                menu_stack.append(current_menu)
                current_menu = 'fields'

        if current_menu == 'search':
            try:
                search_text = input(generate_search_prompt())
                current_menu = 'search results'
            except KeyboardInterrupt:
                current_menu = menu_stack.pop()

        if current_menu == 'search results':
            search_entries = get_db_search(search_text)
            reset_display()
            search_menu_index = draw_menu('Search results for \"' + search_text + '\"', search_entries, 'entry_name', 'BM')

            if search_menu_index == 0:
                current_menu = menu_stack.pop()
            elif search_menu_index == -4:
                menu_stack = []
                current_menu = 'categories'
            else:
                entry_row = search_entries[int(search_menu_index) - 1]
                menu_stack.append(current_menu)
                current_menu = 'fields'

        if current_menu == 'favorites':
            favorites_entries = get_db_favorites()
            reset_display()
            favorite_menu_index = draw_menu('Favorites', favorites_entries, 'entry_name', 'BM')

            if favorite_menu_index == 0:
                current_menu = menu_stack.pop()
            elif favorite_menu_index == -4:
                menu_stack = []
                current_menu = 'categories'
            else:
                entry_row = favorites_entries[int(favorite_menu_index) - 1]
                menu_stack.append(current_menu)
                current_menu = 'fields'

        if current_menu == 'fields':
            entry_id = entry_row['entry_id']
            entry_name = entry_row['entry_name']
            entry_fields = get_db_fields_from_entry(entry_id)
            content = generate_single_entry_screen(entry_name, entry_fields)

            reset_display()
            print(content + '\n')

            prompt_only = False

            while True:
                fields_menu_index = draw_menu('', '', '', 'BWM', prompt_only)

                if fields_menu_index == 0:
                    current_menu = menu_stack.pop()
                    break
                elif fields_menu_index == -1:
                    write_entry_to_file(entry_name, entry_fields)
                    prompt_only = True
                elif fields_menu_index == -4:
                    menu_stack = []
                    current_menu = 'categories'
                    break

if __name__ == '__main__':
    result = main(sys.argv[1:])
    exit(result)

