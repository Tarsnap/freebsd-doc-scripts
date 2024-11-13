""" Functions to fix issues in man pages. """

import freebsd_doc_scripts.man_lines


def sort_seealso(man, _args, _mlo=None):
    """ Sort the SEE ALSO section as expected by mandoc. """
    see_also = man.get_section("SEE ALSO")
    if not see_also:
        return

    # Split into ".Xr" lines and any remaining ones.  Assume that there is
    # a single block of ".Xr" lines.
    ml = freebsd_doc_scripts.man_lines.ManLines(see_also)
    xrs = ml.three_way_split(lambda x: x.startswith(".Xr"),
                             lambda x: not x.startswith(".Xr"))
    if not xrs:
        print("%s: skipping, SEE ALSO does not contain any .Xr" % man.filename)
        return

    # Strip commas (and periods, which shouldn't be in this section anyway!)
    xrs = [xr[:-2] if xr.endswith(" ,") else xr for xr in xrs]
    xrs = [xr[:-2] if xr.endswith(" .") else xr for xr in xrs]

    # Eliminate any duplicate lines.
    xrs = list(set(xrs))

    # Sort according to the order that mandoc wants:
    #   1) ascending by man section
    #   2) ascending by manpage name, case insensitive
    xrs.sort(key=lambda x: (x.split()[2], x.split()[1].lower()))

    # Re-add commas as appropriate, then we're done.
    xrs[:-1] = ["%s ," % x for x in xrs[:-1]]
    ml.replace_middle(xrs)
    man.replace_section("SEE ALSO", ml)


def pp_after(man, _args, mlo=None):
    """ Remove an incorrect .PP macro.  Requires mandoc lint output. """
    # Bail if we don't have mandoc_lint_output.
    if mlo is None:
        return

    # Adjust the line number to account for any previously-remove lines.
    index = mlo.line_number - 1 - man.get_num_removed_lines()

    # Sanity check.  (.LP is a synonym of PP)
    assert man.lines[index] == ".PP" or man.lines[index] == ".LP"

    # Remove the line that mandoc reported as a problem.
    man.remove_line(index)


def fix_backslashes(man, _args, _mlo=None):
    """ Fix incorrectly-written backslashes. """
    for i, line in enumerate(man.lines):
        if "\\\\" in line:
            newline = line.replace("\\\\", "\\e")
            man.replace_line(i, newline)


FIXES = {
    "unusual Xr order": sort_seealso,
    "skipping paragraph macro: PP after SS": pp_after,
    "skipping paragraph macro: PP after SH": pp_after,

    # This isn't a mandoc lint message.
    "backslashes": fix_backslashes,
}
