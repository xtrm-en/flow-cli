import sys

from fart.utils import xlog
import inquirer


def main() -> None:
    xlog("Welcome to F.A.R.T.")
    sys.stdout.flush()

    questions = [
        inquirer.Checkbox('interests',
                          message="What are you interested in?",
                          choices=['Computers', 'Books', 'Science', 'Nature', 'Fantasy', 'History'],
                          ),
    ]
    answers = inquirer.prompt(questions)
    print(answers['interests'])
