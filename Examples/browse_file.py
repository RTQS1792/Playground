import os
import curses

def display_menu(stdscr, current_selection, files_and_dirs, show_menu):
    stdscr.clear()
    if show_menu:
        for idx, item in enumerate(files_and_dirs):
            x = 0
            y = idx
            if idx == current_selection:
                stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, item)
            if idx == current_selection:
                stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()

def handle_user_input(stdscr, key, current_selection, files_and_dirs, current_directory, directory_stack):
    if key == curses.KEY_UP and current_selection > 0:
        current_selection -= 1
    elif key == curses.KEY_DOWN and current_selection < len(files_and_dirs) - 1:
        current_selection += 1
    elif key == curses.KEY_RIGHT:
        potential_dir = os.path.join(current_directory, files_and_dirs[current_selection])
        if os.path.isdir(potential_dir):
            directory_stack.append(current_directory)
            current_directory = potential_dir
            files_and_dirs = os.listdir(current_directory)
            current_selection = 0
    elif key == curses.KEY_LEFT:
        if directory_stack:
            current_directory = directory_stack.pop()
            files_and_dirs = os.listdir(current_directory)
            current_selection = 0
    return current_selection, files_and_dirs, current_directory

def main(stdscr):
    curses.use_default_colors()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, -1)

    directory_stack = []
    current_directory = os.getcwd()
    files_and_dirs = os.listdir(current_directory)
    current_selection = 0
    show_menu = False  
    display_menu(stdscr, current_selection, files_and_dirs, show_menu)

    while True:
        key = stdscr.getch()
        if show_menu:
            current_selection, files_and_dirs, current_directory = handle_user_input(stdscr, key, current_selection, files_and_dirs, current_directory, directory_stack)
            if key == curses.KEY_ENTER or key in [10, 13]:
                selected_item = os.path.join(current_directory, files_and_dirs[current_selection])
                if os.path.isfile(selected_item):
                    stdscr.clear()
                    stdscr.addstr(0, 0, f"Selected file: {files_and_dirs[current_selection]}")
                    stdscr.refresh()
                    stdscr.getch()
                    break
        if key == 9:
            show_menu = not show_menu
        display_menu(stdscr, current_selection, files_and_dirs, show_menu)

    return files_and_dirs[current_selection]

selected_file = curses.wrapper(main)
print(f"Selected file: {selected_file}")
