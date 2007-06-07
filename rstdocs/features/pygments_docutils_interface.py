# Test the parsing and formatting by pygments:


from docutils import nodes, utils, core
import pygments.lexers
from pygments_code_block_directive import DocutilsInterface
    
source_string = """\
def my_function():
    "just a test"
    print 8/2
"""
    
lexer = pygments.lexers.get_lexer_by_name('python')
tokens = list(pygments.lex(source_string, lexer))
document = utils.new_document('generated')
literal_block = nodes.literal_block(raw_code=source_string.splitlines(True),
                                    classes=["code-block", "python"])
document += literal_block

# You could add e.g. 'p' (Token.Punctuation) to unstyled_tokens.
unstyled_tokens = ['', ]
for cls, value in DocutilsInterface(tokens):
    if cls in unstyled_tokens:
        # insert as Text to decrease the verbosity of the output.
        node = nodes.Text(value, value)
    else:
        node = nodes.inline(value, value, classes=[cls])
    literal_block += node

writer_names = ('html', 'pseudoxml', 'xml', 'latex', 'newlatex2e', 's5')
for name in writer_names[2:3]:
    print "\nusing writer %r\n" % name
    print core.publish_from_doctree(document, writer_name=name)


