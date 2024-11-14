""" Handle boilerplate for dealing with man files. """

import freebsd_doc_scripts.man_lines


class ManFile:
    """ A man page. """
    def __init__(self, filename):
        self.filename = filename
        self.lines = None
        self.section_name = None

        with open(self.filename, encoding="utf-8") as fp:
            lines = fp.read().splitlines()
            self.lines = freebsd_doc_scripts.man_lines.ManLines(lines)

    def save(self):
        """ If it was modified, write the man page back to disk. """
        if not self.lines.modified:
            return

        text = "\n".join(self.lines) + "\n"
        with open(self.filename, "w", encoding="utf-8") as fp:
            fp.write(text)

    def clear_section(self):
        """ Clear any in-use sections. """
        self.lines.clear_section()
        self.section_name = None

    def is_modified(self):
        """ Was the file modified? """
        return self.lines.modified

    def get_preamble(self):
        """ Get the commented-out lines at the beginning of the file. """
        index = None
        for i, line in enumerate(self.lines):
            if not line.startswith(".\\"):
                index = i
                break
        if index:
            preamble = self.lines[:index]
        else:
            preamble = []

        return preamble

    def get_section(self, section_name):
        """ Get a section of the man page. """
        self.section_name = section_name

        middle = self.lines.three_way_split(
            lambda x: x.startswith(".Sh %s" % section_name),
            lambda x: x.startswith(".Sh "))

        return middle

    def replace_section(self, section_name, newlines):
        """ Replace a previously-extracted section.
            section_name must match the value given to get_section.
        """
        # Sanity check
        assert section_name == self.section_name

        self.lines.replace_middle(newlines)

    def remove_line(self, index):
        """ Remove a line. """
        # Sanity check
        assert self.section_name is None

        self.lines.remove_line(index)

    def replace_line(self, index, newline):
        """ Replace a line. """
        # Sanity check
        assert self.section_name is None

        self.lines.replace_line(index, newline)

    def get_line_delta_count(self):
        """ Get the difference between current and original line numbers.

            For example, if one line was removed, this would return -1;
            if three lines were then added, this would return 2.
        """
        return self.lines.line_delta_count
