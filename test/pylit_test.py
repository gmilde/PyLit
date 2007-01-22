# -*- coding: iso-8859-1 -*-

# ****************************************************
# Literal programming with Python and reStructuredText
# ****************************************************
# 
# :Version:   0.2
# :Date:      2005-09-02
# :Copyright: 2006 Guenter Milde.
#             Released under the terms of the GNU General Public License 
#             (v. 2 or later)


# Test the pylit.py literal python module
# ***************************************

"""pylit_test.py: test the "literal python" module"""

from pprint import pprint
from pylit_02 import *


# Text <-> Code conversion
# ====================

# Test strings
# ------------
#
# ::

textdata = ['.. #!/usr/bin/env python\n',
            '.. # -*- coding: iso-8859-1 -*-\n',
            '\n',
            'Leading text\n',
            '\n',
            'in several paragraphs followed by a literal block::\n',
            '\n',
            "  block1 = 'first block'\n",
            '\n',
            'Some more text and the next block::\n',
            '\n',
            "  block2 = 'second block'\n",
            '  print block1, block2\n',
            '\n',
            'Trailing text.\n']

text = "".join(textdata)
# print text

stripped_text = """Leading text

in several paragraphs followed by a literal block::

Some more text and the next block::

Trailing text.
"""

# using a triple-quoted string for the code (and stripped_code) would create
# problems with the conversion of this test by pylit::

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

stripped_code = "".join(['#!/usr/bin/env python\n',
                         '# -*- coding: iso-8859-1 -*-\n',
                         '\n',
                         "block1 = 'first block'\n",
                         '\n',
                         "block2 = 'second block'\n",
                         'print block1, block2\n',
                         '\n'])

# pprint(textdata)
# pprint(stripped_code.splitlines(True))

# Text2Code
# ---------

def test_Text2Code():
    """Test the Text2Code class converting rst->code"""
    extract = Text2Code(textdata)()
    print codedata, '\n', extract
    # print "".join(extract)
    assert code == "".join(extract)

def test_Text2Code_nonverbose():
    """strip=True should strip text parts"""
    extract = Text2Code(textdata, strip=True)()
    print stripped_code.splitlines(True), "\n", extract
    # pprint(extract)
    assert stripped_code == "".join(extract)


def test_Text2Code_no_blank_line_after_text():
    """conversion should insert missing blank line after text"""
    data = ['text followed by a literal block::\n',
            "  block1 = 'first block'\n"]
    output = ["", # empty header
              "# text followed by a literal block::\n\n",
              "block1 = 'first block'\n"]
    extract = Text2Code(data)()
    print output, '\n', extract
    assert output == extract


def test_Text2Code_no_blank_line_after_code():
    data = ['::\n',
            '\n',
            "  block1 = 'first block'\n",
            "more text"]
    output = ["", # empty header
              "# ::\n\n",
              "block1 = 'first block'\n\n", # added newline
              "# more text"]
    # codedata = ["# text followed by a literal block::\n",
    #         "  foo = 'first'\n"]
    # text = "text followed by a literal block::"
    extract = Text2Code(data)()
    print output, '\n', extract
    assert output == extract, "should insert missing blank line after code"


def test_Text2Code_remove_double_colon():
    raise nose.DeprecatedTest, "feature removed"
    data = ["text followed by a literal block\n",
            "\n",
            "::\n",
            "\n",
            "  foo = 'first'\n"]
    output = ["", # empty header
            "# text followed by a literal block\n\n",
            "foo = 'first'\n"]
    extract = Text2Code(data)()
    print output, '\n', extract
    assert output == extract, "should remove single double colon"


# Code2Text
# ---------

def test_Code2Text():
    """Test Code2Text class converting code->text"""
    converter = Code2Text(codedata)
    # print converter
    extract = converter()
    # print "".join(extract)
    # print text
    print repr(text), '\n', repr("".join(extract))
    assert text == "".join(extract)

def test_Code2Text_nonverbose():
    """Test Code2Text class converting code->rst with strip=True
    
    Should strip code blocks
    """
    extract = Code2Text(codedata, strip=True)()
    print repr(stripped_text)
    print repr("".join(extract))
    print "".join(extract)
    assert stripped_text == "".join(extract)

def test_Code2Text_different_comment_string():
    """Convert only comments with the specified comment string to text
    """
    extract = Code2Text(codedata, comment_string="##", strip=True)()
    print (extract)
    assert "".join(extract) == ""
    data = ["# ::\n",
            "\n",
            "block1 = 'first block'\n",
            "\n", 
            "## more text"]
    output = ['',  # empty header
              '',  # empty text
              '',  # stripped code
              " more text"]
    extract = Code2Text(data, comment_string="##", strip=True)()
    print output, '\n', extract
    assert output == extract

def test_Code2Text_commented_empty_line():
    """A commented empty line should not count as code 
    
    even if the comment misses trailing whitespace present in the 
    `comment string`
    """
    data = ["# ::\n",
            "\n",
            "block1 = 'first block'\n",
            "\n", 
            "#\n", # should count as empty even if != "# \n"
            "# more text\n"]
    output = ['',  # empty header
              '::\n\n',  # leading text
              '',  # stripped code
              "more text\n"]
    extract = Code2Text(data, comment_string="# ", strip=True)()
    print output
    print extract
    assert output == extract


def test_Code2Text_no_blank_line_after_text():
    """keep comments without trailing blank line"""
    data = ["# text followed by code\n",
            "foo = 'first'\n"]
    output = ["",         # empty header
              "::\n\n"  # empty leading text block
              "  # text followed by code\n", # keep as comment
              "  foo = 'first'\n"]
    extract = Code2Text(data)()
    print output, '\n', extract
    assert output == extract 

def test_Code2Text_no_blank_line_after_code():
    """keep comments without leading blank line"""
    data = ["# ::\n",
            "\n",
            "block1 = 'first block'\n", 
            "# more text"]
    output = ['',  # empty header
              '::\n\n',
              "  block1 = 'first block'\n" +
              "  # more text"]              # keep as comment
    extract = Code2Text(data)()
    print output, '\n', extract
    assert output == extract

def test_Code2Text_no_double_colon():
    data = ["# text followed by a literal block\n",
            "\n",
            "foo = 'first'\n"]
    output = ["", # empty header
              "text followed by a literal block\n\n::\n\n", # colons added
              "  foo = 'first'\n"]
    extract = Code2Text(data)()
    print output, '\n', extract
    assert output == extract, "should insert missing double colon"


# Command line use
# ================

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
        assert result is False

    def test_main_diff_strip(self):
        return # produces spurious output...
        result = main(infile=self.codepath, diff=True, strip=True)
        print "diff return value", result
        assert result is True
        
    def test_main_execute(self):
        result = main(infile=self.txtpath, execute=True)
        print result

    def test_main_execute_code(self):
        result = main(infile=self.codepath, execute=True)



import nose
nose.runmodule() # requires nose 0.9.1
sys.exit()
