# -*- coding: utf-8 -*-
import inquirer


def prompt(questions: list):
    """Wraps the inquirer#prompt function to allow for custom output hooking."""
    from flow.launcher import hijack_streams, restore_streams
    restore_streams()
    answers = inquirer.prompt(questions)
    hijack_streams()
    return answers
