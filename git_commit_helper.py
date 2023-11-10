"""
Author       : Hanqing Qi
Date         : 2023-11-10 15:15:52
LastEditors  : Hanqing Qi
LastEditTime : 2023-11-10 17:14:21
FilePath     : /Playground/git_commit_helper.py
Description  : 
"""
# -*- coding: utf-8 -*-

import subprocess
import curses
import re
import os
import locale

IGNORED_WORDS = {
    "and",
    "or",
    "but",
    "the",
    "a",
    "in",
    "with",
    "to",
    "of",
    "on",
    "at",
    "from",
    "by",
    "as",
    "for",
    "into",
    "through",
    "during",
    "including",
    "until",
    "against",
    "among",
    "throughout",
    "despite",
    "towards",
    "upon",
    "concerning",
    "about",
    "like",
    "over",
    "before",
    "between",
    "after",
    "since",
    "without",
    "under",
    "within",
    "along",
    "following",
    "across",
    "behind",
    "beyond",
    "plus",
    "except",
}

EMOJIS = [
    "📝 Add Documentation",
    "📥 Add",
    "🔨 Fix",
    "💨 Hotfix",
    "🔎 Need Testing",
    "🍻 Pass",
    "📖 Readme",
    "🔥 Remove",
    "🎉 Start",
    "💾 Save",
    "🔧 Update",
    "🏗️",
]


# Check if the current directory is a git repository
def is_git_repository():
    try:
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"])
        return True
    except subprocess.CalledProcessError:
        return False


# Process the code string to match "`" pairs and apply capitalization
def process_code_string(title: str, ignored_words: set = None, capitalize_mode: str = "first") -> str:
    if ignored_words is None:
        ignored_words = IGNORED_WORDS

    words = title.split()
    processed_words = []
    processing_words = []

    tick_open = False
    ext_regex = re.compile(r"\.[a-zA-Z0-9]+$")  # Regular expression to match file extensions

    for idx, word in enumerate(words):
        # Check for a starting backtick `
        if word.startswith("`"):
            if tick_open:
                param = processing_words.pop(0)
                processed_words.append(param + "`")
                for pword in processing_words:
                    processed_words.append(pword if pword.lower() in ignored_words else pword.capitalize())
                processing_words.clear()
                tick_open = False
            if word.endswith("`"):
                processed_words.append(word)
                continue
            elif re.search(ext_regex, word):
                processed_words.append(word + "`")
                continue
            else:
                tick_open = True
                processing_words.append(word)
                continue

        # Check for an ending backtick `
        elif word.endswith("`"):
            tick_open = False
            processing_words.append(word)
            for pword in processing_words:
                processed_words.append(pword)
            processing_words.clear()
            continue

        if tick_open:
            if re.search(ext_regex, word):
                tick_open = False
                processing_words.append(word + "`")
                for pword in processing_words:
                    processed_words.append(pword)
                processing_words.clear()
                continue
            else:
                processing_words.append(word)
                continue
        else:
            # Apply capitalization based on the mode
            if capitalize_mode == "first" and idx == 0:
                processed_words.append(word.capitalize())
            elif capitalize_mode == "all":
                processed_words.append(word if word.lower() in ignored_words else word.capitalize())
            else:
                processed_words.append(word.lower())
            continue

    # If at the end of the title but tick is still open
    if tick_open:
        param = processing_words.pop(0)
        processed_words.append(param + "`")
        for pword in processing_words:
            processed_words.append(pword if pword.lower() in ignored_words else pword.capitalize())
        processing_words.clear()

    # If the capitalization mode is 'first', then add a period at the end if needed
    if capitalize_mode == "first" and not processed_words[-1].endswith("."):
        processed_words[-1] += "."

    return " ".join(processed_words)


# Get directories and files in the current path
def get_directories_and_files(path):
    try:
        # List directories first, then files
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))] + [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    except PermissionError:
        return []


# Recursive function to show the file selection menu
def show_menu(stdscr, y, x, base_path, current_path, depth=0):
    # Get directories and files for the current path
    entries = get_directories_and_files(current_path)
    current_selection = 0

    color_pair_normal = curses.color_pair(6)
    color_pair_selected = curses.color_pair(4) | curses.A_BOLD  # Bold text for selected item

    while True:
        # Display menu items at the current depth
        for idx, entry in enumerate(entries):
            if idx == current_selection:
                stdscr.attron(color_pair_selected)
            else:
                stdscr.attron(color_pair_normal)
            # Display entry with indentation based on depth
            stdscr.addstr(y + idx, x + (depth * 25), entry)
            stdscr.attroff(color_pair_selected)
            stdscr.attroff(color_pair_normal)
        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and current_selection > 0:
            current_selection -= 1
        elif key == curses.KEY_DOWN and current_selection < len(entries) - 1:
            current_selection += 1
        elif key == curses.KEY_RIGHT:
            # Dive into the directory
            new_path = os.path.join(current_path, entries[current_selection])
            if os.path.isdir(new_path):
                selected = show_menu(stdscr, y, x, base_path, new_path, depth + 1)
                if selected:
                    for i in range(len(entries)):
                        stdscr.move(y + i, 0)
                        stdscr.clrtoeol()
                    stdscr.refresh()
                    return selected
        elif key == curses.KEY_LEFT and depth > 0:
            # Clear the menu from the screen
            for i in range(len(entries)):
                stdscr.move(y + i, x)
                stdscr.clrtoeol()
            # Go back up
            return None
        elif key in [10, 13]:  # Enter key
            # Select the file or directory
            # Return the relative path from the base path
            # Clear the menu from the screen
            for i in range(len(entries)):
                stdscr.move(y + i, 0)
                stdscr.clrtoeol()
            stdscr.refresh()
            return os.path.relpath(os.path.join(current_path, entries[current_selection]), base_path)
        elif key == 27:  # Escape key
            for i in range(len(entries)):
                stdscr.move(y + i, 0)
                stdscr.clrtoeol()
            # Exit menu
            if depth == 0:
                return None
            else:
                return


# Insert the selected path into the input string
def insert_selected_path(input_str, selected_path, cursor_x, prompt_length):
    return (input_str[: cursor_x - prompt_length] + "`" + selected_path + "`" + " " + input_str[cursor_x - prompt_length :]), cursor_x + len(selected_path) + 3


# Menu to prompt the user to select an commit type with emojis
def custom_menu(stdscr, menu_title, menu_items, y=1):
    curses.curs_set(0)  # Hide cursor
    current_selection = 0
    color_pair_selected = curses.color_pair(4) | curses.A_BOLD
    color_pair_normal = curses.color_pair(6)

    while True:
        # stdscr.clear()
        # Display menu title on the y line
        stdscr.attron(curses.color_pair(5))
        stdscr.addstr(y, 0, menu_title)
        stdscr.attroff(curses.color_pair(5))

        for idx, entry in enumerate(menu_items):
            if idx == current_selection:
                stdscr.attron(color_pair_selected)
            else:
                stdscr.attron(color_pair_normal)
            # Display each menu item below the title
            stdscr.addstr(y + idx + 1, 0, entry)  # +1 to account for the title line
            stdscr.attroff(color_pair_selected)
            stdscr.attroff(color_pair_normal)

        key = stdscr.getch()
        if key == curses.KEY_UP and current_selection > 0:
            current_selection -= 1
        elif key == curses.KEY_DOWN and current_selection < len(menu_items) - 1:
            current_selection += 1
        elif key in [curses.KEY_ENTER, ord("\n")]:
            # Clear the menu display area
            for i in range(len(menu_items) + 1):  # +1 to include the title line
                stdscr.move(y + i, 0)
                stdscr.clrtoeol()
            stdscr.refresh()
            break  # User made a selection

        stdscr.refresh()

    return menu_items[current_selection]


# Get input from the user
def get_input(stdscr, y, prompt, color_pair, emoji=False):
    stdscr.move(y, 0)  # Move to the new line for each prompt
    max_y, max_x = stdscr.getmaxyx()  # Get window dimensions
    stdscr.clrtoeol()  # Clear the line
    stdscr.attron(color_pair)
    stdscr.addstr(prompt)
    stdscr.attroff(color_pair)
    stdscr.refresh()

    input_str = ""
    if emoji:
        commit_type = custom_menu(stdscr, "Select Commit Type: ", EMOJIS)
        input_str = commit_type + " " + input_str
        cursor_x = len(input_str) + len(prompt)
        stdscr.addstr(y, len(prompt), input_str)
    else:
        cursor_x = len(prompt)
    # Show the cursor
    curses.curs_set(1)
    while True:
        key = stdscr.getch()
        if key in [curses.KEY_BACKSPACE, 127, 8]:  # Handle backspace for different terminals
            # Delete a character at the cursor position and move cursor left
            input_str = input_str[: cursor_x - len(prompt) - 1] + input_str[cursor_x - len(prompt):]
            cursor_x -= 1
        elif key == curses.KEY_LEFT:
            cursor_x = max(len(prompt), cursor_x - 1)
        elif key == curses.KEY_RIGHT:
            cursor_x = min(len(prompt) + len(input_str), cursor_x + 1)
        elif 32 <= key <= 126:
            char = chr(key)
            input_str = input_str[: cursor_x - len(prompt)] + char + input_str[cursor_x - len(prompt):]
            cursor_x += 1
        elif key == curses.KEY_DOWN:
            # Open the menu at the current directory
            base_path = os.getcwd()  # Store the base path
            selected_option = show_menu(stdscr, y + 1, 0, base_path, base_path)
            if selected_option:
                input_str, cursor_x = insert_selected_path(input_str, selected_option, cursor_x, len(prompt))
        elif key == 10:  # Enter key
            break

        stdscr.move(y, 0)  # Move to the start of the prompt
        stdscr.clrtoeol()  # Clear the line from the current position
        stdscr.attron(color_pair)
        stdscr.addstr(prompt)
        stdscr.attroff(color_pair)
        stdscr.addstr(input_str)
        stdscr.move(y, cursor_x + 1 if emoji else cursor_x)  # Move the cursor to the correct position with emoji offset
        stdscr.refresh()

    return input_str.strip()


# Run a git command and display the output
def run_git_command(stdscr, command):
    try:
        # Run the Git command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Display the success message along with any output from the command
        stdscr.attron(curses.color_pair(2))  # Assuming color_pair(2) is for success messages
        if result.stdout:
            stdscr.addstr(result.stdout)
        if result.stderr:
            stdscr.addstr(result.stderr)
        stdscr.attroff(curses.color_pair(2))
        stdscr.refresh()
        # stdscr.getch()
        return True

    except subprocess.CalledProcessError as e:
        # Handle errors specifically from the subprocess
        stdscr.attron(curses.color_pair(3))  # Assuming color_pair(3) is for error messages
        stdscr.addstr("\nGit command failed: ")
        stdscr.addstr("Error - " + str(e.stderr))
        stdscr.attroff(curses.color_pair(3))
        stdscr.refresh()
        # stdscr.getch()
        return False
    except Exception as e:
        # Handle other exceptions
        stdscr.attron(curses.color_pair(3))  # Assuming color_pair(3) is for error messages
        stdscr.addstr("\nUnexpected error occurred:")
        stdscr.addstr(str(e))
        stdscr.attroff(curses.color_pair(3))
        stdscr.refresh()
        # stdscr.getch()
        return False


# The main function
def main(stdscr, prompts, confirmations):
    # check if the current directory is a git repository
    if not is_git_repository():
        raise Exception("Not a git repository")
    # Initialize colors
    curses.use_default_colors()
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, 3, 8)  # Yellow
        curses.init_pair(2, 2, 8)  # Green
        curses.init_pair(3, 1, 8)  # Red
        curses.init_pair(4, 9, 8)  # Orange
        curses.init_pair(5, 4, 8)  # Purple
        curses.init_pair(6, -1, 8)  # White
        color_pair = curses.color_pair(1)
    else:
        raise Exception("Terminal does not support color")

    # Get inputs for all prompts
    responses = []
    y = 0  # Start at the top of the screen
    for prompt in prompts:
        response = get_input(stdscr, y, prompt, color_pair, True if y == 0 else False)
        if response == "":
            response = "-"
        responses.append(response)
        y += 1  # Move to the next line for the next prompt

    # Optionally, display all the entered texts after the inputs
    # stdscr.clear()
    responses[0] = process_code_string(responses[0], capitalize_mode="all")
    responses[1] = process_code_string(responses[1])
    for i, response in enumerate(responses):
        # Apply green color to the prompt
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(i + y, 0, confirmations[i])
        stdscr.attroff(curses.color_pair(2))

        # Print the response in the default color
        stdscr.addstr(response + "\n")
    # Check if user wants to commit the changes
    stdscr.attron(curses.color_pair(5))
    stdscr.addstr("Commit these changes? (y/n): ")
    stdscr.attroff(curses.color_pair(5))
    stdscr.refresh()

    terminated = False
    while True:
        commit_key = stdscr.getch()
        if commit_key in [ord("y"), ord("Y")]:
            # Add all files to the staging area
            add_command = ["git", "add", "."]
            result = run_git_command(stdscr, add_command)
            # result = True
            if not result:
                return
            # Run the git commit command
            commit_command = ["git", "commit", "-m", responses[0], "-m", responses[1]]
            result = run_git_command(stdscr, commit_command)
            # result = True
            if not result:
                return
            stdscr.attron(curses.color_pair(2))
            stdscr.addstr("\nChanges committed successfully.")
            stdscr.attroff(curses.color_pair(2))
            stdscr.refresh()

            # Now ask for push
            stdscr.attron(curses.color_pair(5))
            stdscr.addstr("\nPush the committed changes? (y/n): ")
            stdscr.attroff(curses.color_pair(5))
            stdscr.refresh()

            while True:
                terminated = True
                push_key = stdscr.getch()
                if push_key in [ord("y"), ord("Y")]:
                    # User wants to push
                    # Run the git push command
                    push_command = ["git", "push"]
                    result = run_git_command(stdscr, push_command)
                    # result = True
                    if not result:
                        return
                    stdscr.attron(curses.color_pair(2))
                    stdscr.addstr("\nChanges pushed successfully.")
                    stdscr.attroff(curses.color_pair(2))
                    break
                elif push_key in [ord("n"), ord("N")]:
                    # User does not want to commit
                    stdscr.attron(curses.color_pair(3))
                    stdscr.addstr("\nOperation cancelled by the user.")
                    stdscr.attroff(curses.color_pair(3))
                    break
                else:
                    # Invalid key
                    continue
        elif commit_key in [ord("n"), ord("N")]:
            # User does not want to commit
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr("\nOperation cancelled by the user.")
            stdscr.attroff(curses.color_pair(3))
            break
        else:
            # Invalid key
            if terminated and commit_key in [10, 13]:
                break
            continue

    stdscr.refresh()
    stdscr.getch()


try:
    prompts = ["Enter commit title: ", "Enter commit message: "]
    confirmations = ["Commit title: ", "Commit message: "]
    curses.wrapper(main, prompts, confirmations)
except KeyboardInterrupt:
    print("\033[31m" + "\nOperation cancelled by the user." + "\033[0m")
except Exception as e:
    print("\033[31m" + "\n" + str(e) + "\033[0m")
