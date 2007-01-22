#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# =====================================================
# Literate programming with Python and reStructuredText
# =====================================================
# 
# :Version:   0.2
# :Date:      2006-12-06
# :Copyright: 2006 Guenter Milde.
#             Released under the terms of the GNU General Public License 
#             (v. 2 or later)
# :Changelog: 2005-06-29 Initial version
#             2005-06-30 first literate version of the script
#             2005-07-01 object orientated script using generators 
#             2005-07-10 Two state machine
#             2006-12-04 Start of work on version 0.2 (code restructuring)
# 
# 
# Motivation
# ============
# 
# Literate Programming
# --------------------
# 
# 
#    Literate programming is the combination of documentation and source
#    together in a fashion suited for reading by human beings.
#    
#    -- `Literate Programming FAQ`_
# 
# ..
# 
#    Let us change our traditional attitude to the construction of programs:
#    Instead of imagining that our main task is to instruct a computer what to
#    do, let us concentrate rather on explaining to humans what we want the
#    computer to do. 
#    
#    -- Donald E. Knuth, 1984
# 
# ..
#    
#    The idea is that you do not document programs (after the fact), but write
#    documents that contain the programs. 
#    
#    -- John Max Skaller in a `Charming Python`_ interview.
#    
# 
# Restrictions
# ------------
# 
# Literate programming environments of the WEB_ family failed to gain a strong
# user base. Some of the reasons are:
# 
# * The steep learning curve for mastering TeX, the special WEB commands and
#   the actual programming language in parallel discourages potential literate
#   programmers.
# 
# * While a printout has the professional look of a TeX-typeset essay, the
#   programmer will spend most time viewing and editing the source. A WEB
#   source in a text editor looks rather alienating:
#   
#     In Knuth's work, beautiful literate programs were woven from ugly mixes of
#     markups in combined program and documentation files. The literate program
#     was directly targeted towards paper and books. Of obvious reasons,
#     programmers do not very often print their programs on paper. (And as
#     argued above, few of us intend to publish our programs in a book). Within
#     hours, such a program print out is no longer up-to-date. And furthermore,
#     being based on a paper representation, we cannot use the computers dynamic
#     potentials, such as outlining and searching.
#        
#     -- Kurt Nørmark: `Literate Programming - Issues and Problems`_
# 
# 
# Nevertheless, the idea of "documents that contain a program" is still
# usefull in many contexts. This is the reason for one more attempt of a
# literate programming framework.
# 
# 
# PyLit
# =====
# 
# `PyLit` (Python-Literate) provides a plain but efficient tool for literate
# programming: a translator between a *text source* (reStructuredText_ with
# embedded code blocks) and a *code source* (source code with comment blocks).
# 
# It is written in Python but should work with any programming language that
# provides a syntax for comment blocks. ::

"""pylit: Literate programming with Python and reStructuredText
   Convert between 
   
   * reStructured Text with embedded code, and
   * Source code with embedded text comment blocks
"""

# The most distinct features are:
# 
# Dual source
# -----------
# 
# Text source and code source are considered equal. Both hold the full
# information. 
# 
# The `pylit.py` script converts the text source to code source and vice
# versa. Round-trips are possible without loss of information. (It is
# possible, to 'export' to a format by stripping code or text during the
# conversion using the ``--strip`` option)
# 
# Work on code or documentation can be done in adapted editor modes or
# environments providing formatting tools, syntax highlight, outlining,
# and other conveniences.
# 
# Debugging is straightforward, using the code source.
# 
# Simplicity
# ----------
# 
# `Pylit` does not introduce "named chunks". It lets the programmer
# intersperse documentation and code freely but does not provide code
# re-ordering or multiple expansion of definitions. Some call this
# *semi-literate* style.
# 
# This restriction was done deliberately. It reduces the complexity and seems
# better suited for a programming language like Python where you would rather
# use modules, classes, and functions to organise the code.
# 
#   The computer science and programming pioneers, like Wirth and Knuth, used
#   another programming style than we recommend today. One notable difference
#   is the use of procedure abstractions. When Wirth and Knuth wrote their
#   influential books and programming, procedure calls were used with care,
#   partly because they were relatively expensive. Consequently, they needed
#   an extra level of structuring within a program or procedure. 
#   'Programming by stepwise refinement' as well as 'literate programming' can
#   be seen as techniques and representations to remedy the problem. The use
#   of many small (procedure) abstractions goes in another direction. If you
#   have attempted to use 'literate programming' on a program (maybe an
#   object-oriented program) with lots of small abstractions, you will
#   probably have realized that there is a misfit between, on the one hand,
#   being forced to name literal program fragments (scraps) and on the other,
#   named program abstractions. We do not want to leave the impression that
#   this is a major conceptual problem, but it is the experience of the author
#   that we need a variation of literate programming, which is well-suited to
#   programs with many, small (named) abstractions.
#   
#   -- Kurt Nørmark: `Literate Programming - Issues and Problems`_
# 
# 
# reStructuredText
# ----------------
# 
# `PyLit` uses reStructuredText_ from Python docutils_ for text markup
# 
# * reStructuredText is an "ASCII-markup" language. Its syntax is very similar
#   to the usual conventions used to structure "ASCII text" like e.g. emails.
#   Thus it is more easy to read and to edit in a text editor than e.g. TeX,
#   HTML, or XML.
#   
#   Most of the time, a programmer will see the source in a "text editor".
#   With reStructuredText as documenting language, not only the pretty printed
#   documentation, but either version of the source is a "combination of
#   documentation and source together in a fashion suited for reading by human
#   beings."
#   
# * reStructuredText is well documented, and actively maintained.
#   
# * Special editor modes for editing reStructuredText already exist (see
#   `Editor Support for reStructuredText`_.) 
#   
# * With docutils_, the text source can be converted to a nice looking,
#   hyperlinked, browsable HTML documentation as well as to a printer-ready
#   PDF manual.
# 
# Actually, only the syntax for literal blocks is needed for pylit to convert
# from text to code. I.e. if no pretty-printed or web-ready document is
# needed, the programmer doesnot need to know anything else about
# reStructuredText.
# 
# ::

__docformat__ = 'restructuredtext'


# .. _`Literate Programming FAQ`: http://www.literateprogramming.com/lpfaq.pdf
# 
# .. _`Charming Python`: 
#      http://www-128.ibm.com/developerworks/library/l-pyth7.html
# 
# .. _WEB: http://www-cs-faculty.stanford.edu/~knuth/cweb.html
# 
# .. _`Literate Programming - Issues and Problems`:
#      http://www.cs.auc.dk/~normark/litpro/issues-and-problems.html
# 
# .. _docutils: http://docutils.sourceforge.net/rst.html
# 
# .. _reStructuredText: http://docutils.sourceforge.net/rst.html
# 
# .. _Editor Support for reStructuredText: 
#       http://docutils.sourceforge.net/tools/editors/README.html
# 
# 
# Implementation
# ==============
# 
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

# Previous versions imported from my iterqueue module::
# 
# from iterqueue import PushIterator            # iterator with backtracking
# 
# The PushIterator is a minimal implementation of an iterator with
# backtracking from the `Effective Python Programming`_ OSCON 2005 tutorial by
# Anthony Baxter As the definition is small, it is inlined now. For the full
# reasoning and doc see iterqueue.py.txt (unpublished)
class PushIterator:
    def __init__(self, iterable):
        self.it = iter(iterable)
        self.cache = []
    def __iter__(self):
        """Return `self`, as this is already an iterator"""
        return self
    def next(self):
        return (self.cache and self.cache.pop()) or self.it.next()
    def appendleft(self, value):
        self.cache.append(value)


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
# The generic `PyLitConverter` class inherits the state machine framework
# (initalisation, scheduler, iterator interface, ...) from `SimpleStates`,
# overrides the ``__init__`` method, and adds auxiliary methods and
# configuration attributes (options). 
# 
# ::

class PyLitConverter(SimpleStates):
    """parent class for Text2Code and Code2Text, the state machines
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
    join = "".join    # join lists to a string (by default with empty string)

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
        self.__textindent = 0

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
# Ensure blank line at end of a block ::

    def ensure_trailing_blank_line(self, lines, line):
        if self.strip:
            return
        if lines and lines[-1].lstrip(): 
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
# Convert the comment string of the header (shebang and coding lines). The
# first a non-matching and non-blank line  will trigger the switch to 'text'
# state. ::

    def header(self):
        """Uncomment python header lines"""
        lines = []
        line = ""
        # Test first lines for special python header comments
        for line in self.data_iterator:
            # pass on blank lines
            if not line.lstrip():
                lines.append(line)  
            # strip rst-comment from special python header lines
            elif line.startswith(".. #!"):
                lines.append(line[len(".. "):])
            elif (line.startswith(".. " + self.comment_string)
                  and line.find("coding:") != -1):
                lines.append(line[len(".. "):])
            # everything else is the first non-header line
            else:
                break
        # Push back first non-header line and set state to "text"
        self.data_iterator.appendleft(line)
        self.state = "text"
        self.ensure_trailing_blank_line(lines, line)
        return self.join(lines)

# Text2Code.text_handler_generator
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# The 'text' handler processes everything that is not an indented literal
# comment. Text is quoted with the comment_string or filtered (with
# strip=True). 
# 
# ::

    def text_handler_generator(self):
        """Convert text blocks from rst to comment
        """
        lines = []
        for line in self.data_iterator:
            # print "Text: '%s'"%line
            # default action: add comment string
            if not self.strip:
                lines.append(self.comment_string + line)
            # End of text block: 
            if (line.rstrip().endswith("::")
                and not line.lstrip().startswith("..")):
                # set the current text indent level 
                # (needed by the code handler to find the end of code block)
                self.__textindent = self.get_indent(line)
                self.state = 'code'
                # ensure trailing blank line
                line = self.data_iterator.next()
                if line.lstrip():
                    self.data_iterator.appendleft(line) # push back
                    self.ensure_trailing_blank_line(lines, line)
                elif not self.strip:
                    lines.append(line)
                # remove_literal_marker(lines)
                yield self.join(lines)
                lines = []
                continue
        # End of data
        yield self.join(lines)


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
# the  data_iterator must support the `.appendleft()` method. (This is the
# reason for the use of the PushIterator class in `__init__`.) ::

    def code_handler_generator(self):
        """Convert indented literal blocks to source code
        """
        lines = []
        codeindent = "indent of first non-blank code line" # set below
        for line in self.data_iterator:
            # print "Code: '%s'"%line
            # pass on blank lines (no whitespace except newline)
            if not line.rstrip("\n"):
                lines.append(line)
                continue                    
            # literal block ends with first less indented, nonblank line
            # self.__textindent is set by the text handler to the indent of
            # the surrounding text block
            if line.lstrip() and self.get_indent(line) <= self.__textindent:
                self.data_iterator.appendleft(line) # push back
                self.state = 'text'
                self.ensure_trailing_blank_line(lines, line)
                yield self.join(lines)
                lines = []
                continue
            # default action: append unindented line
            # just in case the line is shorter than codeindent but not totally
            # empty, append only a newline.
            try:
                lines.append(line[codeindent:] or "\n")
            except TypeError:
                # Determine the code indentation:
                if not line.lstrip(): # pass on "white" lines
                    lines.append(line)
                    continue
                codeindent = self.get_indent(line)
                lines.append(line[codeindent:] or "\n")
        yield self.join(lines)
                        

# Txt2Code.remove_literal_marker
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# Remove literal marker (::) in expanded form i.e. in a paragraph on its own.
# 
# While cleaning up the code source, it leads to confusion for doctest and
# searches (e.g. grep) as line-numbers between text and code source will differ.
# ::

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
# Only comments starting at the first column and with a comment string
# matching the one in the `comment_string` attribute are treated as text
# blocks.
# 
# The class is derived from the PyLitConverter state machine and adds handlers
# for the three states "header", "text", and "code". ::

class Code2Text(PyLitConverter):
    """Convert code source to text source
    """

# Code2Text.header
# ~~~~~~~~~~~~~~~~
# 
# Convert the header (shebang and coding lines) to a reStructured text
# comment. Set the state to "text" afterwards (as we expect a leading comment
# block to be the common case). ::

    def header(self):
        """Comment header lines"""
        lines = []
        for line in self.data_iterator:
            # pass on blank lines
            if not line.lstrip():
                lines.append(line)
                continue
            if (line.startswith("#!") 
                or (line.startswith(self.comment_string)
                    and line.find("coding:") != -1)):
                lines.append(".. " + line)
            else:
                break
        self.data_iterator.appendleft(line)
        self.state = "text"
        self.ensure_trailing_blank_line(lines, line)
        if self.strip:
            return ""
        return self.join(lines)

# Code2Text.text_handler_generator
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# The text handler processes 
# 
# * non-indented comment blocks 
# * with matching comment string,
# * that are separated from code by a blank line (the paragraph separator in
#   reStructuredText)
# 
# Text is uncommented. A literal block marker is appended, if not already
# present. ::

    def text_handler_generator(self):
        """Uncomment text blocks in source code
        """
        prefix = " "*self.codeindent + self.comment_string
        lines = [""]
        for line in self.data_iterator:
            # print "Text: " + line
            # pass on blank lines
            if not line.lstrip():
                lines.append(line)
                continue
            # strip comment chars from empty lines
            if line.rstrip() == self.comment_string.rstrip():
                lines.append("\n")
                continue
            # End of text block
            if not line.startswith(self.comment_string):
                self.data_iterator.appendleft(line)
                self.state = 'code'
                # keep as comment if there is no trailing blank line
                if lines and lines[-1].lstrip():
                    lines = [prefix + line for line in lines]
                    # add text block marker before first code block
                    if lines[0] == prefix and not self.keep_lines:
                        lines[0] = "::\n\n"
                    yield self.join(lines)
                else:
                    # Ensure literal block marker
                    if (not self.strip and len(lines)>1 
                        and not lines[-2].rstrip().endswith("::")):
                        lines.append("::\n\n")
                    yield self.join(lines)
                lines = []
                continue
            # default action: strip the comment string
            lines.append(line[len(self.comment_string):])
        yield self.join(lines)

    
# Code2Text.code_handler_generator
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# The `code` method is called on non-commented code. Code is returned as
# indented literal block or filtered (with ``strip=True``). The amount of the
# code indentation is controled by `self.codeindent`. To prevent problems with
# different tabulator settings, hard tabs in code lines  are expanded with the
# `expandtabs` string method when calculating the indentation.
# 
# ::

    def code_handler_generator(self):
        """Convert source code to indented literal blocks.
        
        Expands hard tabs with the `expandtabs` string method.
        Strips the code blocks if self.strip is True
        """
        lines = []
        for line in self.data_iterator:
            # yield "Code: " + line
            # pass on empty lines (only newline)
            if not line.rstrip("\n"):
                lines.append(line)
                continue
            # strip comment chars from empty lines
            if line.rstrip() == self.comment_string.rstrip():
                lines.append("\n")
                continue
            # test for end of code block 
            # (nonindented matching comment string following a blank line)
            if (line.startswith(self.comment_string) 
                and lines and not lines[-1].strip()):
                self.data_iterator.appendleft(line)
                self.state = 'text'
                # self.ensure_trailing_blank_line(lines, line)
                if self.strip:
                    yield ""
                else:
                    yield self.join(lines)
                # reset
                lines = []
                continue
            # default action: indent
            lines.append(" "*self.codeindent + line)
        # no more lines in data_iterator
        if self.strip:
            yield ""
        else:
            yield self.join(lines)
        
                

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
        docstring = "".join(converter())
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
    """Do a round-trip and report differences
    """
    import difflib
    
    data = file(infile)
    # for diffing, we need a copy of the data as list::
    data = data.readlines()
    # convert
    converter = get_converter(data, txt2code)
    output = "".join(converter()).splitlines(True)
    # back-convert the output data
    converter = get_converter(output, not txt2code)
    output = "".join(converter()).splitlines(True)
    # find and print the differences
    delta = list(difflib.unified_diff(data, output, infile,
                                      "result of pylit round-cycle"))
    if not delta:
        print "no differences found in result of pylit round-cycle"
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
            code = "".join(converter())
        else:
            code = data
        exec code
        return

# Default action::

    output = "".join(converter())
    out_stream.write(output)
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


# Alternatives
# ============
# 
# There are already a lot of literate programming frameworks available, both
# sophisticated and lightwight. This non-comprehensive listing will compare
# them to `PyLit`.
# 
# WEB and friends
# ---------------
# 
# The first published literate programming environment was WEB, introduced by
# Donald Knuth in 1981 for his TeX typesetting system; it uses Pascal as its
# underlying programming language and TeX for typesetting of the
# documentation. CWEB_ is a newer version of WEB for the C programming
# language.
# 
# Other implementations of the concept are noweb_ and FunnelWeb_.
# 
# Just compare hello.noweb::

# | @
# | \section{Hello world}
# | 
# | Today I awakened and decided to write
# | some code, so I started to write a Hello World in \textsf C.
# | 
# | <<hello.c>>=
# | /*
# |   <<license>>
# | */
# | #include <stdio.h>
# | 
# | int main(int argc, char *argv[]) {
# |   printf("Hello World!\n");
# |   return 0;
# | }
# | @
# | \noindent \ldots then I did the same in PHP.
# | 
# | <<hello.php>>=
# | <?php
# |   /*
# |   <<license>>
# |   */
# |   echo "Hello world!\n";
# | ?>
# | @
# | \section{License}
# | Later, same day some lawyer reminded me about licenses.
# | So, here it is:
# | 
# | <<license>>=
# | This work is placed in the public domain.
# | @
# 
# to the Pylit Version (in 3 files)
# 
# hello.c.txt::

# | Hello world
# | -----------
# | 
# | Today I awakened and decided to write
# | some code, so I started to write a Hello World in `C`.
# | 
# | ..include: license
# | 
# | :: 

# | 
# | #include <stdio.h>
# | 
# | int main(int argc, char *argv[]) {
# |   printf("Hello World!\n");
# |   return 0;
# | }
# 
# hello.php.txt::

# | ... then I did the same in PHP.
# |
# | ..include: license
# | 
# | :: 

# | 
# | <?php
# |   /*
# |   <<license>>
# |   */
# |   echo "Hello world!\n";
# | ?>
# 
# Later, same day some lawyer reminded me about licenses.
# So, here it is:
# 
# license::

# | This work is placed in the public domain.
# 
# .. _noweb: http://www.eecs.harvard.edu/~nr/noweb/
# 
# .. _FunnelWeb: http://www.ross.net/funnelweb/
# 
# XMLTangle
# ---------
# 
# XMLTangle_ is an generic tangle  program written in Python. It differs from
# PyLit mainly by its choice of XML as documenting language (making the source
# document harder to read for a human being).
# 
#   This program is a version of the tangle program which has the following
#   features:
#   
#   * Works with any programming language
#   * Uses XML as the documentation language
#   * Is not tied to any specific DTD - instead it relies on processing
#     instructions to perform it's tasks
#   
#   It does not include every feature of literate programming - specifically it
#   does not include any macro facility.
# 
#   -- http://literatexml.sourceforge.net/xmltangle/t1.html
#   
# .. _XMLTangle: http://literatexml.sourceforge.net/xmltangle/
# 
# 
# Lightweight literate programming
# --------------------------------
# 
# `Lightweight literate programming`_ is one more example of a Python based
# literal programming framework. One XML source processed to either text or
# code. The XML source itself is rather hard to read for human beeings.
# 
#   In the author's current toolchain, the input is written in a slightly
#   customized dialect of DocBook. Automated tools produce the two primary
#   forms of output:
# 
#   * The ordinary DocBook toolchain processes the source file as a document,
#     producing both Web and PDF formats. For details of this toolchain, see
#     `Writing documentation with Docbook-XML 4.2`_.
#   
#   * A small Python script extracts one or more source files from the
#     document, and these are the executable form of the program. 
# 
# .. _`Lightweight literate programming`: 
#    http://infohost.nmt.edu/~shipman/soft/litprog/
#    
# .. _`Writing documentation with Docbook-XML 4.2`:   
#    http://www.nmt.edu/tcc/help/pubs/docbook42/
#    
# SourceBrowser
# -------------
# 
#   SourceBrowser_ is a documentation meta-programming tool that generates a
#   wiki representation of a source tree. 
# 
#   It provides a `Source Annotation Language` for writing a documentation
#   meta-program and a tool for generating a static wiki for the host program.
# 
# It is a rather complex tool aimed at a hyperlinked representation of complex
# programming projects.
# 
# .. _SourceBrowser: http://web.media.mit.edu/~vyzo/srcb/doc/index.html
# 
# 
# Interscript
# -----------
# 
# PyLit it a simple literal programming framework...
# 
#   Interscript_ is different, because the fundamental paradigm is extended so
#   that there are three kinds of LP sections in file:
# 
#    1. Code sections
#    2. Documentation sections
#    3. Scripting sections
#    
#    -- Interscript_ homepage
#    
# .. _Interscript: http://interscript.sourceforge.net/
# 
# Ly
# --
# 
# Ly_, the "lyterate programming thingy." is an engine for Literate Programming.
# The design consideration look very much like the ones for Pylit:
# 
#   So why would anybody use Ly instead of the established Literate
#   Programming tools like WEB or noweb? 
# 
#     * Elegance. I do not consider the source code of WEB or noweb to be
#       particularly nice. I especially wanted a syntax that allows me to easily
#       write a short paragraph, then two or three lines of code, then another
#       short paragraph. Ly accomplishes this by distinguishing code from text
#       through indentation.
#     * HTML. WEB and CWEB are targeted at outputting TeX. This is a valid
#       choice, but not mine, as I want to create documents with WWW links, and
#       as I want to re-create documents each time I change something-- both of
#       these features don't go well together with a format suited to printout,
#       like TeX is. (Of course you can create HTML from LaTeX, but if my output
#       format is HTML, I want to be able to write HTML directly.)
#     * Python. I originally created Ly for a Python-based project, and
#       therefore I wanted it to run everywhere where Python runs. WEB and noweb
#       are mostly targeted at UNIX-like platforms. 
# 
# Ly introduces its own language with a syntax for code chunks instead of the
# simpler "semi literate" style of pylit. "Ly has some special ways for
# entering HTML tags. However, they are currently undocumented."
# 
# .. _Ly: http://lyterate.sourceforge.net/intro.html
# 
# pyreport
# --------
# 
# Pyreport is quite similar to PyLit in its focus on Python and the use of
# reStructuredText. It is a combination of `documentation generator`__
# (processing embedded documentation) and report tool (processing Python
# output). It is not suited to "write documents that contain the programs".
# 
# __ http://en.wikipedia.org/wiki/Documentation_generator
# 
#   pyreport is a program that runs a python script and captures its output,
#   compiling it to a pretty report in a pdf or an html file. It can display
#   the output embedded in the code that produced it and can process special
#   comments (literate comments) according to markup languages (rst or LaTeX)
#   to compile a very readable document.
#   
#   This allows for extensive literate progamming in python, for generating
#   reports out of calculations written in python, and for making nice
#   tutorials.
# 
# 
# 
# 
# 
# Open questions
# ==============
# 
# * How to handle docstrings in code blocks? (it would be nice to convert them
#   to rst-text if the ``__docformat__`` is ``restructuredtext``)
#   
# * road testing
# 
# * publication and advertisement
# 
# * How can I include a literal block that should not be in the
#   executable code (e.g. an example, an earlier version or variant)?
#   
#   Workaround: Use a `quoted literal block` (with a quotation different from
#               the comment string used for text blocks to keep it as
#               commented over the code-text round-trips.
#           
#               Python `pydoc` examples can also use the special pydoc block
#               syntax (no double colon!).
#   
# .. contents::
# 
#   
