#!/bin/bash

echo "============================================================"
echo "== pyflakes =="
pyflakes yacon | grep -v migration | grep -v wsgi | grep -v filebrowser | grep -v 3rdparty
