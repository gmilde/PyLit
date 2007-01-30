#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ===============================================================
# pylit.py: Literate programming with Python and reStructuredText
# ===============================================================
# 
# :Version:   0.2.3
# :Date:      2007-01-26
# :Copyright: 2005, 2007 Guenter Milde.
#             Released under the terms of the GNU General Public License 
#             (v. 2 or later)
# 
# .. contents::
# 
# Frontmatter
# ===========
# 
# Changelog
# ---------
# 
# :2005-06-29: Initial version
# :2005-06-30: first literate version of the script
# :2005-07-01: object orientated script using generators
# :2005-07-10: Two state machine (later added 'header' state)
# :2006-12-04: Start of work on version 0.2 (code restructuring)
# :2007-01-23: 0.2 published at http://pylit.berlios.de
# :2007-01-25: 0.2.1: Outsorced non-core documentation to the PyLit pages.
# :2007-01-26: 0.2.2: new behaviour of diff()
# :2007-01-29: 0.2.3: new `header` methods after suggestion by Riccardo Murri
# 
# ::

"""pylit: Literate programming with Python and reStructuredText
   Convert between 
   
   * reStructured Text with embedded code, and
   * Source code with embedded text comment blocks
"""

__docformat__ = 'restructuredtext'


# Requirements
# ------------
# 
# * library modules
# 
# ::

import os
import sys
import optparse

# * non-standard extensions
# 
# ::

from simplestates import SimpleStates  # generic state machine

# The PushIterator is a minimal implementation of an iterator with
# backtracking from the `Effective Python Programming`_ OSCON 2005 tutorial by
# Anthony Baxter. As the definition is small, it is inlined now. For the full
# reasoning and doc see `iterqueue.py`_.
# 
# .. _`Effective Python Programming`: 
#    http://www.interlink.com.au/anthony/tech/talks/OSCON2005/effective_r27.pdf
# 
# .. _iterqueue.py: iterqueue.py.html
# 
# ::

class PushIterator:
    def __init__(self, iterable):
        self.it = iter(iterable)
        self.cache = []
    def __iter__(self):
        """Return `self`, as this is already an iterator"""
        return self
    def next(self):
        return (self.cache and self.cache.pop()) or self.it.next()
    def push(self, value):
        self.cache.append(value)

# Classes
# =======
# 
# Converter
# ---------
# 
# The `Text2Code`_ class converts reStructured text to executable code, while
# the `Code2Text`_ class does the opposite: converting commented code to
# text.
# 
# The converters implement a simple `state machine` to separate and transform
# text and code blocks. For this task, only a very limited parsing is needed:
# 
# * indented literal blocks in a text source are considered code blocks.
# 
# * non-indented comments in a code source are considered text blocks.
# 
# Using the full blown docutils_ rst parser would introduce a large overhead
# and slow down the conversion. 
# 
# .. _docutils: http://docutils.sourceforge.net/
# 
# The generic `PyLitConverter` class inherits the state machine framework
# (initalisation, scheduler, iterator interface, ...) from `SimpleStates`,
# overrides the ``__init__`` method, and adds auxiliary methods and
# configuration attributes (options). 
# 
# ::

class PyLitConverter(SimpleStates):
    """parent class for `Text2Code` and `Code2Text`, the state machines
    converting between text source and code source of a literal program.
    """

# Data attributes
# ~~~~~~~~~~~~~~~
# 
# ::

    comment_strings = {"python": "# ", 
                       "slang": "% ", 
                       "c++": "// "}
    # default values override with keyword args to __init__
    language = "python"
    strip = False
    keep_lines = False
    state = 'header'   # initial state
    codeindent = 2

# Instantiation
# ~~~~~~~~~~~~~
# 
# Initializing sets up the `data` attribute, an iterable object yielding
# lines of the source to convert.[1]_   ::

    def __init__(self, data, **keyw):
        """data   --  iterable data object 
                      (list, file, generator, string, ...)
           **keyw --  all remaining keyword arguments are 
                      stored as class attributes 
        """

# As the state handlers need backtracking, the data is wrapped in a
# `PushIterator`::

        self.data = PushIterator(data)
        self._textindent = 0

# Additional keyword arguments are stored as data attributes, overwriting the
# class defaults::

        self.__dict__.update(keyw)
            
# The comment string is set to the languages comment string if not given in
# the keyword arguments::

        if not hasattr(self, "comment_string"):
            self.comment_string = self.comment_strings[self.language]

# .. [1] The most common choice of data is a ``file`` object with the text
#        or code source.
# 
#        To convert a string into a suitable object, use its splitlines method
#        with the optional `keepends` argument set to True.
# 
# Converter.__str__
# ~~~~~~~~~~~~~~~~~
# 
# Return converted data as string::

    def __str__(self):
        blocks = ["".join(block) for block in self()]
        return "".join(blocks)

# Converter.get_indent
# ~~~~~~~~~~~~~~~~~~~~
# 
# Return the number of leading spaces in `string` after expanding tabs ::

    def get_indent(self, string):
        """Return the indentation of `string`.
        """
        line = string.expandtabs()
        return len(line) - len(line.lstrip())

# Converter.ensure_trailing_blank_line
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# Ensure there is a blank line as last element of the list `lines`.
# 
# Pass, if self.strip == True or the `lines` list is empty ::

    def ensure_trailing_blank_line(self, lines, line):
        if self.strip or not lines:
            return
        if lines[-1].lstrip(): 
            sys.stderr.write("\nWarning: inserted blank line between\n %s %s"
                             %(lines[-1], line))
            lines.append("\n")


# Text2Code
# ---------
# 
# The `Text2Code` class separates code blocks (indented literal blocks) from
# reStructured text. Code blocks are unindented, text is commented (or
# filtered, if the ``strip`` option is True.
# 
# Only `indented literal blocks` are extracted. `Quoted literal blocks` and
# `pydoc blocks` are treated as text. This allows the easy inclusion of
# examples:
# 
#    >>> 23 + 3
#    26
# 
# The state handlers are implemented as generators. Iterating over a
# `Text2Code` instance initializes them to generate iterators for
# the respective states (see ``simplestates.py``).
# 
# ::

class Text2Code(PyLitConverter):
    """Convert a (reStructured) text source to code source
    """

# Text2Code.header
# ~~~~~~~~~~~~~~~~
# 
# Convert the header (leading rst comment block) to code::

    def header(self):
        """Convert header (comment) to code"""
        line = self.data_iterator.next()

# Test first line for rst comment: Which variant is better?
# 
# 1. starts with comment marker and has
#    something behind the comment on the first line::

        if line.startswith("..") and len(line.rstrip()) > 2:

# 2. Convert any leading comment to code::

        #if line.startswith(".."):
            self.data_iterator.push(line.replace("..", "", 1))
            return self.code()
        
# No header code found: Push back first non-header line and set state to
# "text"::

        self.data_iterator.push(line)
        self.state = "text"
        return []

# Text2Code.text_handler_generator
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# The 'text' handler processes everything that is not an indented literal
# comment. Text is quoted with the comment_string or filtered (with
# strip=True). 
# 
# It is implemented as a generator function that acts on the `data` iterator
# and yields text blocks.
# 
# Declaration and initialization::

    def text_handler_generator(self):
        """Convert text blocks from rst to comment
        """
        lines = []
        
# Iterate over the data_iterator (which yields the data lines)::
          
        for line in self.data_iterator:
            # print "Text: '%s'"%line
            
# Default action: add comment string and collect in `lines` list
# Skip if ``self.strip`` evaluates to True::

            if not self.strip:
                lines.append(self.comment_string + line)
                
# Test for the end of the text block: a line that ends with `::` but is neither
# a comment nor a directive::

            if (line.rstrip().endswith("::")
                and not line.lstrip().startswith("..")):
                
# End of text block is detected, now:
# 
# set the current text indent level (needed by the code handler to find the
# end of code block) and set the state to "code" (i.e. the next call of
# `self.next` goes to the code handler)::

                self._textindent = self.get_indent(line)
                self.state = 'code'
                
# Ensure a trailing blank line (which is the paragraph separator in
# reStructured Text. Look at the next line, if it is blank, ok, if it is not
# blank, push it back (it should be code) and add a line by calling the
# `ensure_trailing_blank_line` method (which also issues a warning)::

                line = self.data_iterator.next()
                if line.lstrip():
                    self.data_iterator.push(line) # push back
                    self.ensure_trailing_blank_line(lines, line)
                elif not self.strip:
                    lines.append(line)

# Now yield and reset the lines. (There was a function call to remove a
# literal marker (if on a line on itself) to shorten the comment. However,
# this behaviour was removed as the resulting difference in line numbers leads
# to misleading error messages in doctests)::

                #remove_literal_marker(lines)
                yield lines
                lines = []
                
# End of data: if we "fall of" the iteration loop, just join and return the
# lines::

        yield lines


# Text2Code.code_handler_generator
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# The `code` handler is called when a literal block marker is encounterd. It
# returns a code block (indented literal block), removing leading whitespace
# up to the indentation of the first code line in the file (this deviation
# from docutils behaviour allows indented blocks of Python code).
# 
# As the code handler detects the switch to "text" state by looking at
# the line indents, it needs to push back the last probed data token. I.e.
# the  data_iterator must support the `.push()` method. (This is the
# reason for the use of the PushIterator class in `__init__`.) ::

    def code_handler_generator(self):
        """Convert indented literal blocks to source code
        """
        lines = []
        codeindent = None # indent of first non-blank code line, set below
        for line in self.data_iterator:
            # print "Code: '%s'"%line
            # pass on empty lines (no whitespace except newline)
            if not line.rstrip("\n"):
                lines.append(line)
                continue

# Test for end of code block:
# 
# A literal block ends with the first less indented, nonblank line.
# `self._textindent` is set by the text handler to the indent of the
# preceding paragraph. 
# 
# To prevent problems with different tabulator settings, hard tabs in code
# lines  are expanded with the `expandtabs` string method when calculating the
# indentation (i.e. replaced by 8 spaces, by default).
# 
# ::

            if line.lstrip() and self.get_indent(line) <= self._textindent:
                # push back line
                self.data_iterator.push(line) 
                self.state = 'text'
                # append blank line (if not already present)
                self.ensure_trailing_blank_line(lines, line)
                yield lines
                # reset list of lines
                lines = []
                continue
            
            # Determine the code indentation from first non-blank code line
            if codeindent is None and line.lstrip():
                codeindent = self.get_indent(line)
            
            # default action: append unindented line
            # (in case the line is shorter than codeindent but not totally
            # empty, append only a newline.)
            lines.append(line[codeindent:] or "\n")
        yield lines
                        

# Txt2Code.remove_literal_marker
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# Remove literal marker (::) in "expanded form" i.e. in a paragraph on its own.
# 
# While cleaning up the code source, it leads to confusion for doctest and
# searches (e.g. grep) as line-numbers between text and code source will
# differ. ::

    def remove_literal_marker(list):
        try:
            # print lines[-3:]
            if (lines[-3].strip() == self.comment_string.strip() 
                and lines[-2].strip() == self.comment_string + '::'):
                del(lines[-3:-1])
        except IndexError:
            pass


# Code2Text
# ---------
# 
# The `Code2Text` class does the opposite of `Text2Code`_ -- it processes
# valid source code, extracts comments, and puts non-commented code in literal
# blocks. 
# 
# Only lines starting with a comment string matching the one in the
# `comment_string` data attribute are considered text lines.
# 
# The class is derived from the PyLitConverter state machine and adds handlers
# for the three states "header", "text", and "code". ::

class Code2Text(PyLitConverter):
    """Convert code source to text source
    """

# Code2Text.header
# ~~~~~~~~~~~~~~~~
# 
# Sometimes code needs to remain on the first line(s) of the document to be
# valid. The most common example is the "shebang" line that tells a POSIX
# shell how to process an executable file::

#!/usr/bin/env python

# In Python, the ``# -*- coding: iso-8859-1 -*-`` line must occure before any
# other comment or code.
# 
# If we want to keep the line numbers in sync for text and code source, the
# reStructured Text markup for these header lines must start at the same line
# as the first header line. Therfore, header lines could not be marked as
# literal block (this would require the "::" and an empty line above the code).
# 
# OTOH, a comment may start at the same line as the comment marker and it
# includes subsequent indented lines. Comments are visible in the reStructured
# Text source but hidden in the pretty-printed output.
# 
# With a header converted to comment in the text source, everything before the
# first text block (i.e. before the first paragraph using the matching comment
# string) will be hidden away (in HTML or PDF output). 
# 
# This seems a good compromise, the advantages
# 
# * line numbers are kept
# * the "normal" code conversion rules (indent/unindent by `codeindent` apply
# * greater flexibility: you can hide a repeating header in a project
#   consisting of many source files.
# 
# set off the disadvantages
# 
# - it may come as surprise if a part of the file is not "printed",
# - one more syntax element to learn for rst newbees to start with pylit,
#   (however, starting from the code source, this will be auto-generated)
# 
# In the case that there is no matching comment at all, the complete code
# source will become a comment -- however, in this case it is not very likely
# the source is a literate document.
# 
# If needed for the documentation, it is possible to repeat the header in (or
# after) the first text block, e.g. with a *line block* in a *block quote*:
# 
#   |  ``#!/usr/bin/env python``
#   |  ``# -*- coding: iso-8859-1 -*-``
# 
# ::

    def header(self):
        """Convert leading code to rst comment"""

# Test first line for text or code and push back::

        line = self.data_iterator.next()
        self.data_iterator.push(line)
        
        if line.startswith(self.comment_string):
            self.state = "text"
            return []

# Leading code detected: handle with the `code` method and prepend a rst
# comment marker to the first line. (One could be even more flexible by
# storing the "header-marker-string" in a class data argument.) ::

        lines = self.code()
        if lines:
            lines[0] = ".." + lines[0]
        return lines
            
            
# Code2Text.text_handler_generator
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# The text handler converts a comment to a text block if it matches the
# following requirements:
# 
# * every line starts with a matching comment string (test includes whitespace!)
# * comment is separated from code by a blank line (the paragraph separator in
#   reStructuredText)
# 
# It is implemented as a generator function that acts on the `data` iterator
# and yields text blocks.
# 
# Text is uncommented. A literal block marker is appended, if not already
# present. If `self.strip` evaluates to `True`, text is filtered.
# ::

    def text_handler_generator(self):
        """Uncomment text blocks in source code
        """
        lines = []
        
# Iterate over the data lines (remember, code lines are processed by the code
# handler and not seen here). ::
          
        for line in self.data_iterator:
              # print "Text: " + line
              
# Pass on blank lines. Strip comment string from otherwise blank lines
# (trailing whitespace in the `comment_string` is not significant for blank
# lines). Continue with the next line, as there is no need to test blank lines
# for the end of text. ::

            if not line.lstrip():
                lines.append(line)
                continue
            if line.rstrip() == self.comment_string.rstrip():
                lines.append("\n")
                continue

# Test for end of text block: the first line that doesnot start with a
# matching comment string. This tests also whitespace that is part of the
# comment string! ::

            if not line.startswith(self.comment_string):
            
# End of text block: Push back the line and let the "code" handler handle it
# (and subsequent lines)::
              
                self.state = 'code'
                self.data_iterator.push(line)

# Also restore and push back lines that precede the next code line without a
# blank line (paragraph separator) inbetween::
                  
                while lines and lines[-1].lstrip():
                    line = self.comment_string + lines.pop()
                    self.data_iterator.push(line)
                    
# Ensure literal block marker (double colon) at the end of the text block::

                if (not self.strip and len(lines)>1 
                    and not lines[-2].rstrip().endswith("::")):
                     lines.extend(["::\n", "\n"])
                     
# Yield the text block, reset the cache, continue with next line (when the
# state is again set to "text")::
                       
                yield lines
                lines = []
                continue
                
# Test passed: It's text line. Strip the comment string and append to the
# `lines` cache::

            lines.append(line[len(self.comment_string):])
            
# No more lines: Just return the remaining lines::
              
        yield lines

    
# Code2Text.code_handler_generator
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# The `code` method is called on non-commented code. Code is returned as
# indented literal block (or filtered, if ``strip=True``). The amount of the
# code indentation is controled by `self.codeindent` (default 2). 
# 
# ::

    def code_handler_generator(self):
        """Convert source code to indented literal blocks.
        
        Filter code blocks if self.strip is True
        """
        lines = []
        for line in self.data_iterator:
            # yield "Code: " + line
            # pass on empty lines (only newline)
            if line == "\n":
                lines.append(line)
                continue
            # # strip comment string from blank lines
            # if line.rstrip() == self.comment_string.rstrip():
            #     lines.append("\n")
            #     continue
            
# Test for end of code block: nonindented matching comment string following a
# blank line. A comment string matche includes whitespace normally but ignores
# trailing whitespace if the line after the comment is blank. ::

            if (line.startswith(self.comment_string) or
                line.rstrip() == self.comment_string.rstrip()
               ) and lines and not lines[-1].strip():
                self.data_iterator.push(line)
                self.state = 'text'
                # self.ensure_trailing_blank_line(lines, line)
                if self.strip:
                    yield []
                else:
                    yield lines
                # reset
                lines = []
                continue
            # default action: indent
            lines.append(" "*self.codeindent + line)
        # no more lines in data_iterator
        if self.strip:
            yield []
        else:
            yield lines
        

# Command line use
# ================
# 
# Using this script from the command line will convert a file according to its
# extension. This default can be overridden by a couple of options.
# 
# Recognised Filename Extensions
# ------------------------------
# 
# Finding an easy to remember, unused filename extension is not easy.
# 
# .py.txt
#   a double extension (similar to .tar.gz, say) seems most appropriate
#   (at least on UNIX). However, it fails on FAT16 filesystems.
#   The same scheme can be used for c.txt, p.txt and the like.
# 
# .pytxt
#   is recognised as extension by os.path.splitext but also fails on FAT16
# 
# .pyt 
#   (PYthon Text) is used by the Python test interpreter
#   `pytest <http:www.zetadev.com/software/pytest/>`__
# 
# .pyl
#   was even mentioned as extension for "literate Python" files in an
#   email exchange (http://www.python.org/tim_one/000115.html) but 
#   subsequently used for Python libraries.
# 
# .lpy 
#   seems to be free (as by a Google search, "lpy" is the name of a python
#   code pretty printer but this should not pose a problem).
# 
# .tpy
#   seems to be free as well.
# 
# Instead of defining a new extension for "pylit" literate programms,
# by default ``.txt`` will be appended for literate code and stripped by
# the conversion to executable code. i.e. for a program foo:
# 
# * the literate source is called ``foo.py.txt``
# * the html rendering is called ``foo.py.html``
# * the python source is called ``foo.py``
# 
# OptionValues
# ------------
# 
# For use as keyword arguments, it is handy to have the options
# in a dictionary. The following class adds an `as_dict` method
# to  `optparse.Values`::

class OptionValues(optparse.Values):
    def as_dict(self):
        """Return options as dictionary object"""
        return dict([(option, getattr(self, option)) for option in dir(self)
                     if option not in dir(OptionValues)
                     and option is not None
                    ])
 
# PylitOptions
# ------------
# 
# Options are stored in the values attribute of the `PylitOptions` class.
# It is initialized with default values and parsed command line options (and
# arguments)  This scheme allows easy customization by code importing the
# `pylit` module. ::

class PylitOptions:
    """Storage and handling of program options
    """

# Recognized file extensions for text and code versions of the source:: 

    code_languages = {".py": "python", ".sl": "slang", ".c": "c++"}
    code_extensions = code_languages.keys()
    text_extensions = [".txt"]

# Instantiation
# ~~~~~~~~~~~~~
# 
# Instantiation sets up an OptionParser and initializes it with pylit's
# command line options and `default_values`. It then updates the values based
# on command line options and sensible defaults::

    def __init__(self, args=sys.argv[1:], **default_values):
        """Set up an `OptionParser` instance and parse and complete arguments
        """
        p = optparse.OptionParser(usage=main.__doc__, version="0.2")
        # set defaults
        p.set_defaults(**default_values)
        # add the options
        p.add_option("-c", "--code2txt", dest="txt2code", action="store_false",
                     help="convert code to reStructured text")
        p.add_option("--doctest", action="store_true",
                     help="run doctest.testfile() on the text version")
        p.add_option("-e", "--execute", action="store_true",
                     help="execute code (implies -c, Python only)")
        p.add_option("-f", "--infile",
                     help="input file name ('-' for stdout)" )
        p.add_option("--overwrite", action="store", 
                     choices = ["yes", "update", "no"],
                     help="overwrite output file (default 'update')")
        p.add_option("-o", "--outfile",
                     help="output file name ('-' for stdout)" )
        p.add_option("--replace", action="store_true",
                     help="move infile to a backup copy (appending '~')")
        p.add_option("-s", "--strip", action="store_true",
                     help="strip comments|code")
        p.add_option("-t", "--txt2code", action="store_true",
                     help="convert reStructured text to code")
        p.add_option("-d", "--diff", action="store_true", 
                     help="do a round-trip and test for differences")
        self.parser = p
        
        # parse to fill a self.Values instance
        self.values = self.parse_args(args)
        # complete with context-sensitive defaults
        self.values = self.complete_values(self.values)

# Calling
# ~~~~~~~
# 
# "Calling" an instance updates the option values based on command line
# arguments and default values and does a completion of the options based on
# "context-sensitive defaults"::

    def __call__(self, args=sys.argv[1:], **default_values):
        """parse and complete command line args
        """
        values = self.parse_args(args, **default_values)
        return self.complete_values(values)


# PylitOptions.parse_args
# ~~~~~~~~~~~~~~~~~~~~~~~
# 
# The `parse_args` method calls the `optparse.OptionParser` on command
# line or provided args and returns the result as `PylitOptions.Values`
# instance.  Defaults can be provided as keyword arguments::

    def parse_args(self, args=sys.argv[1:], **default_values):
        """parse command line arguments using `optparse.OptionParser`
        
           args           --  list of command line arguments.
           default_values --  dictionary of option defaults
        """
        # update defaults
        defaults = self.parser.defaults.copy()
        defaults.update(default_values)
        # parse arguments
        (values, args) = self.parser.parse_args(args, OptionValues(defaults))
        # Convert FILE and OUTFILE positional args to option values
        # (other positional arguments are ignored)
        try:
            values.infile = args[0]
            values.outfile = args[1]
        except IndexError:
            pass
        return values

# PylitOptions.complete_values
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# The `complete` method uses context information to set missing option values
# to sensible defaults (if possible).
# 
# ::

    def complete_values(self, values):
        """complete option values with context sensible defaults
        """
        values.ensure_value("infile", "")
        # Guess conversion direction from infile filename
        if values.ensure_value("txt2code", None) is None:
            in_extension = os.path.splitext(values.infile)[1]
            if in_extension in self.text_extensions:
                values.txt2code = True
            elif in_extension in self.code_extensions:
                values.txt2code = False
        # Auto-determine the output file name
        values.ensure_value("outfile", self.get_outfile_name(values.infile, 
                                                             values.txt2code))
        # Guess conversion direction from outfile filename or set to default
        if values.txt2code is None:
            out_extension = os.path.splitext(values.outfile)[1]
            values.txt2code = not (out_extension in self.text_extensions)
        
        # Set the language of the code (default "python")
        if values.txt2code is True:
            code_extension = os.path.splitext(values.outfile)[1]
        elif values.txt2code is False:
            code_extension = os.path.splitext(values.infile)[1]
        values.ensure_value("language", 
                            self.code_languages.get(code_extension, "python"))
        
        # Set the default overwrite mode
        values.ensure_value("overwrite", 'update')

        return values

# PylitOptions.get_outfile_name
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# Construct a matching filename for the output file. The output filename is
# constructed from `infile` by the following rules:
# 
# * '-' (stdin) results in '-' (stdout)
# * strip the `txt_extension` or add the `code_extension` (txt2code)
# * add a `txt_ extension` (code2txt)
# * fallback: if no guess can be made, add ".out"
# 
# ::

    def get_outfile_name(self, infile, txt2code=None):
        """Return a matching output filename for `infile`
        """
        # if input is stdin, default output is stdout
        if infile == '-':
            return '-'
        # Modify `infile`
        (base, ext) = os.path.splitext(infile)
        # TODO: should get_outfile_name() use self.values.outfile_extension
        #       if it exists?
        
        # strip text extension
        if ext in self.text_extensions: 
            return base
        # add (first) text extension for code files
        if ext in self.code_extensions or txt2code == False:
            return infile + self.text_extensions[0]
        # give up
        return infile + ".out"



# Helper functions
# ----------------
# 
# open_streams
# ~~~~~~~~~~~~
# 
# Return file objects for in- and output. If the input path is missing,
# write usage and abort. (An alternative would be to use stdin as default.
# However,  this leaves the uninitiated user with a non-responding application
# if (s)he just tries the script without any arguments) ::

def open_streams(infile = '-', outfile = '-', overwrite='update', **keyw):
    """Open and return the input and output stream
    
    open_streams(infile, outfile) -> (in_stream, out_stream)
    
    in_stream   --  file(infile) or sys.stdin
    out_stream  --  file(outfile) or sys.stdout
    overwrite   --  ['yes', 'update', 'no']
                    if 'update', only open output file if it is older than
                    the input stream.
                    Irrelevant if outfile == '-'.
    """
    if not infile:
        strerror = "Missing input file name ('-' for stdin; -h for help)"
        raise IOError, (2, strerror, infile)
    if infile == '-':
        in_stream = sys.stdin
    else:
        in_stream = file(infile, 'r')
    if outfile == '-':
        out_stream = sys.stdout
    elif overwrite == 'no' and os.path.exists(outfile):
        raise IOError, (1, "Output file exists!", outfile)
    elif overwrite == 'update' and is_newer(outfile, infile):
        raise IOError, (1, "Output file is newer than input file!", outfile)
    else:
        out_stream = file(outfile, 'w')
    return (in_stream, out_stream)


def is_newer(path1, path2):
    """Check if `path1` is newer than `path2` (using mtime)
    
    Non-existing files are considered oldest
    """
    try:
        mtime1 = os.path.getmtime(path1)
    except OSError:
        return False
    try:
        mtime2 = os.path.getmtime(path2)
    except OSError:
        return True
    # print "mtime of path %d, mtime of self %d" % (mtime1, mtime2)
    return mtime1 > mtime2


# get_converter
# ~~~~~~~~~~~~~
# 
# Get an instance of the converter state machine::

def get_converter(data, txt2code=True, **keyw):
    if txt2code:
        return Text2Code(data, **keyw)
    else:
        return Code2Text(data, **keyw)


# Use cases
# ---------
# 
# run_doctest
# ~~~~~~~~~~~
# 
# ::

def run_doctest(infile="-", txt2code=True, 
                globs={}, verbose=False, optionflags=0, **keyw):
    """run doctest on the text source
    """
    from doctest import DocTestParser, DocTestRunner
    (data, out_stream) = open_streams(infile, "-")
    
# If source is code, convert to text, as tests in comments are not found by
# doctest::
    
    if txt2code is False: 
        converter = Code2Text(data, keep_lines=True, **keyw)
        docstring = str(converter)
    else: 
        docstring = data.read()
        
# Use the doctest Advanced API to do all doctests in a given string::
    
    test = DocTestParser().get_doctest(docstring, globs={}, name="", 
                                           filename=infile, lineno=0)
    runner = DocTestRunner(verbose=verbose, optionflags=optionflags)
    runner.run(test)
    runner.summarize
    if not runner.failures:
        print "%d failures in %d tests"%(runner.failures, runner.tries)
    return runner.failures, runner.tries


# diff
# ~~~~
# 
# ::

def diff(infile='-', outfile='-', txt2code=True, **keyw):
    """Report differences between converted infile and existing outfile
    
    If outfile is '-', do a round-trip conversion and report differences
    """
    
    import difflib
    
    instream = file(infile)
    # for diffing, we need a copy of the data as list::
    data = instream.readlines()
    # convert
    converter = get_converter(data, txt2code)
    new = str(converter).splitlines(True)
    
    if outfile != '-':
        outstream = file(outfile)
        old = outstream.readlines()
        oldname = outfile
        newname = "<conversion of %s>"%infile
    else:
        old = data
        oldname = infile
        # back-convert the output data
        converter = get_converter(new, not txt2code)
        new = str(converter).splitlines(True)
        newname = "<round-conversion of %s>"%infile
        
    # find and print the differences
    delta = list(difflib.unified_diff(old, new, fromfile=oldname, 
                                      tofile=newname))
    if not delta:
        print oldname
        print newname
        print "no differences found"
        return False
    print "".join(delta)
    return True
       
# main
# ----
# 
# If this script is called from the command line, the `main` function will
# convert the input (file or stdin) between text and code formats::

def main(args=sys.argv[1:], **default_values):
    """%prog [options] FILE [OUTFILE]
    
    Convert between reStructured Text with embedded code, and
    Source code with embedded text comment blocks"""

# Parse and complete the options::

    options = PylitOptions(args, **default_values).values

# Run doctests if ``--doctest`` option is set::

    if options.ensure_value("doctest", None):
        return run_doctest(**options.as_dict())

# Do a round-trip and report differences if the ``--diff`` opton is set::

    if options.ensure_value("diff", None):
        return diff(**options.as_dict())

# Open in- and output streams::

    try:
        (data, out_stream) = open_streams(**options.as_dict())
    except IOError, ex:
        print "IOError: %s %s" % (ex.filename, ex.strerror)
        sys.exit(ex.errno)

# Get a converter instance::

    converter = get_converter(data, **options.as_dict())
    
# Execute if the ``-execute`` option is set::

    if options.ensure_value("execute", None):
        print "executing " + options.infile
        if options.txt2code:
            code = str(converter)
        else:
            code = data
        exec code
        return

# Default action::

    out_stream.write(str(converter))
    if out_stream is not sys.stdout:
        print "extract written to", out_stream.name
        
# Rename the infile to a backup copy if ``--replace`` is set
# 
# ::

    if options.ensure_value("replace", None):
        os.rename(options.infile, options.infile + "~")

    return


if __name__ == '__main__':
    main()
 
