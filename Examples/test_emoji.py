import curses

def main(stdscr):
    # Initialize curses
    curses.start_color()
    curses.use_default_colors()

    # Print text with the checkmark emoji
    stdscr.addstr(0, 0, "Task completed ✅")
    stdscr.addstr(1, 0, "Unicode version: \u2705")

    # Refresh the screen to show the text
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)
