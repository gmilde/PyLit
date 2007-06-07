import pygments
import pygments.lexers
from pygments.formatter import Formatter
from pygments.formatters.html import _get_ttype_class


# This formatter class combines code from
# pygments.formatters.html and pygments.formatters.others::

class DocutilsInterface(object):
    """Yield tokens for addition to the docutils document tree.
    
    Merge subsequent tokens of the same token-type. 
    Does not write to a file but yields the tokens as 
    ``(ttype_class, value)`` tuples.

    Where ttype_class is taken from pygments.token.STANDARD_TYPES) and 
    corresponds to the class argument used in pygments html output.

    This formatter differs from the "normal" pygments formatters as it is
    solely intended for programmatic use. It     
    The docutils 'code_block' directive will use this to convert the parsed
    tokens to a <literal_block> doctree element with <inline> nodes for tokes
    with ttype_class != ''.

    """
    name = 'docutils'
    # aliases = ['docutils tokens']

    def __init__(self, tokensource, **options):
        self.tokensource = tokensource

    def __iter__(self):
        lasttype = None
        lastval = u''
        for ttype, value in self.tokensource:
            if ttype is lasttype:
                lastval += value
            else:
                if lasttype:
                    yield(_get_ttype_class(lasttype), lastval)
                lastval = value
                lasttype = ttype
        yield(_get_ttype_class(lasttype), lastval)


# Test the parsing and formatting by pygments:

if __name__ == "__main__":

    from docutils import nodes, utils, core
    
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
    
    # print core.publish_from_doctree(document, writer_name='html')
    # print core.publish_from_doctree(document, writer_name='pseudoxml')
    print core.publish_from_doctree(document, writer_name='xml')
    # print core.publish_from_doctree(document, writer_name='latex')
    # print core.publish_from_doctree(document, writer_name='newlatex2e')

