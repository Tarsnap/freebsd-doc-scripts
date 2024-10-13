""" Functions to fix issues in man pages. """


def sort_seealso(man):
    """ Sort the SEE ALSO section as expected by mandoc. """
    see_also = man.get_section("SEE ALSO")

    # Split into ".Xr" lines and any remaining ones.
    # FIXME: assume that all ".Xr" lines come first.  This is true for
    # the current set of files that `mandoc -T lint ...` warns about,
    # but it's not true of every single (currently-ok) man in -CURRENT.
    splitindex = None
    for i, x in enumerate(see_also):
        if not x.startswith(".Xr"):
            splitindex = i
            break
    if splitindex:
        xrs = see_also[:splitindex]
        rem = see_also[splitindex:]
    else:
        xrs = see_also
        rem = []

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
    man.replace_section("SEE ALSO", xrs + rem)
