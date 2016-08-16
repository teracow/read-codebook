#!/usr/bin/python3
# -*- coding: utf-8 -*-
# line wraps @ 99 chars

# read-codebook.py

# Traverse the codebook dB structure and locate individual entries

# Copyright (C) 2016 Teracow Software

# This program is free software: you can redistribute it and/or modify it under the terms of the
#   GNU General Public License as published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#   even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#   General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program. If
#   not, see http://www.gnu.org/licenses/.

# If you find this code useful, please let me know. :) teracow@gmail.com

import os
import sys
import getopt
import sqlite3 as lite

SCRIPT_FILE = 'read-codebook.py'
SCRIPT_DATE = '2016-08-16'

# text colours
COLOUR_WHITE_FG = '\033[97m'
COLOUR_LIGHT_FG = '\033[38;5;250m'
COLOUR_YELLOW_FG = '\033[33;40m'
COLOUR_GREEN_FG = '\033[32;40m'
COLOUR_RED_FG = '\033[31;40m'
COLOUR_GREY_FG = '\033[38;5;246m'
COLOUR_ORANGE_FG = '\033[38;5;214m'

# background colours
COLOUR_DARK_GREY_BG = '\033[48;5;234m'

# colour modifiers
COLOUR_BOLD = '\033[1m'
COLOUR_RESET = '\033[0m'

# colour scheme
colours_menu_box = COLOUR_LIGHT_FG + COLOUR_DARK_GREY_BG
colours_menu_title_item = COLOUR_ORANGE_FG + COLOUR_BOLD + COLOUR_DARK_GREY_BG
colours_menu_title_function = COLOUR_YELLOW_FG + COLOUR_BOLD + COLOUR_DARK_GREY_BG
colours_menu_item = COLOUR_LIGHT_FG + COLOUR_DARK_GREY_BG

colours_single_entry_box = COLOUR_GREY_FG + COLOUR_DARK_GREY_BG
colours_single_entry_title = COLOUR_WHITE_FG + COLOUR_BOLD + COLOUR_DARK_GREY_BG
colours_single_entry_header = COLOUR_GREY_FG + COLOUR_DARK_GREY_BG
colours_single_entry_name = COLOUR_LIGHT_FG + COLOUR_DARK_GREY_BG
colours_single_entry_value = COLOUR_ORANGE_FG + COLOUR_DARK_GREY_BG

colours_prompt = COLOUR_LIGHT_FG + COLOUR_BOLD

colours_write_ok = COLOUR_GREEN_FG + COLOUR_BOLD
colours_write_fail = COLOUR_RED_FG + COLOUR_BOLD

BOX_POSITION = 'center'         # 'left', 'center' or 'right' of screen
BOX_INDENT = 1                  # space from side of screen to box
BOX_TITLE_INDENT = 4            # chars from left border to start of title bookend
TITLE_SPACING = 1               # space between bookends and title on left and right
MENU_ITEM_INDENT = 1            # space between the left border and the index parentheses
MENU_ITEM_GAP = 1               # space between index parentheses and the displayed item
MENU_ITEM_TAIL = 1              # space between item and right border
PROMPT_INDENT = 1               # from left of box to start of prompt
ENTRY_NAME_INDENT = 1           # from left of box to name
ENTRY_VALUE_INDENT = 4          # from left of box to value

# initial values
box_left = 0                    # calculated later on depending on BOX_POSITION
box_with = 0                    # calculated later on depending on widest item in display

# these are only used for calculation
BOX_TITLE_CHARS_LENGTH = 4      # characters needed to form title row
BOX_VERTICAL_CHARS_LENGTH = 2   # characters needed to form vertical sides of box
BOX_FOOTER_CHARS_LENGTH = 2     # characters needed to form footer

row_min_length = MENU_ITEM_INDENT + 2 + MENU_ITEM_GAP + MENU_ITEM_TAIL + 2      # 2 x parentheses
                                                                                # and 2 x box chars

SCRIPT_DETAILS = '{} ({})'.format(COLOUR_LIGHT_FG + COLOUR_BOLD + SCRIPT_FILE + COLOUR_RESET,
                                    SCRIPT_DATE)

def draw_menu(title, table, column, options, prompt_only = False, function = False):
    # function = False   : menu title will be shown in colour = colours_menu_title_item
    # function = True    : menu title will be shown in colour = colours_menu_title_function

    display_menu = True
    total = len(table)
    header, separator, footer = generate_menu_lines(title, table, column, function)
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

        display_menu = False    # for any other char - only re-show prompt

    return user_selection

def calc_box_width(records, record_index):
    global box_width

    box_width = 31              # minimum box width

    for index, record in enumerate(records):
        item_width = calc_line_item_width(index, record[record_index])
        if (item_width + row_min_length) > box_width: box_width = item_width + row_min_length

    return

def calc_box_left():
    global box_left

    if BOX_POSITION == 'left':
        box_left = BOX_INDENT
    elif BOX_POSITION == 'center':
        rows, columns = get_screen_size()
        box_left = (columns // 2) - (box_width // 2)
    else:
        rows, columns = get_screen_size()
        box_left = columns - BOX_INDENT - box_width

    return

def generate_menu_lines(title, records, record_index, function = False):
    global box_width

    index = 0
    row_min_length = MENU_ITEM_INDENT + 2 + MENU_ITEM_GAP + MENU_ITEM_TAIL\
                    + BOX_VERTICAL_CHARS_LENGTH

    title_min_length = len(title) + BOX_TITLE_CHARS_LENGTH + (TITLE_SPACING * 2) + BOX_TITLE_INDENT
    calc_box_width(records, record_index)
    calc_box_left()

    if function == True:
        title_colour = colours_menu_title_function
    else:
        title_colour = colours_menu_title_item

    if title_min_length > box_width: box_width = title_min_length

    if title:
        menu_header = (' ' * (box_left
                        + ((box_width // 2) - ((len(SCRIPT_FILE) + len(SCRIPT_DATE) + 3) // 2))))\
                        + SCRIPT_DETAILS + '\n\n'

        menu_header += (' ' * box_left) + colours_menu_box + '┌' + ('─' * BOX_TITLE_INDENT)\
                        + '┤' + (' ' * TITLE_SPACING) + title_colour + title + COLOUR_RESET\
                        + colours_menu_box + (' ' * TITLE_SPACING) + '├'\
                        + ('─' * (box_width - title_min_length)) + '┐' + COLOUR_RESET

        menu_separator = (' ' * box_left) + colours_menu_box + '├'\
                        + ('─' * (box_width - BOX_VERTICAL_CHARS_LENGTH)) + '┤' + COLOUR_RESET

        menu_footer = (' ' * box_left) + colours_menu_box + '└'\
                        + ('─' * (box_width - BOX_VERTICAL_CHARS_LENGTH)) + '┘' + COLOUR_RESET
    else:
        menu_header = (' ' * box_left) + colours_menu_box + '┌'\
                        + ('─' * (box_width - BOX_VERTICAL_CHARS_LENGTH)) + '┐' + COLOUR_RESET

        menu_separator = ''

        menu_footer = (' ' * box_left) + colours_menu_box + '└'\
                        + ('─' * (box_width - BOX_VERTICAL_CHARS_LENGTH)) + '┘' + COLOUR_RESET

    return menu_header, menu_separator, menu_footer

def generate_menu_line_item(index, text):

    return (' ' * box_left) + colours_menu_box + '│' + (' ' * MENU_ITEM_INDENT) + '('\
            + allowed_item_key(str(index)) + COLOUR_RESET + colours_menu_box + ')'\
            + (' ' * MENU_ITEM_GAP) + colours_menu_item + text\
            + (' ' * (box_width - calc_line_item_width(index, text) - row_min_length))\
            + (' ' * MENU_ITEM_TAIL) + COLOUR_RESET + colours_menu_box + '│' + COLOUR_RESET

def generate_menu_line_option(char, text):

    return (' ' * box_left) + colours_menu_box + '│' + (' ' * MENU_ITEM_INDENT) + '('\
            + allowed_option_key(char) + COLOUR_RESET + colours_menu_box + ')'\
            + (' ' * MENU_ITEM_GAP) + text\
            + (' ' * (box_width - calc_line_item_width(char, text) - row_min_length))\
            + (' ' * MENU_ITEM_TAIL) + '│' + COLOUR_RESET

def calc_line_item_width(index, text):

    return len(str(index) + text)

def generate_menu_prompt():

    return (' ' * (box_left + PROMPT_INDENT)) + colours_prompt + 'select:' + COLOUR_RESET + ' '

def generate_search_prompt():

    return (' ' * (box_left + PROMPT_INDENT)) + colours_prompt + 'enter text to search for: '\
            + COLOUR_RESET + ' '

def allowed_item_key(text):

    return COLOUR_ORANGE_FG + COLOUR_BOLD + COLOUR_DARK_GREY_BG + text + COLOUR_RESET

def allowed_option_key(text):

    return COLOUR_YELLOW_FG + COLOUR_BOLD + COLOUR_DARK_GREY_BG + text + COLOUR_RESET

def get_screen_size():
    rows_str, columns_str = os.popen('stty size', 'r').read().split()

    return int(rows_str), int(columns_str)

def reset_display():
    print('\033c')

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
                        fields.idx          AS field_index,\
                        types.mode          AS data_type\
                FROM entries\
                        JOIN fields         ON fields.entry_id = entries.id\
                LEFT    JOIN types          ON types.id = fields.type_id '

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute(base_sql + 'WHERE entry_id = ? ORDER BY field_index', (entry_id,))

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

def generate_single_entry_screen(title, entry_fields):
    rows, columns = get_screen_size()
    title_min_length = len(title) + BOX_TITLE_CHARS_LENGTH + (TITLE_SPACING * 2) + BOX_TITLE_INDENT

    header = (' ' * BOX_INDENT) + colours_single_entry_box + '╔' + ('═' * BOX_TITLE_INDENT) + '╡'\
                + (' ' * TITLE_SPACING) + colours_single_entry_title + title + COLOUR_RESET\
                + colours_single_entry_box + (' ' * TITLE_SPACING) + '╞' + '═' * (columns\
                - BOX_INDENT - title_min_length - BOX_INDENT) + '╗' + COLOUR_RESET + '\n'
    content = ''

    footer = (' ' * BOX_INDENT) + colours_single_entry_box + '╚'\
                + ('═' * (columns - BOX_FOOTER_CHARS_LENGTH - BOX_INDENT - BOX_INDENT)) + '╝'\
                + COLOUR_RESET

    for field in entry_fields:
        if field['data_type'] == 'note' or field['entry_type'] == 1:
            content += generate_note_screen('Note', field['value'], columns)
            break
        else:
            content += generate_field_screen(field['field_name'], field['value'], columns)

    return header + content + footer

def generate_single_entry_file(entry_fields):
    content = ''

    for field in entry_fields:
        if field['data_type'] == 'note' or field['entry_type'] == 1:
            content += generate_field_file('Note', field['value'])
        else:
            content += generate_field_file(field['field_name'], field['value']) + '\n'

    return content

def generate_note_screen(name, value, columns):
    title = name + ':'
    name_min_length = len(title) + BOX_VERTICAL_CHARS_LENGTH + ENTRY_NAME_INDENT
    name_line = (' ' * BOX_INDENT) + colours_single_entry_box + '║' + (' ' * ENTRY_NAME_INDENT)\
                + colours_single_entry_name + title\
                + (' ' * (columns - BOX_INDENT - name_min_length - BOX_INDENT))\
                + colours_single_entry_box + '║' + COLOUR_RESET + '\n'
    value_line = ''

    for line in value.splitlines():
        line_min_length = len(line) + BOX_VERTICAL_CHARS_LENGTH + ENTRY_VALUE_INDENT

        value_line += (' ' * BOX_INDENT) + colours_single_entry_box + '║'\
                        + (' ' * ENTRY_VALUE_INDENT) + colours_single_entry_value + line\
                        + (' ' * (columns - BOX_INDENT - line_min_length - BOX_INDENT))\
                        + colours_single_entry_box + '║' + COLOUR_RESET + '\n'

    return name_line + value_line

def generate_field_screen(name, value, columns):
    title = name + ':'
    name_min_length = len(title) + BOX_VERTICAL_CHARS_LENGTH + ENTRY_NAME_INDENT
    value_min_length = len(value) + BOX_VERTICAL_CHARS_LENGTH + ENTRY_VALUE_INDENT

    name_line = (' ' * BOX_INDENT) + colours_single_entry_box + '║' + (' ' * ENTRY_NAME_INDENT)\
                + colours_single_entry_name + title + (' ' * (columns - BOX_INDENT\
                - name_min_length - BOX_INDENT)) + colours_single_entry_box + '║' + COLOUR_RESET\
                + '\n'

    value_line = (' ' * BOX_INDENT) + colours_single_entry_box + '║' + (' ' * ENTRY_VALUE_INDENT)\
                + colours_single_entry_value + value + (' ' * (columns - BOX_INDENT\
                - value_min_length - BOX_INDENT)) + colours_single_entry_box + '║' + COLOUR_RESET\
                + '\n'

    return name_line + value_line

def generate_field_file(name, value):
    name_line = name + ':\n'
    value_line = value + '\n'

    return name_line + value_line

def write_entry_to_file(entry_name, entry_fields):
    output_pathfile = entry_name.replace(' ', '_').replace('/', '_').replace('\\', '_').\
                        replace('?', '_')
    output_pathfile += '.txt'
    content = generate_single_entry_file(entry_fields)

    if not os.path.exists(output_pathfile):
        with open(output_pathfile, 'w') as text_file:
            text_file.write(content)

        print((' ' * (box_left + PROMPT_INDENT)) + "* {} *\n".\
                format(colours_write_ok + 'written to file' + COLOUR_RESET))
    else:
        print((' ' * (box_left + PROMPT_INDENT)) + "! {} !\n".\
                format(colours_write_fail + 'did not write (file already exists)' + COLOUR_RESET))

    return

def check_opts(argv):
    global database_pathfile

    database_pathfile = ''
    help_message = '\nUsage: ./' + SCRIPT_FILE + ' -i [inputfile]'

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
    print(SCRIPT_DETAILS)

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
            entry_menu_index = draw_menu(category_row['category_name'], category_entries,
                                        'entry_name', 'SBFM')

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
            search_menu_index = draw_menu('Search results for \"' + search_text + '\"',
                                            search_entries, 'entry_name', 'BM', None, True)

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
            favorite_menu_index = draw_menu('Favorites', favorites_entries, 'entry_name', 'BM',
                                            None, True)

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
