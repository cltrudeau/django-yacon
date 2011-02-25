#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Foo:
    def __unicode__(self):
        return 'unicode'

f = Foo()
print '%s' % f

print str(f)
