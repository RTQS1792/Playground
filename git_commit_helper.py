import subprocess
import re

IGNORED_WORDS = {'and', 'or', 'but', 'the', 'a', 'in', 'with', 'to', 'of', 'on'}

def process_code_string(title: str, ignored_words: set = None) -> str:
    if ignored_words is None:
        ignored_words = set()

    words = title.split()
    processed_words = []
    processing_words = []

    tick_open = False
    ext_regex = re.compile(r'\.[a-zA-Z0-9]+$')  # Regular expression to match file extensions

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
            processed_words.append(
                word if word.lower() in ignored_words and idx != 0 else word.capitalize()
            )
            continue

    # If at the end of the title but tick is still open
    if tick_open:
        param = processing_words.pop(0)
        processed_words.append(param + "`")
        for pword in processing_words:
            processed_words.append(pword if pword.lower() in ignored_words else pword.capitalize())
        processing_words.clear()
    
    return ' '.join(processed_words)


def test_input():
    test_messages = [
        "`test.py here and this should be capitalized and this `test2.py too",
        "this is a test `file.txt here",
        "`file with no extension here and then normal words",
        "just some regular words with no special characters",
        "`this has no end tick",
        "`this` has `matching` ticks",
        "a mix of `non-matching and `matching` ticks",
        "A mix of `word and `some code.ext and nothing",
        "a mix of `some code.ext and `word and nothing",
        "a complete message with `some code.ext` and `word` and nothing"
    ]

    expected_results = [
        "`test.py` Here And This Should Be Capitalized And This `test2.py` Too",
        "This Is A Test `file.txt` Here",
        "`file` With No Extension Here And Then Normal Words",
        "Just Some Regular Words With No Special Characters",
        "`this` Has No End Tick",
        "`this` Has `matching` Ticks",
        "A Mix Of `non-matching` And `matching` Ticks",
        "A Mix Of `word` And `some code.ext` And Nothing",
        "A Mix Of `some code.ext` And `word` And Nothing",
        "A Complete Message With `some code.ext` And `word` And Nothing"
    ]

    # Test the function
    for msg, expected in zip(test_messages, expected_results):
        result = process_code_string(msg, IGNORED_WORDS)
        print("Original:", msg)
        print("Result:  ", result)
        print("Expected:", expected)
        # If success, print in green; otherwise, print in red
        if result == expected:
            print("\033[32m" + "Success!" + "\033[0m")
        else:
            print("\033[31m" + "Failed!" + "\033[0m")
        print("---")

def get_user_input(prompt: str, color_code="\033[33m") -> str:
    try:
        return input(f"{color_code}{prompt.ljust(25)}\033[0m")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        exit()

def run_git_command(command: list):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        print("\033[31m" + "Git command failed!" + "\033[0m")
        exit()

def commit_changes(title: str, message: str):
    formatted_title = process_code_string(title, IGNORED_WORDS)
    formatted_message = message.capitalize()
    
    if not formatted_message.endswith('.'):
        formatted_message += "."
    
    print(f"\033[32mCommit title:\t\t\033[0m {formatted_title}")
    print(f"\033[32mCommit message:\t\t\033[0m {formatted_message}")

    # Confirm before committing
    confirm = get_user_input("Commit changes? (y/n): ")
    if confirm.lower() == 'y':
        run_git_command(["git", "add", "--all"])
        run_git_command(["git", "commit", "-m", formatted_title, "-m", formatted_message])
        print("\033[32m" + "Changes committed successfully!" + "\033[0m")
    else:
        print("\033[31m" + "Operation cancelled by user." + "\033[0m")

# Main interaction
if __name__ == "__main__":
    title = get_user_input("Enter commit title: ")
    message = get_user_input("Enter commit message: ")
    commit_changes(title, message)
