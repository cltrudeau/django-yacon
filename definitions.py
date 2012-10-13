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
    'b',
    'blockquote',
    'code',
    'em',
    'img',
    'i',
    'li',
    'ol',
    'strong',
    'ul',
    'h1',
    'h2',
    'h3',
    'p'
]

ALLOWED_ATTRIBUTES = {
    'a' : ['href', 'title'],
    'img' : ['src', ],
}
