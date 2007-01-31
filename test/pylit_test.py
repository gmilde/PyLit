#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Test the pylit.py literal python module
# =======================================
# 
# :Version:   0.2
# :Date:      2005-09-02
# :Copyright: 2006 Guenter Milde.
#             Released under the terms of the GNU General Public License 
#             (v. 2 or later)
# 
# .. contents::
# 
# ::

"""pylit_test.py: test the "literal python" module"""

from pprint import pprint
from pylit import *

# Text <-> Code conversion
# ========================
# 
# Test strings
# ------------
# 
# First, a longer text, code and stripped code to "get the main picture"::

text = """..  #!/usr/bin/env python
  # -*- coding: iso-8859-1 -*-

Leading text

in several paragraphs followed by a literal block::

  block1 = 'first block'

Some more text and the next block::

  block2 = 'second block'
  print block1, block2

Trailing text.
"""
# print text

# The converter expects the data in separate lines (iterator or list)
# with trailing newlines. We use the `splitlines` string method with
# `keepends=True`::

textdata = text.splitlines(True)
# print textdata

# If a "code source" is converted with the `strip` option, only text blocks
# are extracted, which leads to::

stripped_text = """Leading text

in several paragraphs followed by a literal block::

Some more text and the next block::

Trailing text.
"""

# The code corresponding to the text test string.
# 
# using a triple-quoted string for the code (and stripped_code) would create
# problems with the conversion of this test by pylit 
# (as the text parts would be converted to text) 
# ::

codedata = ['#!/usr/bin/env python\n',
            '# -*- coding: iso-8859-1 -*-\n',
            '\n',
            '# Leading text\n',
            '# \n',
            '# in several paragraphs followed by a literal block::\n',
            '\n',
            "block1 = 'first block'\n",
            '\n',
            '# Some more text and the next block::\n',
            '\n',
            "block2 = 'second block'\n",
            'print block1, block2\n',
            '\n',
            '# Trailing text.\n']

code = "".join(codedata)
# print code

# Converting the text teststring with the `strip` option leads to::

stripped_code = "".join(['#!/usr/bin/env python\n',
                         '# -*- coding: iso-8859-1 -*-\n',
                         '\n',
                         "block1 = 'first block'\n",
                         '\n',
                         "block2 = 'second block'\n",
                         'print block1, block2\n',
                         '\n'])

## pprint(textdata)
## pprint(stripped_code.splitlines(True))

# Containers for special case examples:
# 
# 1. Text2Code samples
# ``textsamples["what"] = (<text data>, <output>, <output (with `strip`)``
# ::

textsamples = {}

# 2. Code2Txt samples
# ``codesamples["what"] = (<code data>, <output>, <output (with `strip`)``
# ::

codesamples = {}

# Auxiliary function to test the textsamples and codesamples::

def check_converter(key, converter, output):
    print "failed:", key
    extract = converter()
    # print "".join(data)
    print "ist: ", extract
    print "soll:", output
    assert output == extract

# Test generator for textsample tests::

def test_Text2Code_samples():
    for key, sample in textsamples.iteritems():
        yield check_converter, key, Text2Code(sample[0]), sample[1]
        if len(sample) == 3:
            yield (check_converter, key, 
                   Text2Code(sample[0], strip=True), sample[2])

# Test generator for codesample tests::

def test_Code2Text_samples():
    for key, sample in codesamples.iteritems():
        yield check_converter, key, Code2Text(sample[0]), sample[1]
        if len(sample) == 3:
            yield (check_converter, key, 
                   Code2Text(sample[0], strip=True), sample[2])


# Text2Code
# ---------
# 
# base tests on the "long" test data ::

def test_Text2Code():
    """Test the Text2Code class converting rst->code"""
    outstr = str(Text2Code(textdata))
    print code,
    print outstr
    assert code == outstr

def test_Text2Code_strip():
    """strip=True should strip text parts"""
    outstr = str(Text2Code(textdata, strip=True))
    print stripped_code
    print outstr
    # pprint(outstr)
    assert stripped_code == outstr

def test_Text2Code_malindented_code_line():
    """raise error if code line is less indented than code-indent"""
    data1 = ["..    #!/usr/bin/env python\n", # indent == 4 * " "
            "\n",
            "  print 'hello world'"]          # indent == 2 * " "
    data2 = ["..\t#!/usr/bin/env python\n",   # indent == 4 * " "
            "\n",
            "  print 'hello world'"]          # indent == 2 * " "
    for data in (data1, data2):
        try:
            blocks = Text2Code(data)()
            assert False, "wrong indent did not raise ValueError"
        except ValueError:
            pass


# Special Cases
# ~~~~~~~~~~~~~
# 
# Code follows text block without blank line
# ''''''''''''''''''''''''''''''''''''''''''
# 
# End of text block detected ('::') but no paragraph separator (blank line)
# follows
# 
# It is an reStructuredText syntax error, if a "literal block
# marker" is not followed by a blank line.
# 
# Assuming that no double colon at end of line occures accidentially,
# pylit will fix this and issue a warning::

textsamples["insert missing blank line after text"] = (
    ['text followed by a literal block::\n',
     "  block1 = 'first block'\n"],
    [[], # empty header
     ["# text followed by a literal block::\n", "\n"],
     ["block1 = 'first block'\n"]
    ])

# Text follows code block without blank line
# ''''''''''''''''''''''''''''''''''''''''''
# 
# End of code block detected (a line not more indented than the preceding text
# block)
# 
# reStructuredText syntax demands a paragraph separator (blank line) before
# it.
# 
# Assuming that the unindent is not accidential, pylit fixes this and issues a
# warning::

textsamples["insert missing blank line after code"] = (
    ['::\n',
     '\n',
     "  block1 = 'first block'\n",
     "more text"],
    [[], # empty header
     ["# ::\n", "\n"],
     ["block1 = 'first block'\n", "\n"], # added newline
     ["# more text"]
    ])

# A double colon on a line on its own
# '''''''''''''''''''''''''''''''''''
# 
# As a double colon is added by the Code2Text conversion after a text block
# (if not already present), it could be removed by the Text2Code conversion
# to keep the source small and pretty.
# 
# However, this would put the text and code source line numbers out of sync,
# which is bad for error reporting, failing doctests, and the `pylit_buffer()`
# function in http://jedmodes.sf.net/mode/pylit.sl ::
                                                       
## textsamples["should remove single double colon"] = (
##     ["text followed by a literal block\n",
##      "\n",
##      "::\n",
##      "\n",
##      "  foo = 'first'\n"]
##     ["", # empty header
##      "# text followed by a literal block\n\n",
##      "foo = 'first'\n"]
 

# header samples
# ''''''''''''''
# 
# Convert a leading reStructured text comment  (variant: only if there is
# content on the first line) to a leading code block.  Return an empty list,
# if there is no header. ::

textsamples["simple header"] = (
    ["..  print 'hello world'"],
    [["print 'hello world'"]
    ])

textsamples["no header (start with text)"] = (
    ["a classical example without header::\n",
     "\n",
     "  print 'hello world'"],
    [[],
     ["# a classical example without header::\n",
      "\n"],
     ["print 'hello world'"]
    ])

textsamples["standard header, followed by text"] = (
    ["..  #!/usr/bin/env python\n",
     "  # -*- coding: iso-8859-1 -*-\n",
     "\n",
     "a classical example with header::\n",
     "\n",
     "  print 'hello world'"],
    [["#!/usr/bin/env python\n",
      "# -*- coding: iso-8859-1 -*-\n",
      "\n"],
     ["# a classical example with header::\n",
      "\n"],
     ["print 'hello world'"]
    ])

textsamples["standard header, followed by code"] = (
    ["..  #!/usr/bin/env python\n",
     "\n",
     "  print 'hello world'"],
    [["#!/usr/bin/env python\n", 
      "\n",
      "print 'hello world'"]
    ])



# Code2Text
# ---------
# 
# base tests on the "long" test strings ::

def test_Code2Text():
    """Test Code2Text class converting code->text"""
    outstr = str(Code2Text(codedata))
    # print text
    print repr(text)
    print repr(outstr)
    assert text == outstr

def test_Code2Text_strip():
    """Test Code2Text class converting code->rst with strip=True
    
    Should strip code blocks
    """
    outstr = str(Code2Text(codedata, strip=True))
    print repr(stripped_text)
    print repr(outstr)
    print outstr
    assert stripped_text == outstr

def test_Code2Text_different_comment_string():
    """Convert only comments with the specified comment string to text
    """
    outstr = str(Code2Text(codedata, comment_string="##", strip=True))
    print outstr
    assert outstr == ""
    data = ["# ::\n",
            "\n",
            "block1 = 'first block'\n",
            "\n", 
            "## more text"]
    soll = [['..  # ::\n', 
             '\n', 
             "  block1 = 'first block'\n", 
             '\n'],                # leading code block as header
            [' more text']         # keep space (not part of comment string)
           ]
    output = Code2Text(data, comment_string="##")()
    print "ist ", output
    print "soll", soll
    assert output == soll

# Special cases
# ~~~~~~~~~~~~~
# 
# blank comment line
# ''''''''''''''''''''
# 
# Normally, whitespace in the comment string is significant, i.e. with
# `comment_string = "# "`, a line "#something\n" will count as code.
# 
# However, if a comment line is blank, trailing whitespace in the comment
# string should be ignored, i.e. "#\n" is recognized as a blank text line::

codesamples["ignore trailing whitespace in comment string for blank line"] = (
    ["# ::\n",
     "\n",
     "block1 = 'first block'\n",
     "\n", 
     "#\n", # should count as empty even if != "# \n"
     "# more text\n"],
    [[],                # empty header
     ["::\n",
      "\n"],            # leading text
     ["  block1 = 'first block'\n", 
      "\n"], 
     ["\n", 
      "more text\n"]
    ])


# No blank line after text
# ''''''''''''''''''''''''
# 
# If a matching comment precedes oder follows a code line (i.e. any line
# without matching comment) without a blank line inbetween, it counts as code
# line. 
# 
# This will keep small inline comments close to the code they comment on. It
# will also keep blocks together where one commented line doesnot match the
# comment string (the whole block will be kept as commented code)
# ::

codesamples["comment before code (without blank line)"] = (
    ["# this is text::\n",
     "# \n",
     "# this is a comment\n",
     "foo = 'first'\n"],
    [[],         # empty header
     ["this is text::\n", 
      "\n"],  # leading text block
     ["  # this is a comment\n", 
      "  foo = 'first'\n"]
    ])

codesamples["comment after code (without blank line)"] = (
    ["# ::\n",
     "\n",
     "block1 = 'first block'\n", 
     "# commented code"],
    [[],  # empty header
     ['::\n', 
      '\n'],
     ["  block1 = 'first block'\n",
      "  # commented code"]
    ])


# missing literal block marker
# ''''''''''''''''''''''''''''
# 
# If text (with matching comment string) is followed by code (line(s) without
# matching comment string), but there is no double colon at the end, back
# conversion would not recognize the end of text!
# 
# Therefore, pylit adds a paragraph containing only "::" -- the literal block
# marker in expanded form. (While it would in many cases be nicer to add the
# double colon to the last text line, this is not always valid rst syntax,
# e.g. after a section header or a list. Therefore the automatic insertion
# will use the save form, feel free to correct this by hand.)::

codesamples["insert missing double colon after text block"] = (
    ["# text followed by code without double colon\n",
     "\n",
     "foo = 'first'\n"],
    [[], # empty header
     ["text followed by code without double colon\n",
      "\n",
      "::\n", # colons added
      "\n"], 
     ["  foo = 'first'\n"]
    ])

# header samples
# ''''''''''''''
# 
# Convert a header (leading code block) to a reStructured text comment. Return
# an empty list, if there is no leading code. ::

codesamples["no matching comment, just code"] = (
    ["print 'hello world'"],
    [["..  print 'hello world'"]
    ])

codesamples["empty header (start with matching comment)"] = (
    ["# a classical example without header::\n",
     "\n",
     "print 'hello world'"],
    [[],
     ["a classical example without header::\n",
      "\n"],
     ["  print 'hello world'"]
    ])

codesamples["standard header, followed by text"] = (
    ["#!/usr/bin/env python\n",
     "# -*- coding: iso-8859-1 -*-\n",
     "\n",
     "# a classical example with header::\n",
     "\n",
     "print 'hello world'"],
    [["..  #!/usr/bin/env python\n",
      "  # -*- coding: iso-8859-1 -*-\n",
      "\n"],
     ["a classical example with header::\n",
      "\n"],
     ["  print 'hello world'"]
    ])

codesamples["standard header, followed by code"] = (
    ["#!/usr/bin/env python\n",
     "\n",
     "print 'hello world'"],
    [["..  #!/usr/bin/env python\n", 
      "\n",
      "  print 'hello world'"]
    ])



# Command line use
# ================
# 
# Test the option parsing::

def test_Values():
    values = OptionValues()
    print values
    defaults = {"a1": 1, "a2": False}
    values = OptionValues(defaults)
    print values, values.as_dict()
    assert values.a1 == 1
    assert values.a2 == False
    assert values.as_dict() == defaults
        


class test_PylitOptions:
    """Test the PylitOption class"""
    def setUp(self):
        self.options = PylitOptions()
        
    def test_languages_and_extensions(self):
        """dictionary of programming languages and extensions"""
        for ext in [".py", ".sl", ".c"]:
            assert ext in self.options.code_extensions
        assert self.options.code_languages[".py"] == "python"
        assert self.options.code_languages[".sl"] == "slang"
        assert self.options.code_languages[".c"] == "c++"
        
    def test_parse_args(self):
        """parse cmd line args"""
        # default should appear in options
        values = self.options.parse_args(txt2code=False)
        print values, type(values), dir(values)
        assert values.txt2code == False
        # "cmd line arg should appear as option overwriting default"
        values = self.options.parse_args(["--txt2code"], txt2code=False)
        assert values.txt2code == True
        # "1st non option arg is infile, 2nd is outfile"
        values = self.options.parse_args(["--txt2code", "text.txt", "code.py"])
        print values.infile
        assert values.infile == "text.txt"
        assert values.outfile == "code.py"
        # set the output (option with argument)
        values = self.options.parse_args(["--outfile", "code.py"])
        assert values.outfile == "code.py"
        
    def test_get_outfile_name(self):
        """should return a sensible outfile name given an infile name"""
        # return stdout for stdin
        assert "-" == self.options.get_outfile_name("-")
        # return with ".txt" stripped
        assert "foo.py" == self.options.get_outfile_name("foo.py.txt")
        # return with ".txt" added if extension marks code file
        assert "foo.py.txt" == self.options.get_outfile_name("foo.py")
        assert "foo.sl.txt" == self.options.get_outfile_name("foo.sl")
        assert "foo.c.txt" == self.options.get_outfile_name("foo.c")
        # return with ".txt" added if txt2code == False (not None!)
        assert "foo.py.txt" == self.options.get_outfile_name("foo.py", txt2code=False)
        # catchall: add ".out" if no other guess possible
        assert "foo.out" == self.options.get_outfile_name("foo", txt2code=None)

    def test_complete_values(self):
        """Basic test of the option completion"""
        values = optparse.Values()
        values.infile = "foo"
        values = self.options.complete_values(values)
        # the following options should be set:
        print values.infile # logo, as we give it...
        print values.outfile
        assert values.outfile == "foo.out" # fallback extension .out added
        print values.txt2code
        assert values.txt2code == True # the default
        print values.language
        assert values.language == "python" # the default

    def test_complete_values_txt(self):
        """Test the option completion with a text input file"""
        values = optparse.Values()
        values.infile = "foo.txt"
        values = self.options.complete_values(values)
        # should set outfile (see also `test_get_outfile_name`)
        assert values.outfile == "foo"
        # should set conversion direction according to extension
        assert values.txt2code == True
        
    def test_complete_values_code(self):
        """Test the option completion with a code input file"""
        values = optparse.Values()
        values.infile = "foo.py"
        values = self.options.complete_values(values)
        # should set outfile name
        assert values.outfile == "foo.py.txt"
        # should set conversion directions according to extension
        print values.txt2code
        assert values.txt2code == False
        
    def test_complete_values_dont_overwrite(self):
        """The option completion must not overwrite existing option values"""
        values = optparse.Values()
        values.infile = "foo.py"
        values.outfile = "bar.txt"
        values.txt2code = True
        values = self.options.complete_values(values)
        assert values.outfile == "bar.txt"
        assert values.txt2code == True
        
    def test_init(self):
        options = PylitOptions(["--txt2code", "foo"], txt2code=False)
        pprint(options)
        assert options.values.txt2code == True
        assert options.values.infile == "foo"



# Input and Output streams
# ------------------------
# 
# ::

class IOTests:
    """base class for IO tests, sets up and tears down example files in /tmp
    """
    txtpath = "/tmp/pylit_test.py.txt"
    codepath = "/tmp/pylit_test.py"
    outpath = "/tmp/pylit_test.out"
    #
    def setUp(self):
        """Set up the test files"""
        txtfile = file(self.txtpath, 'w')
        txtfile.write(text)
        # txtfile.flush()  # is this needed if we close?
        txtfile.close()
        #
        codefile = file(self.codepath, 'w')
        codefile.write(code)
        # codefile.flush()  # is this needed if we close?
        codefile.close()
    #
    def tearDown(self):
        """clean up after all member tests are done"""
        try:
            os.unlink(self.txtpath)
            os.unlink(self.codepath)
            os.unlink(self.outpath)
        except OSError:
            pass


class test_Streams(IOTests):
    def test_is_newer(self):
        # this __file__ is older, than code file
        print __file__, os.path.getmtime(__file__)
        print self.codepath, os.path.getmtime(self.codepath) 
        #
        assert is_newer(self.codepath, __file__), "file1 is newer"
        assert is_newer(__file__, self.codepath) == False, "file2 is newer"
        assert is_newer(__file__, "fffo"), "file2 doesnot exist"
        assert is_newer("fflo", __file__) == False, "file1 doesnot exist"
        #
        assert is_newer(__file__, __file__) == False, "equal is not newer"
        assert is_newer("fflo", "fffo") == False, "no file exists"
    
    def test_open_streams(self):
        # default should return stdin and -out:
        (instream, outstream) = open_streams()
        assert instream is sys.stdin
        assert outstream is sys.stdout
        
        # open input and output file
        (instream, outstream) = open_streams(self.txtpath, self.outpath)
        assert type(instream) == file
        assert type(outstream) == file
        # read something from the input
        assert instream.read() == text
        # write something to the output
        outstream.write(text)
        # check the output, we have to flush first
        outstream.flush()
        outfile = file(self.outpath, 'r')
        assert outfile.read() == text

    def test_open_streams_no_infile(self):
        """should exit with usage info if no infile given"""
        try:
            (instream, outstream) = open_streams("")
            assert False, "should rise SystemExit"
        except IOError:
            pass

# Another convenience function that returns a converter instance::

def test_get_converter():
    # with default or txt2code
    converter = get_converter(textdata)
    print converter.__class__
    assert converter.__class__ == Text2Code
    converter = get_converter(textdata, txt2code=False)
    assert converter.__class__ == Code2Text

# the run_doctest runs a doctest on the text version (as doc-string)
class test_Run_Doctest(IOTests):
    """Doctest should run on the text source"""
    def test_doctest_txt2code(self):
        (failures, tests) = run_doctest(self.txtpath, txt2code=True)
        assert (failures, tests) == (0, 0)
    def test_doctest_code2txt(self):
        (failures, tests) = run_doctest(self.codepath, txt2code=False)
        assert (failures, tests) == (0, 0)

# The main() function is called if the script is run from the command line
# 
# ::

class test_Main(IOTests):
    """test default operation from command line
    """
    def get_output(self):
        """read and return the content of the output file"""
        outstream = file(self.outpath, 'r')
        return outstream.read()
        
    def test_text_to_code(self):
        """test conversion of text file to code file"""
        main(infile=self.txtpath, outfile=self.outpath)
        output = self.get_output()
        print repr(output)
        assert output == code
                
    def test_text_to_code_strip(self):
        """test conversion of text file to stripped code file"""
        main(infile=self.txtpath, outfile=self.outpath, strip=True)
        output = self.get_output()
        print repr(output)
        assert output == stripped_code
                
    def test_main_code_to_text(self):
        """test conversion of code file to text file"""
        main(infile=self.codepath, outfile=self.outpath)
        output = self.get_output()
        assert output == text
    
    def test_main_code_to_text_strip(self):
        """test conversion of code file to stripped text file"""
        main(infile=self.codepath, outfile=self.outpath, strip=True)
        output = self.get_output()
        assert output == stripped_text

    def test_main_diff(self):
        result = main(infile=self.codepath, diff=True)
        print "diff return value", result
        assert result is False # no differences found

    def test_main_diff_with_differences(self):
        """diffing a file to itself should fail, as the input is converted"""
        result = main(infile=self.codepath, outfile=self.codepath, diff=True)
        print "diff return value", result
        assert result is True # differences found
        
    def test_main_execute(self):
        result = main(infile=self.txtpath, execute=True)
        print result

    def test_main_execute_code(self):
        result = main(infile=self.codepath, execute=True)



import nose
nose.runmodule() # requires nose 0.9.1
sys.exit()
