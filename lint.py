""" Functions to identify (but not fix) issues in man pages. """


def lines_contain_index(lines, substr):
    """ If substr apprears in any line, return that index; otherwise, None. """
    index = None
    for i, line in enumerate(lines):
        if substr in line:
            index = i
            break
    return index


def check_spdx(man):
    """ Check the location of any SPDX-License-Identifier line.

        If the full license is included, it should be before the license.
        If not, it should be after the copyright line.
    """
    preamble = man.get_preamble()

    # Bail if there's no SPDX-License
    spdx_index = lines_contain_index(preamble, "SPDX-License")
    if spdx_index is None:
        return

    license_index = lines_contain_index(preamble, "Redistribution and use")
    if license_index is None:
        # Does not have license text; we want SPDX after copyright.
        copyright_index = lines_contain_index(preamble, "Copyright")
        if copyright_index is None:
            return

        if spdx_index < copyright_index:
            print("%s: SPDX line is before the copyright" % man.filename)
    else:
        # Has full license text; we want SPDX before it.
        if spdx_index > license_index:
            print("%s: SPDX line is after the license" % man.filename)
