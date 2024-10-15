""" Handle boilerplate for dealing with man files. """


class ManFile:
    """ A man page. """
    def __init__(self, filename):
        self.filename = filename
        self.lines = None
        self.modified = False
        self.section = {}
        self._section_reset()

        with open(self.filename, encoding="utf-8") as fp:
            self.lines = fp.read().splitlines()

    def _section_reset(self):
        self.section["name"] = None
        self.section["before"] = []
        self.section["middle"] = []
        self.section["after"] = []

    def save(self):
        """ If it was modified, write the man page back to disk. """
        if not self.modified:
            return

        text = "\n".join(self.lines) + "\n"
        with open(self.filename, "w", encoding="utf-8") as fp:
            fp.write(text)

    def is_modified(self):
        """ Was the file modified? """
        return self.modified

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
        self.section["name"] = section_name

        state = 0
        for line in self.lines:
            if state == 0:
                if line.startswith(".Sh %s" % section_name):
                    state = 1
                self.section["before"].append(line)
            elif state == 1:
                if line.startswith(".Sh "):
                    state = 2
                    self.section["after"].append(line)
                else:
                    self.section["middle"].append(line)
            else:
                self.section["after"].append(line)

        return self.section["middle"]

    def replace_section(self, section_name, lines):
        """ Replace a previously-extracted section.
            section_name must match the value given to get_section.
        """
        # Sanity check
        assert section_name == self.section["name"]

        if lines != self.section["middle"]:
            self.modified = True

        self.lines = self.section["before"] + lines + self.section["after"]
        self._section_reset()
