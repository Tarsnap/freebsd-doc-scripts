#!/bin/sh

# Generate list of man pages to check.
#
# According to CONTRIBUTING.md, these directories "likely has an upstream".
#   contrib/
#   crypto/
#   sys/cddl/
#   sys/contrib/
#   sys/crypto/
# In addition to that, ntp has an upstream.
#
# We also ignore /tests/ directories, plus 04.csh/ and cxgbetool.8 because
# they have an unusual amount of errors that aren't yet fixed.
if [ ! -e man-pages.txt ]; then
	git ls-files "*.[1-9]" --			\
		":(exclude)contrib/"			\
		":(exclude)crypto/"			\
		":(exclude)sys/cddl/"			\
		":(exclude)sys/contrib/"		\
		":(exclude)sys/crypto/"			\
							\
		":(exclude)bin/sh/tests/"		\
		":(exclude)share/doc/usd/04.csh/"	\
		":(exclude)share/man/man4/iwlwififw.4"	\
		":(exclude)usr.bin/bmake/tests/"	\
		":(exclude)usr.bin/sed/tests/"		\
		":(exclude)usr.sbin/cxgbetool/cxgbetool.8"	\
		":(exclude)usr.sbin/ntp/doc/ntp*"	\
		":(exclude)usr.sbin/ntp/doc/sntp.8"	\
		> man-pages.txt
fi

# Fix problems in those man pages.
if [ ! -e man-warnings.txt ]; then
	mandoc -T lint -W warning $(cat man-pages.txt) > man-warnings.txt
fi
