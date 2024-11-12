""" Handle output from `mandoc -T lint ...` """

import collections


MandocLintOutput = collections.namedtuple("MandocLintOutput",
                                          ["filename", "line_number",
                                           "col_number", "severity",
                                           "message"])


def parse_mandoc_lint_line(line):
    """ Parse a line of output from `mandoc -T lint ...` """
    split_line = line.split()
    filename_line_column = split_line[1].split(":")
    filename = filename_line_column[0]
    line_number = int(filename_line_column[1])
    column_number = int(filename_line_column[2])
    severity = split_line[2][:-1]
    message = " ".join(split_line[3:])

    return MandocLintOutput(filename, line_number, column_number, severity,
                            message)


def parse(filename):
    """ Parse a file containing output from `mandoc -T lint ...` """
    with open(filename, encoding="utf-8") as fp:
        lines = fp.readlines()

    lint_outputs = []
    for line in lines:
        lint_outputs.append(parse_mandoc_lint_line(line))

    return lint_outputs
