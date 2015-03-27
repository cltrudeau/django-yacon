#!/bin/bash

rm -rf build
rm -rf dist
python setup.py sdist
python setup.py bdist_wheel

echo "now do:"
echo "   twine upload dist/*"
