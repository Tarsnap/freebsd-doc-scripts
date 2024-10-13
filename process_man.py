#!/usr/bin/env python3

""" Apply man fixes to the specified files. """

import argparse

import fixes
import lint
import man_file


def parse_args():
    """ Parse the command-line arguments. """
    parser = argparse.ArgumentParser(
                 description="Fix some elements of man files")
    parser.add_argument("--lint", action="store_true",
                        help="Run checks without fixing anything")
    parser.add_argument("-f", "--filenames-list",
                        help="A file containing a list of man pages to fix")
    parser.add_argument("filenames", nargs="*",
                        help="Specific man files to fix")
    args = parser.parse_args()

    # Sanity checks
    if args.filenames and args.filenames_list:
        print("Cannot specify -f and filenames on the command line")
        exit(1)
    if not args.filenames and not args.filenames_list:
        print("Must specify one -f or filenames on the command line")
        exit(1)

    return args


def main():
    """ Apply man fixes to the specified files. """
    args = parse_args()

    # Get the list of filenames from the appropriate location.
    if args.filenames:
        filenames = args.filenames
    else:
        with open(args.filenames_list, encoding="utf-8") as fp:
            filenames = fp.read().splitlines()

    # Apply fixes to all those files.
    for filename in filenames:
        man = man_file.ManFile(filename)
        if args.lint:
            lint.check_spdx(man)
        else:
            fixes.sort_seealso(man)
            man.save()


if __name__ == "__main__":
    main()
