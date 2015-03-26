django-pagination 1.0.7

- source from:

    http://pypi.python.org/pypi/django-pagination/1.0.7

- included here instead of as egg due to modifications
    - changed template/pagination.html to be yacon-ified
    - redid the logic behind the pagination tag so that it is based on the
      number of characters showing rather than the window
    - moved templatetags and templates into corresponding yacon directories
