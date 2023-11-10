import os
import curses

def display_menu(stdscr, current_selection, files_and_dirs, show_menu):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    if show_menu:
        for idx, item in enumerate(files_and_dirs):
            x = 0
            y = idx
            if idx == current_selection:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, item)
    stdscr.refresh()

def main(stdscr):
    # Use terminal default colors
    curses.use_default_colors()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, -1)  # Set the selection color to black with default background

    # Stack to keep track of directories user has navigated through
    directory_stack = []

    # Start at the current directory
    current_directory = os.getcwd()
    files_and_dirs = os.listdir(current_directory)
    current_selection = 0

    show_menu = False  # Menu is hidden initially
    display_menu(stdscr, current_selection, files_and_dirs, show_menu)

    while True:
        key = stdscr.getch()
        height, width = stdscr.getmaxyx()  # Get the current size of the window

        if show_menu:
            if key == curses.KEY_UP and current_selection > 0:
                current_selection -= 1
            elif key == curses.KEY_DOWN and current_selection < len(files_and_dirs) - 1:
                current_selection += 1
            elif key == curses.KEY_RIGHT:
                # Attempt to enter a directory
                potential_dir = os.path.join(current_directory, files_and_dirs[current_selection])
                if os.path.isdir(potential_dir):
                    directory_stack.append(current_directory)
                    current_directory = potential_dir
                    files_and_dirs = os.listdir(current_directory)
                    current_selection = 0
            elif key == curses.KEY_LEFT:
                # Go back to previous directory
                if directory_stack:
                    current_directory = directory_stack.pop()
                    files_and_dirs = os.listdir(current_directory)
                    current_selection = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                # Output the selected file name and exit
                selected_item = os.path.join(current_directory, files_and_dirs[current_selection])
                if os.path.isfile(selected_item):
                    stdscr.clear()
                    stdscr.addstr(0, 0, f"Selected file: {files_and_dirs[current_selection]}")
                    stdscr.refresh()
                    stdscr.getch()
                    # Exiting the program
                    break

        if key == 9:  # Tab key
            show_menu = not show_menu  # Toggle menu display

        display_menu(stdscr, current_selection, files_and_dirs, show_menu)

    # Returning the selected file name
    return files_and_dirs[current_selection]

# Running the program
selected_file = curses.wrapper(main)
print(f"Selected file: {selected_file}")
