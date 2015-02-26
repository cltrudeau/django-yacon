#!/bin/bash

echo "============================================================"
echo "== pyflakes =="
pyflakes . | grep -v migration | grep -v wsgi | grep -v filebrowser | grep -v playground
