#!/usr/bin/env python3

""" Apply man fixes to the specified files. """

import argparse
import collections

import freebsd_doc_scripts.fixes
import freebsd_doc_scripts.lint
import freebsd_doc_scripts.man_file
import freebsd_doc_scripts.mandoc_lint_output


def _apply_funcs(man, args, notify, mlos, funcs_dict):
    """ Run (some) functions from func_dict on the man page.  If mlos is
        None, then run all the functions; otherwise, only run the
        functions(s) which correspond to messages in mlos.
    """
    if mlos is None:
        for fix_msg, func in funcs_dict.items():
            # Skip funcs if the message begins with an underscore
            if fix_msg.startswith("_"):
                continue

            # Apply the function.
            if func(man, args) or man.is_modified():
                notify[func.__name__] += 1
            man.clear_section()
        return

    # Sort mlos by line number: if any fixes remove a line, we need to
    # do those in order.
    mlos = sorted(mlos, key=lambda x: x.line_number)

    for mlo in mlos:
        for fix_msg, func in funcs_dict.items():
            # Skip funcs if the message begins with an underscore
            if fix_msg.startswith("_"):
                continue

            # Only run the specific fixes mentioned in mlo.
            if mlo.message.startswith(fix_msg):
                if func(man, args, mlo) or man.is_modified():
                    notify[func.__name__] += 1
                man.clear_section()


def process(filenames, args, mlos, funcs_dict):
    """ Run (some) functions from funcs_dict on the indicated files, save the
        modified file(s) (if applicable), and return a summary of the
        results.  If mlos is None, run all the functions; otherwise, only
        run the functions(s) which correspond to messages in mlos.
    """
    notify = collections.defaultdict(int)
    for filename in filenames:
        # Bail if we've acted on enough files.
        if args.max_files > 0 and sum(notify.values()) >= args.max_files:
            break

        # Load.
        man = freebsd_doc_scripts.man_file.ManFile(filename)

        # Get the relevant mandoc lint outputs.
        if mlos is None:
            relevant_mlos = None
        else:
            relevant_mlos = [mlo for mlo in mlos if mlo.filename == filename]

        # Process.
        _apply_funcs(man, args, notify, relevant_mlos, funcs_dict)

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
    parser.add_argument("--max-files", type=int, default=0,
                        help="Maximum number of files to fix")
    parser.add_argument("-f", "--filenames-list",
                        help="A file containing a list of man pages to fix")
    parser.add_argument("--mandoc-lint-output",
                        help="A file containing lint output from mandoc")
    parser.add_argument("filenames", nargs="*",
                        help="Specific man files to fix")
    args = parser.parse_args()

    # Sanity checks: exactly one set of filenames.
    num_args_filenames = ((len(args.filenames) > 0) +
                          (args.filenames_list is not None) +
                          (args.mandoc_lint_output is not None))
    if num_args_filenames > 1:
        print("Cannot specify -f and filenames on the command line")
        exit(1)
    if num_args_filenames == 0:
        print("Must specify one -f, --mandoc-lint-output, or filenames"
              " on the command line")
        exit(1)

    return args


def main():
    """ Apply man fixes to the specified files. """
    args = parse_args()
    mlos = None

    # Get the list of filenames from the appropriate location.
    if args.mandoc_lint_output:
        mlos = freebsd_doc_scripts.mandoc_lint_output.parse(
            args.mandoc_lint_output)
        filenames = sorted({m.filename for m in mlos})
    elif args.filenames:
        filenames = args.filenames
    else:
        with open(args.filenames_list, encoding="utf-8") as fp:
            filenames = fp.read().splitlines()

    # Do linting or fixes.
    if args.lint:
        funcs_dict = freebsd_doc_scripts.lint.CHECKS
    else:
        funcs_dict = freebsd_doc_scripts.fixes.FIXES
    notify = process(filenames, args, mlos, funcs_dict)

    # Print summary of issues.
    print("Processed %i files, problems in %i" % (
          len(filenames), sum(notify.values())))
    for key, value in notify.items():
        print("\t%s:\t%i" % (key, value))


if __name__ == "__main__":
    main()
