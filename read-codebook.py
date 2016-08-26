#!/usr/bin/python3
# -*- coding: utf-8 -*-
# line wraps @ 120 chars

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
import colour_scheme as scheme

SCRIPT_FILE = os.path.basename(sys.argv[0])
SCRIPT_DATE = '2016-08-26'

#BOX_POSITION = 'left'           # left of screen
BOX_POSITION = 'center'         # center of screen
#BOX_POSITION = 'right'          # right of screen
BOX_INDENT = 1                  # space from side of screen to box
BOX_TITLE_INDENT = 4            # chars from left border to start of title bookend
                                #   this is ignored if BOX_POSITION is 'center'
TITLE_SPACING = 1               # space between bookends and title on left and right
MENU_ITEM_INDENT = 1            # space between the left border and the index parentheses
MENU_ITEM_GAP = 1               # space between index parentheses and the displayed item
MENU_ITEM_TAIL = 1              # space between item and right border
MENU_ITEM_FAVORITE = ' ✶'       # show this when menu item is a favorite
PROMPT_INDENT = 1               # from left of box to start of prompt
ENTRY_NAME_INDENT = 1           # from left of box to name
ENTRY_VALUE_INDENT = 4          # from left of box to value
ENTRY_NAME_FAVORITE = ' ✶'      # show this when displaying favorite item fields

# these are only used for calculation
BOX_TITLE_CHARS_LENGTH = 4      # left corner, title bookends, right corner
BOX_VERTICAL_CHARS_LENGTH = 2   # upright lines
BOX_FOOTER_CHARS_LENGTH = 2     # left corner, right corner

MENU_ROW_MIN_LENGTH = MENU_ITEM_INDENT + 2 + MENU_ITEM_GAP + (len(MENU_ITEM_FAVORITE))\
                    + MENU_ITEM_TAIL + BOX_VERTICAL_CHARS_LENGTH

SCRIPT_DETAILS = '{} ({})'.format(scheme.COLOUR_LIGHT_FG + scheme.COLOUR_BOLD + SCRIPT_FILE + scheme.COLOUR_RESET,
                SCRIPT_DATE)

DATABASE = None


def draw_menu(title, table, column, options, prompt_only = False, special = False):
    # if prompt_only is True    : don't show menu box and items, only show prompt line
    # if special is True        : menu title colour will be scheme.COLOURS_MENU_TITLE_SPECIAL
    # if special is False       : menu title colour will be scheme.COLOURS_MENU_TITLE_REGULAR

    global box_width, box_left

    total_items = len(table)

    if prompt_only: display_menu = False
    else:
        display_menu = True
        box_width = 31      # minimum box width
        line_length = longest_column_entry(table, column)
        title_length = calc_title_length(title)
        if (line_length + MENU_ROW_MIN_LENGTH) > box_width:
            box_width = line_length + MENU_ROW_MIN_LENGTH
        if title_length > box_width: box_width = title_length
        box_left = calc_box_left()
        header, separator, footer = generate_menu_lines(title, special)

    while True:
        if display_menu:
            print(header)

            for index, row in enumerate(table):
                try:
                    show_favorite = row['favorite']
                except:
                    show_favorite = ''

                print(generate_menu_line_item(index + 1, row[column], show_favorite))

            if total_items > 0: print(separator)
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
            if int(user_selection) > 0 and int(user_selection) <= total_items: break
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

    return int(user_selection)


def generate_menu_lines(title, special = False):
    title_length = calc_title_length(title)

    if special: title_colour = scheme.COLOURS_MENU_TITLE_SPECIAL
    else: title_colour = scheme.COLOURS_MENU_TITLE_REGULAR

    if title:
        menu_header = (' ' * (box_left + ((box_width // 2) - ((len(SCRIPT_FILE) + len(SCRIPT_DATE) + 3) // 2))))\
                    + SCRIPT_DETAILS + '\n\n'

        if BOX_POSITION == 'left':
            left_padding = '─' * BOX_TITLE_INDENT
            right_padding = '─' * (box_width - title_length)
        elif BOX_POSITION == 'center':
            left_padding = '─' * ((box_width - title_length) // 2)
            right_padding = '─' * (box_width - title_length - len(left_padding))
        else:
            left_padding = '─' * (box_width - title_length)
            right_padding = '─' * BOX_TITLE_INDENT

        header_template = (' ' * box_left) + '{}◤' + left_padding + '┤' + (' ' * TITLE_SPACING) + '{}' + title\
                        + (' ' * TITLE_SPACING) + '{}├' + right_padding + '┐{}'
        menu_header += header_template.format(scheme.COLOURS_MENU_BOX, title_colour, scheme.COLOUR_RESET
                    + scheme.COLOURS_MENU_BOX, scheme.COLOUR_RESET)
        separator_template = (' ' * box_left) + '{}├' + ('─' * (box_width - BOX_VERTICAL_CHARS_LENGTH)) + '┤{}'
        menu_separator = separator_template.format(scheme.COLOURS_MENU_BOX, scheme.COLOUR_RESET)
    else:
        header_template = (' ' * box_left) + '{}◤' + ('─' * (box_width - BOX_VERTICAL_CHARS_LENGTH)) + '┐{}'
        menu_header = header_template.format(scheme.COLOURS_MENU_BOX, scheme.COLOUR_RESET)
        menu_separator = ''

    footer_template = (' ' * box_left) + '{}└' + ('─' * (box_width - BOX_VERTICAL_CHARS_LENGTH)) + '◢{}'
    menu_footer = footer_template.format(scheme.COLOURS_MENU_BOX, scheme.COLOUR_RESET)

    return menu_header, menu_separator, menu_footer


def generate_menu_line_item(index, text, show_favorite = False):
    if show_favorite: line_favorite = scheme.COLOURS_FAVORITE_STAR + MENU_ITEM_FAVORITE
    else: line_favorite = (' ' * len(MENU_ITEM_FAVORITE))

    template = (' ' * box_left) + '{}│' + (' ' * MENU_ITEM_INDENT) + '({}' + str(index) + '{})' + (' ' * MENU_ITEM_GAP)\
                + '{}' + text + (' ' * (box_width - calc_line_item_width(index, text) - MENU_ROW_MIN_LENGTH))\
                + line_favorite + (' ' * MENU_ITEM_TAIL) + scheme.COLOUR_RESET + scheme.COLOURS_MENU_BOX + '{}│{}'

    return template.format(scheme.COLOURS_MENU_BOX, scheme.COLOURS_ALLOWED_ITEM_KEY, scheme.COLOUR_RESET
                            + scheme.COLOURS_MENU_BOX, scheme.COLOURS_MENU_ITEM, scheme.COLOUR_RESET
                            + scheme.COLOURS_MENU_BOX, scheme.COLOUR_RESET)


def generate_menu_line_option(char, text):
    template = (' ' * box_left) + '{}│' + (' ' * MENU_ITEM_INDENT) + '({}' + char + '{})' + (' ' * MENU_ITEM_GAP)\
                + text + (' ' * (box_width - calc_line_item_width(char, text) - MENU_ROW_MIN_LENGTH))\
                + (' ' * len(MENU_ITEM_FAVORITE)) + (' ' * MENU_ITEM_TAIL) + '│{}'

    return template.format(scheme.COLOURS_MENU_BOX, scheme.COLOURS_ALLOWED_OPTION_KEY, scheme.COLOUR_RESET
                            + scheme.COLOURS_MENU_BOX, scheme.COLOUR_RESET)


def generate_menu_prompt():
    template = (' ' * (box_left + PROMPT_INDENT)) + '{}select:{} '

    return template.format(scheme.COLOURS_PROMPT, scheme.COLOUR_RESET)


def generate_search_prompt():
    template = (' ' * (box_left + PROMPT_INDENT)) + '{}enter text to search for:{} '

    return template.format(scheme.COLOURS_PROMPT, scheme.COLOUR_RESET)


def longest_column_entry(entries, name):
    # checks the length of every item in column 'name' and returns the longest

    current_length = 1

    for index, entry in enumerate(entries):
        field_length = calc_line_item_width(index, entry[name])
        if field_length > current_length: current_length = field_length

    return current_length


def calc_line_item_width(index, text):
    return len(str(index) + text)


def calc_title_length(title):
    length = len(title) + BOX_TITLE_CHARS_LENGTH + (TITLE_SPACING * 2)
    if BOX_POSITION != 'center': length += BOX_TITLE_INDENT

    return length


def calc_box_left():
    if BOX_POSITION == 'left':
        return BOX_INDENT
    elif BOX_POSITION == 'right':
        rows, columns = get_screen_size()
        return columns - BOX_INDENT - box_width
    else:
        rows, columns = get_screen_size()
        return (columns // 2) - (box_width // 2)


def get_db_categories():
    con = lite.connect(DATABASE)
    base_sql = 'SELECT  id          AS category_id,\
                        name        AS category_name\
                FROM categories '

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute(base_sql + 'ORDER BY category_name')

    return cur.fetchall()


def get_db_entries_from_category(category_id):
    con = lite.connect(DATABASE)
    base_sql = 'SELECT  categories.id       AS category_id,\
                        categories.name     AS category_name,\
                        entries.id          AS entry_id,\
                        entries.name        AS entry_name,\
                        entries.type        AS entry_type,\
                        entries.is_favorite AS favorite\
                FROM categories\
                        JOIN entries        ON entries.category_id = categories.id '

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute(base_sql + 'WHERE category_id = ? ORDER BY entry_name COLLATE NOCASE', (category_id,))

    return cur.fetchall()


def get_db_fields_from_entry(entry_id):
    con = lite.connect(DATABASE)
    base_sql = 'SELECT  entry_id,\
                        entries.name        AS entry_name,\
                        entries.type        AS entry_type,\
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
    con = lite.connect(DATABASE)
    base_sql = 'SELECT  entries.id          AS entry_id,\
                        entries.name        AS entry_name,\
                        entries.type        AS entry_type,\
                        entries.is_favorite AS favorite,\
                        fields.value\
                FROM entries\
                        JOIN fields         ON fields.entry_id = entries.id\
                LEFT    JOIN types          ON types.id = fields.type_id '

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute(base_sql + 'WHERE value LIKE ? OR entry_name LIKE ? COLLATE NOCASE GROUP BY entry_name\
                    ORDER BY entry_name', ('%' + text + '%', '%' + text + '%'))

    return cur.fetchall()


def get_db_favorites():
    con = lite.connect(DATABASE)
    base_sql = 'SELECT  entries.id          AS entry_id,\
                        entries.name        AS entry_name,\
                        entries.type        AS entry_type,\
                        entries.is_favorite AS favorite\
                FROM entries '

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute(base_sql + 'WHERE favorite = 1 ORDER BY entry_name COLLATE NOCASE')

    return cur.fetchall()


def generate_single_entry_screen(title, fields, favorite = False):
    rows, columns = get_screen_size()

    if favorite:
        title_length = calc_title_length(title + ENTRY_NAME_FAVORITE)
        title += scheme.COLOURS_FAVORITE_STAR + ENTRY_NAME_FAVORITE
    else:
        title_length = calc_title_length(title)

    if BOX_POSITION == 'left':
        left_padding = '═' * BOX_TITLE_INDENT
        right_padding = '═' * (columns - (BOX_INDENT * 2) - title_length)
    elif BOX_POSITION == 'center':
        left_padding = '═' * ((columns - title_length) // 2)
        right_padding = ('═' * (columns - (BOX_INDENT * 2) - title_length - len(left_padding)))
    else:
        left_padding = '═' * (columns - (BOX_INDENT * 2) - title_length)
        right_padding = '═' * BOX_TITLE_INDENT

    template_header = (' ' * BOX_INDENT) + '{}◤' + left_padding + '╡' + (' ' * TITLE_SPACING) + '{}' + title + '{}'\
                    + (' ' * TITLE_SPACING) + '╞' + right_padding + '╗{}\n'
    header = template_header.format(scheme.COLOURS_SINGLE_ENTRY_BOX, scheme.COLOURS_SINGLE_ENTRY_TITLE,
                scheme.COLOUR_RESET + scheme.COLOURS_SINGLE_ENTRY_BOX, scheme.COLOUR_RESET)
    content = ''

    for field in fields:
        if field['data_type'] == 'note' or field['entry_type'] == 1:
            content += generate_note_screen('Note', field['value'], columns)
            break
        else:
            content += generate_field_screen(field['field_name'], field['value'], columns)

    template_footer = (' ' * BOX_INDENT) + '{}╚' + ('═' * (columns - BOX_FOOTER_CHARS_LENGTH - (BOX_INDENT * 2)))\
                    + '◢{}'
    footer = template_footer.format(scheme.COLOURS_SINGLE_ENTRY_BOX, scheme.COLOUR_RESET)

    return header + content + footer


def generate_single_entry_file(fields):
    content = ''

    for field in fields:
        if field['data_type'] == 'note' or field['entry_type'] == 1:
            content += generate_field_file('Note', field['value'])
        else:
            content += generate_field_file(field['field_name'], field['value']) + '\n'

    return content


def generate_note_screen(name, value, columns):
    name += ':'
    name_min_length = len(name) + BOX_VERTICAL_CHARS_LENGTH + ENTRY_NAME_INDENT
    template_name_line = (' ' * BOX_INDENT) + '{}║' + (' ' * ENTRY_NAME_INDENT) + '{}' + name\
                        + (' ' * (columns - BOX_INDENT - name_min_length - BOX_INDENT)) + '{}║{}\n'
    name_line = template_name_line.format(scheme.COLOURS_SINGLE_ENTRY_BOX, scheme.COLOURS_SINGLE_ENTRY_NAME,
                scheme.COLOURS_SINGLE_ENTRY_BOX, scheme.COLOUR_RESET)
    value_line = ''

    for line in value.splitlines():
        line_min_length = len(line) + BOX_VERTICAL_CHARS_LENGTH + ENTRY_VALUE_INDENT
        template_value_line = (' ' * BOX_INDENT) + '{}║' + (' ' * ENTRY_VALUE_INDENT) + '{}' + line\
                            + (' ' * (columns - BOX_INDENT - line_min_length - BOX_INDENT)) + '{}║{}\n'
        value_line += template_value_line.format(scheme.COLOURS_SINGLE_ENTRY_BOX, scheme.COLOURS_SINGLE_ENTRY_VALUE,
                        scheme.COLOURS_SINGLE_ENTRY_BOX, scheme.COLOUR_RESET)

    return name_line + value_line


def generate_field_screen(name, value, columns):
    name += ':'
    name_min_length = len(name) + BOX_VERTICAL_CHARS_LENGTH + ENTRY_NAME_INDENT
    value_min_length = len(value) + BOX_VERTICAL_CHARS_LENGTH + ENTRY_VALUE_INDENT
    template_name_line = (' ' * BOX_INDENT) + '{}║' + (' ' * ENTRY_NAME_INDENT) + '{}' + name\
                        + (' ' * (columns - BOX_INDENT - name_min_length - BOX_INDENT)) + '{}║{}\n'
    name_line = template_name_line.format(scheme.COLOURS_SINGLE_ENTRY_BOX, scheme.COLOURS_SINGLE_ENTRY_NAME,
                scheme.COLOURS_SINGLE_ENTRY_BOX, scheme.COLOUR_RESET)
    template_value_line = (' ' * BOX_INDENT) + '{}║' + (' ' * ENTRY_VALUE_INDENT) + '{}' + value\
                        + (' ' * (columns - BOX_INDENT - value_min_length - BOX_INDENT)) + '{}║{}\n'
    value_line = template_value_line.format(scheme.COLOURS_SINGLE_ENTRY_BOX, scheme.COLOURS_SINGLE_ENTRY_VALUE,
                    scheme.COLOURS_SINGLE_ENTRY_BOX, scheme.COLOUR_RESET)

    return name_line + value_line


def generate_field_file(name, value):
    return name + ':\n' + value + '\n'


def write_fields_to_file(filename, fields):
    target_pathfile = filename.replace(' ', '_').replace('/', '_').replace('\\', '_').replace('?', '_') + '.txt'
    content = generate_single_entry_file(fields)

    if not os.path.exists(target_pathfile):
        with open(target_pathfile, 'w') as text_file:
            text_file.write(content)

        print((' ' * (box_left + PROMPT_INDENT)) + "* {} *\n".format(scheme.COLOURS_WRITE_OK
                + 'written to file' + scheme.COLOUR_RESET))
    else:
        print((' ' * (box_left + PROMPT_INDENT)) + "! {} !\n".format(scheme.COLOURS_WRITE_FAIL
                + 'did not write (file already exists)' + scheme.COLOUR_RESET))

    return


def get_screen_size():
    rows_str, columns_str = os.popen('stty size', 'r').read().split()

    return int(rows_str), int(columns_str)


def reset_display():
    print('\033c')

    return


def show_help():
    print('\nUsage: ./{} -i [inputfile]'.format(SCRIPT_FILE))
    sys.exit()


def what_are_my_options(argv):
    input_pathfile = None

    try:
        opts, args = getopt.getopt(argv,'hvi:',['help','version','input-file='])
    except getopt.GetoptError:
        show_help()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            show_help()
        elif opt in ('-v', '--version'):
            sys.exit()
        elif opt in ('-i', '--input-file'):
            if not arg:
                show_help()
            input_pathfile = arg

    if not input_pathfile: show_help()

    return input_pathfile


def main():
    menu_stack = []
    current_menu = 'categories'
    all_categories = get_db_categories()

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
                category_row = all_categories[category_menu_index - 1]
                current_menu = 'entries'

        if current_menu == 'entries':
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
                menu_stack.append(current_menu)
                entry_row = category_entries[entry_menu_index - 1]
                current_menu = 'fields'

        if current_menu == 'search':
            try:
                search_text = input(generate_search_prompt())
            except KeyboardInterrupt:
                current_menu = menu_stack.pop()
            else:
                if search_text: current_menu = 'search results'
                else: print()

        if current_menu == 'search results':
            search_entries = get_db_search(search_text)
            reset_display()
            search_menu_index = draw_menu('Search results for \"' + search_text + '\"', search_entries, 'entry_name',
                                'BMF', None, True)

            if search_menu_index == 0:
                current_menu = menu_stack.pop()
            elif search_menu_index == -3:
                menu_stack.append(current_menu)
                current_menu = 'favorites'
            elif search_menu_index == -4:
                menu_stack = []
                current_menu = 'categories'
            else:
                menu_stack.append(current_menu)
                entry_row = search_entries[search_menu_index - 1]
                current_menu = 'fields'

        if current_menu == 'favorites':
            favorites_entries = get_db_favorites()
            reset_display()
            favorite_menu_index = draw_menu('Favorites', favorites_entries, 'entry_name', 'BMS', None, True)

            if favorite_menu_index == 0:
                current_menu = menu_stack.pop()
            elif favorite_menu_index == -2:
                menu_stack.append(current_menu)
                current_menu = 'search'
            elif favorite_menu_index == -4:
                menu_stack = []
                current_menu = 'categories'
            else:
                menu_stack.append(current_menu)
                entry_row = favorites_entries[favorite_menu_index - 1]
                current_menu = 'fields'

        if current_menu == 'fields':
            entry_name = entry_row['entry_name']
            entry_fields = get_db_fields_from_entry(entry_row['entry_id'])
            content = generate_single_entry_screen(entry_name, entry_fields, entry_row['favorite'])

            reset_display()
            print(content + '\n')

            prompt_only = False

            while True:
                fields_menu_index = draw_menu('', '', '', 'BWM', prompt_only)

                if fields_menu_index == 0:
                    current_menu = menu_stack.pop()
                    break
                elif fields_menu_index == -1:
                    write_fields_to_file(entry_name, entry_fields)
                    prompt_only = True
                elif fields_menu_index == -4:
                    menu_stack = []
                    current_menu = 'categories'
                    break


if __name__ == '__main__':
    print(SCRIPT_DETAILS)
    DATABASE = what_are_my_options(sys.argv[1:])
    if not os.path.exists(DATABASE):
        print('\n! Input file not found! [{}]'.format(DATABASE))
    else:
        main()
