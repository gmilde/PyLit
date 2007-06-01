# This is a proof of concept for a pygments-enhanced docutils parser
# by Felix Wiemann

# On 30.05.07, David Goodger wrote:
# This approach is good.

# 2007-06-01 removing redundancy from the classes  [G Milde]

import pygments
import pygments.lexers
from docutils import nodes, utils, core

source_string = """\
def my_function():
    "just a test"
    print 8/2
"""

print repr(source_string)

lexer = pygments.lexers.get_lexer_by_name('python')
tokens = list(pygments.lex(source_string, lexer))
document = utils.new_document('generated')
literal_block = nodes.literal_block(raw_source=source_string,
                                    classes=["sourcecode", "python"])
document += literal_block
# You could add 'Token.Punctuation' to unstyled_tokens.
unstyled_tokens = ['Token.Text', ]

for token_type, text in tokens:
    # print "token type:", type(token_type), token_type
    token_str = str(token_type)
    if token_str in unstyled_tokens:
        # Do not insert an inline node to decrease the verbosity of
        # the output.
        node = nodes.Text(text, text)
    else:
        classes = token_str.split('.')
        assert classes[0] == "Token"
        classes = [cls.lower() for cls in classes[1:]]
        node = nodes.inline(text, text, classes=classes)
    literal_block += node

#print core.publish_from_doctree(document, writer_name='pseudoxml')
print core.publish_from_doctree(document, writer_name='xml')
#print core.publish_from_doctree(document, writer_name='html')
#print core.publish_from_doctree(document, writer_name='latex')


