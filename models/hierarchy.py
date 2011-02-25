# yacon.models.hierarchy.py
# blame ctrudeau chr(64) arsensa.com

import re
import exceptions
from django.db import models
from treebeard.mp_tree import MP_Node

match_word = re.compile('^\w*$')
match_slash = re.compile('/')

# ============================================================================
# Hierarchy Management
# ============================================================================

class ParsedPath():
    def __init__(self, *args, **kwargs):
        self.slugs_in_path = []
        self.slugs_after_node = []
        self.path = ''
        self.node = None

    def __str__(self):
        return \
        'ParsedPath(path=%s, slugs_in_path=%s, slugs_after_node=%s, node=%s)' \
            % (self.path, self.slugs_in_path, self.slugs_after_node, self.node)

class BadSlug(exceptions.Exception):
    pass

class Node(MP_Node):
    """Represents a node in the hierarchical graph used that corresponds to
    URIs and collections of content in the system.  Constructor requires:

    @param name -- human readable name of this node
    @param slug -- portion of the path specifying this node.  For example:
        to add 'milk' to '/articles/health/' (creating '/artciles/health/milk')
        slug='milk', with the '/articles/health' portion of the path
        determined by the node's location in the hierarchy.  Do not include
        leading or trailing '/' characters they are added automatically.
    """
    name = models.CharField(max_length=30)
    slug = models.TextField(unique=True, db_index=True)

    class Meta:
        app_label = 'yacon'

    def __init__(self, *args, **kwargs):
        is_root = False
        try:
            if kwargs['root']:
                is_root = True

            del kwargs['root']
        except KeyError:
            # root parm only gets passed in from ContentHierarchy constructing
            # a new root node, it is used to skip the slug \w check
            pass

        try:
            # check that the slug is of the right form
            if not match_word.search(kwargs['slug']) and not is_root:
                raise BadSlug('Slug must be of form [0-9a-zA-Z_]*')
        except KeyError:
            # MP_Node will construct without parms when reading from the db,
            # if kwarg['slug'] isn't there just ignore it, if the user hasn't
            # provided one it will get caught by MP_Node when it goes to write
            # to the db and raise an exception there
            pass

        super(Node, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return 'Node: %s (%s)' % (self.name, self.slug)

    def _walk_tree_to_string(self, node, output, indent):
        """Breadth first walk of tree returning node as string

        @param node -- node to walk
        @param string -- string to append to before returning
        @param output -- list of lines containing a string from each node
            visited
        @param indent -- how much to indent the displayed node
        """
        output.append('%s%s (%s)' % (3*indent*' ', node.name, node.slug))
        for child in node.get_children():
            self._walk_tree_to_string(child, output, indent+1)

    def tree_to_string(self):
        """Returns a string representation of the sub-tree using the 'self' 
        node as root"""

        output = []
        self._walk_tree_to_string(self, output, 0)
        return "\n".join(output)

    def node_to_path(self):
        """Returns a path string for this node"""
        nodes = []
        for node in self.get_ancestors():
            nodes.append(node)

        # get_ancestors() will include root which we don't use in paths and
        # won't include us, so remove the first and add this node at the end
        nodes.pop(0)
        nodes.append(self)
        return "/%s/" % "/".join([n.slug for n in nodes]) 

    def has_children(self):
        return self.get_children_count() > 0


class PathNotFound(exceptions.Exception):
    pass

class ContentHierarchy():
    """Factory class for dealing with the content hierarchy.  Has a root _Node
    object and can return and manipulate the the tree associated with it."""

    @classmethod
    def get_root(cls):
        # search for a root node
        root = Node.get_first_root_node()
        if root == None:
            root = Node.add_root(name="root", slug="/", root=True)

        return root

    # -----------------------------------------------------------------------
    # Debug Methods
    @classmethod
    def output_tree(cls):
        """Prints tree out to stdout, should only be used to help debug"""
        node = cls.get_root()
        cls._output_node(node)

    @classmethod
    def _output_node(cls, node, indent=0):
        kids = node.get_children()
        for kid in kids:
            cls._output_node(kid, indent+1)

    # -----------------------------------------------------------------------
    # Search Methods

    @classmethod
    def node_from_path(cls, path):
        """Returns the a Node object by walking a uri path that correlates to 
        the tree.  For example, '/blogs/health/milk' will return the id of a
        _Node object corresponding to 'milk' which is a child of health which
        is a child of blogs.  

        @param path -- path portion of a URI for the desired Node.  Leading
            and trailing slashes are optional and ignored
        @raise PathNotFound -- if the path passed in doesn't correspond to the
            hierarchy
        @return -- id of a _Node object"""

        node = cls.get_root()
        parts = match_slash.split(path)
        for part in parts:
            if part == '':
                continue 

            kids = node.get_children()
            found = False
            for kid in kids:
                if kid.slug == part:
                    found = True
                    node = kid
                    break

            if not found:
                raise PathNotFound('%s has no child %s' % (node.slug, part))

        # if you get here succesfully then node is the last piece
        return node

    @classmethod
    def parse_path(cls, path):
        """Returns a ParsedPath object by walking the path given until it
        runs out of either tree or the path.  The ParsedPath object contains
        the list of slugs in the path and any slugs after the path (i.e. if we
        run out of tree) along with a Node object.  If the path does not
        result in finding a node then a ParsedPath object is still returned

        @param path -- path to walk to find a container Node 
        @return -- ParsedPath object.
            ParsedPath.slugs_in_path -- a list of slugs in the path passed in
            ParsedPath.slugs_after_node -- a list of slugs found in the path
                after we ran out of tree to walk
            ParsedPath.Node -- the Node object corresponding to the part of
                the tree where we ran out of path.  If the path does not
                correspond to the tree then Node will be None and all slugs in
                the path will be in ParsedPath.slugs_after_node"""

        node = cls.get_root()
        parsed = ParsedPath()
        parsed.path = path
        parts = match_slash.split(path)
        end_of_tree = False
        for part in parts:
            if part == '':
                continue 

            if not end_of_tree:
                kids = node.get_children()
                found = False
                for kid in kids:
                    if kid.slug == part:
                        found = True
                        parsed.slugs_in_path.append(part)
                        parsed.node = kid
                        node = kid
                        break

                if not found:
                    parsed.slugs_after_node.append(part)
                    end_of_tree = True
            else:
                parsed.slugs_after_node.append(part)

        return parsed
