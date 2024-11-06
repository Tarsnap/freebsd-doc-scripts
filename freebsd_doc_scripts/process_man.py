#!/usr/bin/env python3

""" Apply man fixes to the specified files. """

import argparse
import collections

import freebsd_doc_scripts.fixes
import freebsd_doc_scripts.lint
import freebsd_doc_scripts.man_file


def do_lint(filenames, args):
    """ Apply lint checks to man pages. """
    notify = collections.defaultdict(int)
    for filename in filenames:
        # Load.
        man = freebsd_doc_scripts.man_file.ManFile(filename)

        # Process.
        for check in freebsd_doc_scripts.lint.CHECKS:
            if check(man, args):
                notify[check.__name__] += 1

    return notify


def do_fixes(filenames, args):
    """ Apply fixes to man pages. """
    notify = collections.defaultdict(int)
    for filename in filenames:
        # Load.
        man = freebsd_doc_scripts.man_file.ManFile(filename)

        # Process.
        for _, fix_func in freebsd_doc_scripts.fixes.FIXES.items():
            fix_func(man, args)
            if man.is_modified():
                notify[fix_func.__name__] += 1

        # Save (if modified).
        if not args.dry_run:
            man.save()

    return notify


def parse_args():
    """ Parse the command-line arguments. """
    parser = argparse.ArgumentParser(
                 description="Fix some elements of man files")
    parser.add_argument("--debug", action="store_true",
                        help="Print additional info (certain lints or fixes)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't write any files to disk")
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

    # Do linting or fixes.
    if args.lint:
        notify = do_lint(filenames, args)
    else:
        notify = do_fixes(filenames, args)

    # Print summary of issues.
    print("Processed %i files, problems in %i" % (
          len(filenames), sum(notify.values())))
    for key, value in notify.items():
        print("\t%s:\t%i" % (key, value))


if __name__ == "__main__":
    main()
