# yacon.loader.py
#
# Utility function for loading modules.  In its own file to help avoid
# circular dependencies

import logging

logger = logging.getLogger(__name__)

# ============================================================================

def _name_splitter(name):
    fn_name = None
    mod_name = None
    parts = name.split('.')
    fn_name = parts[-1]
    mod_name = '.'.join(parts[:-1])

    return (fn_name, mod_name)


def dynamic_load(name):
    """Equiavlent of a "from X import Y" statement using dot notation to
    separate the module and thing being imported.  Returns the thing being
    imported.  

    Example: dynamic_load('foo.bar.Thing') would load the module "foo.bar" and
    return Thing from it.

    :param name: dot notation for import statement

    :returns: item imported, usually a function or a class
    :raises: will cause exceptions the same way an import will when things
        aren't found properly
    """
    (fn_name, mod_name) = _name_splitter(name)
    mod = __import__(mod_name, globals(), locals(), [fn_name])

    return getattr(mod, fn_name)


def dynamic_safe_load(name, variable_name, default):
    """Wraps dynamic_load() in a try/except, logs any errors

    :param name: import string to pass to dynamic_load()
    :param variable_name: name of thing trying to be loaded (rather than its
        contents, used in logger message
    :param default: value to return if an exception happens

    :returns: imported item
    """
    try:
        logger.debug('about to import %s', variable_name)
        return dynamic_load(name)
    except Exception:
        (fn_name, mod_name) = _name_splitter(name)
        msg = ('importing %s caused exception, setting:'
            '"%s", module name:"%s", function name: "%s"' )
        logger.exception(msg, variable_name, name, mod_name, fn_name)

    return default
