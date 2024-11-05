""" Handle boilerplate for dealing with a list of lines. """


class ManLinesSection:
    """ Keep track of a section of the ManLines. """
    def __init__(self, ml):
        self.ml = ml

        # Variables
        self.in_use = False
        self.middle_index = None
        self.after_index = None

    def reset(self):
        """ Reset the variables. """
        self.in_use = False
        self.middle_index = None
        self.after_index = None

    def get_lines(self):
        """ Get the lines described by this section. """
        assert self.in_use is True
        if self.middle_index is None or self.after_index is None:
            return None
        return self.ml[self.middle_index:self.after_index]


class ManLines(list):
    """ A list of lines. """
    def __init__(self, lines):
        super().__init__(lines)
        self.modified = False
        self.section = ManLinesSection(self)

    def three_way_split(self, func_middle_index, func_end):
        """ Split the lines into 3 lists:
            1) before func_middle_index is true
            2) before func_end is true
            3) everything remaining
        """
        assert self.section.in_use is False
        self.section.in_use = True

        state = 0
        for i, line in enumerate(self):
            if state == 0:
                if func_middle_index(line):
                    state = 1
                    self.section.middle_index = i
            elif state == 1:
                if func_end(line):
                    state = 2
                    self.section.after_index = i
            elif state == 2:
                pass

        # If the lines end while still in the middle section, end it.
        if state == 1:
            self.section.after_index = len(self)

        return self.section.get_lines()

    def replace_middle(self, newlines):
        """ Replace a previously-extracted section. """
        assert self.section.in_use is True

        if newlines == self.section.get_lines():
            self.section.reset()
            return

        # Replace the relevant lines
        self[self.section.middle_index:self.section.after_index] = newlines
        self.modified = True

        self.section.reset()