#!/usr/bin/python

# :Author: a Pygments author|contributor; Felix Wiemann; Guenter Milde
# :Date: $Date: $
# :Copyright: This module has been placed in the public domain.
# 
# This is a merge of `Using Pygments in ReST documents`_ from the pygments_
# documentation, and a `proof of concept`_ by Felix Wiemann.
# 
# ========== ===========================================================
# 2007-06-01 Removed redundancy from class values.
# 2007-06-04 Merge of successive tokens of same type
#            (code taken from pygments.formatters.others).
# 2007-06-05 Separate docutils formatter script
#            Use pygments' CSS class names (like the html formatter)
#            allowing the use of pygments-produced style sheets.
# 2007-06-07 Re-include the formatting of the parsed tokens 
#            (class DocutilsInterface)
# ========== ===========================================================
# 
# ::

"""Define and register a code-block directive using pygments
"""

# Requirements
# ------------
# ::

from docutils import nodes
from docutils.parsers.rst import directives
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import _get_ttype_class

# Customisation
# -------------
# 
# Do not insert inline nodes for the following tokens.
# (You could add e.g. Token.Punctuation like ``['', 'p']``.) ::

unstyled_tokens = ['']

# DocutilsInterface
# -----------------

# This interface class combines code from
# pygments.formatters.html and pygments.formatters.others::

class DocutilsInterface(object):
    """Yield tokens for addition to the docutils document tree.
    
    Merge subsequent tokens of the same token-type. 
    
    Yields the tokens as ``(ttype_class, value)`` tuples, 
    where ttype_class is taken from pygments.token.STANDARD_TYPES and 
    corresponds to the class argument used in pygments html output.

    """
    name = 'docutils'
    # aliases = ['docutils tokens']

    def __init__(self, tokensource):
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



# code_block_directive
# --------------------
# ::

def code_block_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    language = arguments[0]
    # create a literal block element and set class argument
    code_block = nodes.literal_block(raw_content=content,
                                     classes=["code-block", language])
    # Get lexer for language (use text as fallback)
    try:
        lexer = get_lexer_by_name(language)
    except ValueError:
        lexer = get_lexer_by_name('text')
    
    # parse content with pygments
    tokens = list(pygments.lex(u'\n'.join(content), lexer))
    
    for cls, value in DocutilsInterface(tokens):
        if cls in unstyled_tokens:
            # insert as Text to decrease the verbosity of the output.
            code_block += nodes.Text(value, value)
        else:
            code_block += nodes.inline(value, value, classes=[cls])

    return [code_block]


# Register Directive
# ------------------
# ::

code_block_directive.arguments = (1, 0, 1)
code_block_directive.content = 1
directives.register_directive('code-block', code_block_directive)

# .. _doctutils: http://docutils.sf.net/
# .. _pygments: http://pygments.org/
# .. _Using Pygments in ReST documents: http://pygments.org/docs/rstdirective/
# .. _proof of concept:
#      http://article.gmane.org/gmane.text.docutils.user/3689
# 
# Test output
# -----------
# 
# If called from the command line, call the docutils publisher to render the
# input::

if __name__ == '__main__':
    from docutils.core import publish_cmdline, default_description
    description = "code-block directive test output" + default_description
    try:
        import locale
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass
    # Uncomment the desired output format:
    publish_cmdline(writer_name='pseudoxml', description=description)
    # publish_cmdline(writer_name='xml', description=description)
    # publish_cmdline(writer_name='html', description=description)
    # publish_cmdline(writer_name='latex', description=description)
    # publish_cmdline(writer_name='newlatex2e', description=description)
    


