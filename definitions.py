# yacon.definitions.py
#
# This file contains common values that aren't usually changed per
# installation and therefore shouldn't go in the django settings file

# max length of slugs
SLUG_LENGTH = 25

# max length of title
TITLE_LENGTH = 50

# bleach constants
ALLOWED_TAGS = [
    'a',
    'address',
    'b',
    'br',
    'blockquote',
    'code',
    'div',
    'em',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'hr',
    'img',
    'i',
    'li',
    'ol',
    'p',
    'pre',
    'span',
    'strike',
    'strong',
    'sub',
    'sup',
    'table',
    'tbody',
    'tr',
    'td',
    'u',
    'ul',
]

ALLOWED_ATTRIBUTES = {
    'a':['href', 'title'],
    'img':['alt', 'src', 'width', 'height', 'style'],
    'table':['border', 'cellpadding', 'cellspacing', 'style', ],
    'p':['style', ],
}

ALLOWED_STYLES = [
    'background-color',
    'border-width',
    'border-height',
    'border-style',
    'color',
    'float',
    'font-family',
    'font-size',
    'height',
    'margin',
    'margin-bottom',
    'margin-left',
    'margin-right',
    'margin-top',
    'text-align',
    'width',
]
