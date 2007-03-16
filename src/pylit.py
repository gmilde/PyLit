#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# ===============================================================
# pylit.py: Literate programming with Python and reStructuredText
# ===============================================================
# 
# :Date:      $Date: 2007-03-06$
# :Version:   SVN-Revision $Revision$
# :URL:       $URL$
# :Copyright: 2005, 2007 Guenter Milde.
#             Released under the terms of the GNU General Public License 
#             (v. 2 or later)
# 
# .. sectnum::
# .. contents::

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
# :2007-01-23: 0.2   published at http://pylit.berlios.de
# :2007-01-25: 0.2.1 Outsourced non-core documentation to the PyLit pages.
# :2007-01-26: 0.2.2 new behaviour of `diff` function
# :2007-01-29: 0.2.3 new `header` methods after suggestion by Riccardo Murri
# :2007-01-31: 0.2.4 raise Error if code indent is too small
# :2007-02-05: 0.2.5 new command line option --comment-string
# :2007-02-09: 0.2.6 add section with open questions,
#                    Code2Text: let only blank lines (no comment str)
#                    separate text and code,
#                    fix `Code2Text.header`
# :2007-02-19: 0.2.7 simplify `Code2Text.header,`
#                    new `iter_strip` method replacing a lot of ``if``-s
# :2007-02-22: 0.2.8 set `mtime` of outfile to the one of infile
# :2007-02-27: 0.3   new `Code2Text` converter after an idea by Riccardo Murri
#                    explicite `option_defaults` dict for easier customization
# :2007-03-02: 0.3.1 expand hard-tabs to prevent errors in indentation,
#                    `Text2Code` now also works on blocks,
#                    removed dependency on SimpleStates module
# :2007-03-06: 0.3.2 bugfix: do not set `language` in `option_defaults`
#                    renamed `code_languages` to `languages`
# 
# ::

"""pylit: Literate programming with Python and reStructuredText
   
   PyLit is a bidirectional converter between
   
   * a (reStructured) text source with embedded code, and
   * a code source with embedded text blocks (comments)
"""

__docformat__ = 'restructuredtext'

_version = "0.3"


# Requirements
# ------------
# 
# * library modules
# 
# ::

import re
import os
import sys
import optparse

# Customization
# =============
# 
# defaults
# --------
# 
# Collect option defaults in an `defaults` object. This gives an central
# point for the used defaults and their customization.
# It also facilitates the setting of options in programmatic use ::

defaults = optparse.Values()

# Languages and language specific defaults::

# The language is set from file extensions (if not given as command line
# option). Setting it in `defaults` would override this auto-setting
# feature.::

defaults.languages  = {".py": "python", 
                       ".sl": "slang", 
                       ".c": "c++",
                       ".css": "css",
                       ".el":"elisp"}

defaults.code_extensions = defaults.languages.keys()
defaults.text_extensions = [".txt"]

# The fallback is our favourite language::

defaults.default_language = "python"

defaults.comment_strings = {"python": '# ',
                            "slang":  '% ', 
                            "c++":    '// ',
                            "css":    '// ',
                            "elisp":  ';; '}  

# Marker string for the first code block. (Should be a valid rst directive
# that accepts code on the same line, e.g. ``'.. admonition::'``.)  No
# trailing whitespace needed as indented code follows. Default is a comment
# marker::
  
defaults.header_string = '..'

# Export to the output format stripping text or code blocks::

defaults.strip = False
      
# Number of spaces to indent code blocks in the code -> text conversion. [#]_
# ::

defaults.codeindent =  2

# .. [#] For the text -> code conversion, the codeindent is determined by the
#        first recognized code line (leading comment or first indented literal
#        block of the text source).
# 
#   
#  
# Classes
# =======
# 
# Converter
# ---------
# 
# The converters are implemented as classes derived from a `Converter`
# parent class: `Text2Code`_ converts a text source to executable code, while
# `Code2Text`_ does the opposite: converting commented code to a text source.
# 
# ::

class PyLitConverter(object):
    """parent class for `Text2Code` and `Code2Text`, the state machines
    converting between text source and code source of a literal program.
    """

# The converter classes implement a simple state machine to separate and
# transform documentation and code blocks. For this task, only a very limited
# parsing is needed. PyLit's parser assumes:
# 
# * indented literal blocks in a text source are code blocks.
#   (TODO: allow other directives for source code)
# 
# * comment lines that start with a matching comment string in a code source
#   are documentation blocks.
# 
# .. _docutils: http://docutils.sourceforge.net/
#   
# Data attributes
# ~~~~~~~~~~~~~~~
# 
# The data attributes are class default values. They are fetched from the
# `defaults`_ dictionary and can be overridden by matching keyword
# arguments during class instantiation. Keyword arguments to `get_converter`_
# and `main`_ can be used to customize the converter, as they are passed on to
# the instantiation of a converter class. ::

    language = defaults.default_language
    comment_strings = defaults.comment_strings
    comment_string = None # set in __init__
    codeindent =  defaults.codeindent
    header_string = defaults.header_string
    strip = defaults.strip

# Initial state (do not overwrite)::

    state = 'header' 


# Converter.__init__
# ~~~~~~~~~~~~~~~~~~
# 
# Initializing sets up the `data` attribute, an iterable object yielding lines
# of the source to convert. [1]_ Additional keyword arguments are stored as
# data attributes, overwriting the class defaults. If not given as keyword
# argument, `comment_string` is set to the language's default comment
# string::

    def __init__(self, data, **keyw):
        """data   --  iterable data object 
                      (list, file, generator, string, ...)
           **keyw --  remaining keyword arguments are 
                      stored as data-attributes 
        """
        self.data = data
        self.__dict__.update(keyw)
        if not self.comment_string:
            self.comment_string = self.comment_strings[self.language]
            
# .. [1] The most common choice of data is a `file` object with the text
#        or code source.
# 
#        To convert a string into a suitable object, use its splitlines method
#        with the optional `keepends` argument set to True.
# 
# 
# Converter.__call__
# ~~~~~~~~~~~~~~~~~~
# 
# The special `__call__` method allows the use of class instances as callable
# objects. It returns the converted data as list::

    def __call__(self):
        """Iterate over state-machine and return results as a list"""
        return [token for token in self]

# TODO: return a list of lines?
# 
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
# Return the number of leading spaces in `line` after expanding tabs ::

    def get_indent(self, line):
        """Return the indentation of `string`.
        """
        # line = line.expandtabs() # now done in `collect_blocks`
        return len(line) - len(line.lstrip())

# Converter.ensure_trailing_blank_line
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# Ensure there is a blank line as last element of the list `lines`.
# (currently not used)::

    def ensure_trailing_blank_line(self, lines, next_line):
        if not lines:
            return
        if lines[-1].lstrip(): 
            sys.stderr.write("\nWarning: inserted blank line between\n %s %s"
                             %(lines[-1], next_line))
            lines.append("\n")


# Converter.collect_blocks
# ~~~~~~~~~~~~~~~~~~~~~~~~
# 
# A generator function to aggregate "paragraphs" (blocks separated by blank
# lines).::

    def collect_blocks(self): 
        """collect lines in a list 
        
        yield list for each block of lines (paragraph) seperated by a 
        blank line (whitespace only).
        
        Also expand hard-tabs as these will lead to errors in indentation.
        """
        block = []
        for line in self.data:
            block.append(line.expandtabs())
            if not line.rstrip():
                yield block
                block = []
        yield block
                

# Text2Code
# ---------
# 
# The `Text2Code` class separates code blocks (indented literal blocks) from
# documentation. Code blocks are unindented, documentation is commented (or
# filtered, if the ``strip`` option is True.
# 
# Only `indented literal blocks` are extracted. `quoted literal blocks` and
# `pydoc blocks` are treated as text. This allows the easy inclusion of
# examples: [#]_
# 
#    >>> 23 + 3
#    26
# 
# .. [#] Mark that there is no double colon before the doctest block in
#        the text source.
# 
# Using the full blown docutils_ rst parser would introduce a large overhead
# and slow down the conversion.
# ::

class Text2Code(PyLitConverter):
    """Convert a (reStructured) text source to code source
    """

# Text2Code.__iter__
# ~~~~~~~~~~~~~~~~~~
# 
# Data is collected into "blocks" separated by blank lines. The state is set
# by the `set_state` method based on markers or indentation in the block.
# ::

    def __iter__(self):
        """Iterate over text source and return lists of code-source lines"""

# The indent of first non-blank code line, set in `Text2Code.code`::

        self._codeindent = None  

# Text indent level (needed by the code handler to find the
# end of code block)::

        self._textindent = 0

# The "code" to "text" state transition is detected in the  first non-code
# block. `header_test` will set `set_state` to `code_test` which checks the
# indentation.
# 
# The "text" to "code" state transition is codified in the preceding "text"
# block. This is why the "end-of-text" test is performed inside the `text`
# state handler.
# ::

        for block in self.collect_blocks():
            if self.state != "text":
                self.state = self.set_state(block)
            yield getattr(self, self.state)(block)
            


# Text2Code.set_state
# ~~~~~~~~~~~~~~~~~~~~~
# 
# At start, the check for "text" or "code" needs to check for the 
# `header_string`. After testing the "header" block, test for code-blocks with
# `Code2Text.code_test`_::

    def set_state(self, lines):
        """Return whether the header block is "text" or "code".
        
        Strip `self.header_string` if present."""
        
  
        self.set_state = self.code_test
        
        if lines[0].startswith(self.header_string):
            lines[0] = lines[0].replace(self.header_string, "", 1)
            return "code"
        return "text"


# Code2Text.code_test
# ~~~~~~~~~~~~~~~~~~~
# 
# Test for end of code block, return next state. 
# 
# A literal block ends with the first less indented, nonblank line.
# `_textindent` is set by the text handler to the indent of the
# preceding paragraph. 
# 
# ::

    def code_test(self, block):
        """test code block for end of "code" state, return next state
        """
        indents = [self.get_indent(line) for line in block]
        if min(indents) <= self._textindent:
            return 'text'
        return 'code'

# TODO: insert blank line before the first line with too-small codeindent?
# self.ensure_trailing_blank_line(lines, line)
# 
# 
# Text2Code.text
# ~~~~~~~~~~~~~~
# 
# The 'text' handler processes everything that is not an indented literal
# comment. Text is quoted with `self.comment_string` or filtered (with
# strip=True). ::

    def text(self, lines):
        """Convert text blocks from rst to comment
        """
        
        lines = [self.comment_string + line for line in lines]
                
# Test for the end of the text block: does the second last line end with
# `::` but is neither a comment nor a directive?
# If end-of-text marker is detected, 
# 
# * set state to 'code'
# * set the current text indent level (needed by the code handler to find the
#   end of code block)
# * remove the comment from the last line again (it's a separator between text
#   and code blocks).
# 
# TODO: allow different code marking directives (for syntax color etc)
# ::

        try:
            line = lines[-2]
        except IndexError:  # len(lines < 2)
            pass
        else:
            if (line.rstrip().endswith("::") 
                and not line.lstrip().startswith("..")):
                self.state = "code"
                self._textindent = self.get_indent(line)
                lines[-1] = lines[-1].replace(self.comment_string, "", 1)

        if self.strip:
            return []
        return lines
    
# TODO: Ensure a trailing blank line? Would need to test all
# text lines for end-of-text marker and add a line by calling the
# `ensure_trailing_blank_line` method (which also issues a warning)
# 
# 
# Text2Code.code
# ~~~~~~~~~~~~~~
# 
# The `code` handler is called with an indented literal block. It removes
# leading whitespace up to the indentation of the first code line in the file
# (this deviation from docutils behaviour allows indented blocks of Python
# code). ::

    def code(self, block): 
        """Convert indented literal blocks to source code
        """
        
# If still unset, determine the code indentation from first non-blank code
# line::

        if self._codeindent is None:
            self._codeindent = self.get_indent(block[0])

# Check if we can safely unindent the code block. There must not be lines less
# indented then `_codeindent` otherwise something got wrong. ::

        for line in block:
            if line.lstrip() and self.get_indent(line) < self._codeindent:
                raise ValueError, "code block contains line less indented " \
                                "than %d spaces \n%r"%(self._codeindent, block)

# return unindented block::

        return [line.replace(" "*self._codeindent, "", 1) for line in block]


# Txt2Code.remove_literal_marker
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# Remove literal marker (::) in "expanded form" i.e. in a paragraph on its own.
# 
# While cleaning up the code source, it leads to confusion for doctest and
# searches (e.g. grep) as line-numbers between text and code source will
# differ. 
# The code is left here, as it can be used for conversion of
# a literal marker to a different code-marker::

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
# The class is derived from the PyLitConverter state machine and adds  an
# `__iter__` method as well as handlers for "text", and "code" states. ::

class Code2Text(PyLitConverter):
    """Convert code source to text source
    """

# Code2Text.__iter__
# ~~~~~~~~~~~~~~~~~~
# 
# ::

    def __iter__(self):

# If the last text block doesnot end with a code marker (by default, the
# literal-block marker ``::``), the `text` method will set `code marker` to
# a paragraph that will start the next code block. It is yielded if non-empty
# at a text-code transition. If there is no preceding text block, `code_marker`
# contains the  `header_string`::

        if self.strip:
            self.code_marker = []
        else:
            self.code_marker = [self.header_string]
        
        for block in self.collect_blocks():
            
# Test the state of the block with `Code2Text.block_is_text`_, return it
# processed with the matching handler::

            if self.block_is_text(block):
                self.state = "text"
            else:
                if self.state != "code" and self.code_marker:
                    yield self.code_marker
                self.state = "code"
            yield getattr(self, self.state)(block)

# "header" state
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
# literal block (this would require the ``::`` and an empty line above the code).
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
# the source is a literate document anyway.
# 
# If needed for the documentation, it is possible to repeat the header in (or
# after) the first text block, e.g. with a `line block` in a `block quote`:
# 
#   |  ``#!/usr/bin/env python``
#   |  ``# -*- coding: iso-8859-1 -*-``
# 
# The current implementation represents the header state by the setting of
# `code_marker` to ``[self.header_string]``. The first non-empty text block
# will overwrite this setting.
# 
# Code2Text.text
# ~~~~~~~~~~~~~~
# 
# The *text state handler* converts a comment to a text block by stripping
# the leading `comment string` from every line::

    def text(self, lines):
        """Uncomment text blocks in source code
        """
        
        lines = [line.replace(self.comment_string, "", 1) for line in lines]

        lines = [re.sub("^"+self.comment_string.rstrip(), "", line)
                 for line in lines]

# If the code block is stripped, the literal marker would lead to an error
# when the text is converted with docutils. Replace it with
# `Code2Text.strip_literal_marker`_::
          
        if self.strip:
            self.strip_literal_marker(lines)
            self.code_marker = []

# Check for code block marker (double colon) at the end of the text block
# Update the `code_marker` argument. (The `code marker` is yielded by
# `Code2Text.__iter__`_ at a text -> code transition if it is not empty)::

        elif len(lines)>1:
            if lines[-2].rstrip().endswith("::"):
                self.code_marker = []
            else:
                self.code_marker = ["::\n", "\n"]

# Return the text block to the calling function::

        return lines
                     

# Code2Text.code
# ~~~~~~~~~~~~~~
# 
# The `code` method is called on non-commented code. Code is returned as
# indented literal block (or filtered, if ``self.strip == True``). The amount
# of the code indentation is controled by `self.codeindent` (default 2). 
# ::

    def code(self, lines):
        """Indent lines or strip if `strip` == `True`
        """
        if self.strip == True:
            return []

        return [" "*self.codeindent + line for line in lines]

# Code2Text.block_is_text
# ~~~~~~~~~~~~~~~~~~~~~~~
# 
# A paragraph is a text block, if every non-blank line starts with a matching
# comment string  (test includes whitespace except for commented blank lines!)
# ::

    def block_is_text(self, block):
        for line in block:
            if (line.rstrip() 
                and not line.startswith(self.comment_string)
                and line.rstrip() != self.comment_string.rstrip()):
                return False
        return True
  
# Code2Text.strip_literal_marker
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# Replace the literal marker with the equivalent of docutils replace rules
# 
# * strip `::`-line (and preceding blank line) if on a line on its own
# * strip `::` if it is preceded by whitespace. 
# * convert `::` to a single colon if preceded by text
# 
# `lines` should be list of text lines (with a trailing blank line). 
# It is modified in-place::

    def strip_literal_marker(self, lines):
        try:
            line = lines[-2]
        except IndexError:  # len(lines < 2)
            return
        
        # split at rightmost '::'
        try:
            (head, tail) = line.rsplit('::', 1)
        except ValueError:  # only one part (no '::')
            return
        
        # '::' on an extra line
        if not head.strip():            
            del(lines[-2])
            # delete preceding line if it is blank
            if len(lines) >= 2 and not lines[-2].lstrip():
                del(lines[-2])
        # '::' follows whitespace                
        elif head.rstrip() < head:      
            head = head.rstrip()
            lines[-2] = "".join((head, tail))
        # '::' follows text        
        else:
            lines[-2] = ":".join((head, tail))



# Command line use
# ================
# 
# Using this script from the command line will convert a file according to its
# extension. This default can be overridden by a couple of options.
# 
# Dual source handling
# --------------------
# 
# How to determine which source is up-to-date?
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# - set modification date of `oufile` to the one of `infile` 
# 
#   Points out that the source files are 'synchronized'. 
#   
#   * Are there problems to expect from "backdating" a file? Which?
# 
#     Looking at http://www.unix.com/showthread.php?t=20526, it seems
#     perfectly legal to set `mtime` (while leaving `ctime`) as `mtime` is a
#     description of the "actuality" of the data in the file.
# 
#   * Should this become a default or an option?
# 
# - alternatively move input file to a backup copy (with option: `--replace`)
#   
# - check modification date before overwriting 
#   (with option: `--overwrite=update`)
#   
# - check modification date before editing (implemented as `Jed editor`_
#   function `pylit_check()` in `pylit.sl`_)
# 
# .. _Jed editor: http://www.jedsoft.org/jed/
# .. _pylit.sl: http://jedmodes.sourceforge.net/mode/pylit/
# 
# Recognised Filename Extensions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
# the conversion to executable code. i.e. for a Python program foo:
# 
# * the code source is called ``foo.py``
# * the text source is called ``foo.py.txt``
# * the html rendering is called ``foo.py.html``
# 
# OptionValues
# ------------
# 
# For use as keyword arguments, it is handy to have the options
# in a dictionary. The following class adds an `as_dict` method to
# `optparse.Values` that returns all data arguments that are not in the class
# definition (thus filtering class methods and arguments) and not None::

class OptionValues(optparse.Values):
    def as_dict(self):
        """Return options as dictionary object"""
        non_values = dir(OptionValues)
        return dict([(option, getattr(self, option)) for option in dir(self)
                     if option not in non_values and option is not None])

# Defining `__getattr__` lets us replace calls like
# ``options.ensure_value("key", None)`` with the more concise
# ``options.key``.
#
# The Python Reference Manual says:
#
#   Called when an attribute lookup has not found the attribute in the usual
#   places (i.e. it is not an instance attribute nor is it found in the class
#   tree for self). name is the attribute name. This method should return the
#   (computed) attribute value or raise an AttributeError exception.

    def __getattr__(self, name): 
        """Return default value for non existing options"""
        return None

# PylitOptions
# ------------
# 
# Options are stored in the values attribute of the `PylitOptions` class.
# It is initialized with default values and parsed command line options (and
# arguments)  This scheme allows easy customization by code importing the
 # `pylit` module. ::

class PylitOptions(object):
    """Storage and handling of program options
    """

# Instantiation       
# ~~~~~~~~~~~~~
# 
# Instantiation sets up an OptionParser and initializes it with pylit's
# command line options and default values. ::

    def __init__(self, args=sys.argv[1:], **keyw):
        """Set up an `OptionParser` instance for pylit command line options
        """
        p = optparse.OptionParser(usage=main.__doc__, version=_version)
        # add the options
        p.add_option("-c", "--code2txt", dest="txt2code", action="store_false",
                     help="convert code to reStructured text")
        p.add_option("--comment-string", dest="comment_string",
                     help="text block marker (default '# ' (for python))" )
        p.add_option("-d", "--diff", action="store_true", 
                     help="test for differences to existing file")
        p.add_option("--doctest", action="store_true",
                     help="run doctest.testfile() on the text version")
        p.add_option("-e", "--execute", action="store_true",
                     help="execute code (Python only)")
        p.add_option("-f", "--infile",
                     help="input file name ('-' for stdout)" )
        p.add_option("--language", action="store", 
                     choices = defaults.languages.values(),
                     help="use LANGUAGE native comment style")
        p.add_option("--overwrite", action="store", 
                     choices = ["yes", "update", "no"],
                     help="overwrite output file (default 'update')")
        p.add_option("-o", "--outfile",
                     help="output file name ('-' for stdout)" )
        p.add_option("--replace", action="store_true",
                     help="move infile to a backup copy (appending '~')")
        p.add_option("-s", "--strip", action="store_true",
                     help="export by stripping text or code")
        p.add_option("-t", "--txt2code", action="store_true",
                     help="convert reStructured text to code")
        self.parser = p

# Calling
# ~~~~~~~
# 
# "Calling" an instance parses the argument list to get option values and 
# completes the option values based on "context-sensitive defaults". 
# Defaults can be provided as keyword arguments. ::

    def __call__(self, args=sys.argv[1:], **keyw):
        """parse and complete command line args
        """
        values = self.parse_args(args, **keyw)
        return self.complete_values(values)


# PylitOptions.parse_args
# ~~~~~~~~~~~~~~~~~~~~~~~
# 
# The `parse_args` method calls the `optparse.OptionParser` on command
# line or provided args and returns the result as `PylitOptions.Values`
# instance. Defaults can be provided as keyword arguments::

    def parse_args(self, args=sys.argv[1:], **keyw):
        """parse command line arguments using `optparse.OptionParser`
        
           parse_args(args, **keyw) -> OptionValues instance
        
            args --  list of command line arguments.
            keyw --  keyword arguments or dictionary of option defaults
        """
        # parse arguments
        (values, args) = self.parser.parse_args(args, OptionValues(keyw))
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
            if in_extension in defaults.text_extensions:
                values.txt2code = True
            elif in_extension in defaults.code_extensions:
                values.txt2code = False
        # Auto-determine the output file name
        values.ensure_value("outfile", self.get_outfile_name(values.infile, 
                                                             values.txt2code))
        # Guess conversion direction from outfile filename or set to default
        if values.txt2code is None:
            out_extension = os.path.splitext(values.outfile)[1]
            values.txt2code = not (out_extension in defaults.text_extensions)
        
        # Set the language of the code (default "python")
        if values.txt2code is True:
            code_extension = os.path.splitext(values.outfile)[1]
        elif values.txt2code is False:
            code_extension = os.path.splitext(values.infile)[1]
        values.ensure_value("language", 
                            defaults.languages.get(code_extension, "python"))
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
        if ext in defaults.text_extensions: 
            return base
        # add (first) text extension for code files
        if ext in defaults.code_extensions or txt2code == False:
            return infile + defaults.text_extensions[0]
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

# is_newer
# ~~~~~~~~
# 
# ::  

def is_newer(path1, path2):
    """Check if `path1` is newer than `path2` (using mtime)
    
    Compare modification time of files at path1 and path2.
    
    Non-existing files are considered oldest: Return False if path1 doesnot
    exist and True if path2 doesnot exist.
    
    Return None for equal modification time. (This evaluates to False in a
    boolean context but allows a test for equality.)
    
    """
    try:
        mtime1 = os.path.getmtime(path1)
    except OSError:
        mtime1 = -1
    try:
        mtime2 = os.path.getmtime(path2)
    except OSError:
        mtime2 = -1
    # print "mtime1", mtime1, path1, "\n", "mtime2", mtime2, path2
    
    if mtime1 == mtime2:
        return None
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
        converter = Code2Text(data, **keyw)
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
    converter = get_converter(data, txt2code, **keyw)
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
    delta = list(difflib.unified_diff(old, new, 
                                      fromfile=oldname, tofile=newname))
    if delta:
        print "".join(delta)
    else:
        print oldname
        print newname
        print "no differences found"
    return bool(delta)
       
# main
# ----
# 
# If this script is called from the command line, the `main` function will
# convert the input (file or stdin) between text and code formats.
# 
# Customization
# ~~~~~~~~~~~~~
# 
# Option defaults for the conversion can be as keyword arguments to `main`_. 
# The option defaults will be updated by command line options and extended
# with "intelligent guesses" by `PylitOptions` and passed on to helper
# functions and the converter instantiation.
# 
# This allows easy customization for programmatic use -- just or call `main`
# with the appropriate keyword options (or with a `defaults`
# dictionary.), e.g.:
# 
# >>> defaults = {'language': "c++",
# ...             'codeindent': 4,
# ...             'header_string': '..admonition::'
# ...            }
# 
# >>> main(**defaults)
# 
# ::

def main(args=sys.argv[1:], **defaults):
    """%prog [options] FILE [OUTFILE]
    
    Convert between reStructured Text with embedded code, and
    Source code with embedded text comment blocks"""

# Parse and complete the options::

    options = PylitOptions()(args, **defaults)

# Special actions with early return::

    if options.doctest:
        return run_doctest(**options.as_dict())

    if options.diff:
        return diff(**options.as_dict())

# Open in- and output streams::

    try:
        (data, out_stream) = open_streams(**options.as_dict())
    except IOError, ex:
        print "IOError: %s %s" % (ex.filename, ex.strerror)
        sys.exit(ex.errno)
    
# Get a converter instance::

    converter = get_converter(data, **options.as_dict())
    
# Execute if the ``-execute`` option is set
# Doesnot work with `eval`, as code is not just one expression. ::

    if options.execute:
        print "executing " + options.infile
        if options.txt2code:
            code = str(converter)
        else:
            code = data
        exec code
        return 

# Default action: Convert and write to out_stream::

    out_stream.write(str(converter))
    
    if out_stream is not sys.stdout:
        print "extract written to", out_stream.name
        out_stream.close()

# If input and output are from files, set the modification time (`mtime`) of
# the output file to the one of the input file to indicate that the contained
# information is equal. [#]_ ::

        try:
            os.utime(options.outfile, (os.path.getatime(options.outfile),
                                       os.path.getmtime(options.infile))
                    )
        except OSError:
            pass

    ## print "mtime", os.path.getmtime(options.infile),  options.infile 
    ## print "mtime", os.path.getmtime(options.outfile), options.outfile


# .. [#] Make sure the corresponding file object (here `out_stream`) is
#        closed, as otherwise the change will be overwritten when `close` is 
#        called afterwards (either explicitely or at program exit).
# 
# 
# Rename the infile to a backup copy if ``--replace`` is set::
 
    if options.replace:
        os.rename(options.infile, options.infile + "~")
        

# Run main, if called from the command line::

if __name__ == '__main__':
    main()
 

# Open questions
# ==============
# 
# Open questions and ideas for further development
# 
# Clean code
# ----------
# 
# * can we gain from using "shutils" over "os.path" and "os"?
# * use pylint or pyChecker to enfoce a consistent style? 
# 
# Options
# -------
# 
# * Use templates for the "intelligent guesses" (with Python syntax for string
#   replacement with dicts: ``"hello %(what)s" % {'what': 'world'}``)
# 
# * Is it sensible to offer the `header_string` option also as command line
#   option?
# 
# * Configurable 
#   
# Parsing Problems
# ----------------------
#     
# * How can I include a literal block that should not be in the
#   executable code (e.g. an example, an earlier version or variant)?
# 
#   Workaround: 
#     Use a `quoted literal block` (with a quotation different from
#     the comment string used for text blocks to keep it as commented over the
#     code-text round-trips.
# 
#     Python `pydoc` examples can also use the special pydoc block syntax (no
#     double colon!).
#               
#   Alternative: 
#     use a special "code block" directive or a special "no code
#     block" directive.
#     
# * ignore "matching comments" in literal strings?
# 
#   (would need a specific detection algorithm for every language that
#   supports multi-line literal strings (C++, PHP, Python)
# 
# * Warn if a comment in code will become text after round-trip?
# 
# code syntax highlight
# ---------------------
#   
# use `listing` package in LaTeX->PDF
# 
# in html, see 
# 
# * the syntax highlight support in rest2web
#   (uses the Moin-Moin Python colorizer, see a version at
#   http://www.standards-schmandards.com/2005/fangs-093/)
# * Pygments (pure Python, many languages, rst integration recipe):
#   http://pygments.org/docs/rstdirective/
# * Silvercity, enscript, ...  
# 
# Some plug-ins require a special "code block" directive instead of the
# `::`-literal block. TODO: make this an option
# 
# Ask at docutils users|developers
# 
# * How to handle docstrings in code blocks? (it would be nice to convert them
#   to rst-text if ``__docformat__ == restructuredtext``)
# 
