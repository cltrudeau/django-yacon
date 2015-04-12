#!/bin/bash

find . -name "*.pyc" -exec rm {} \;
rm db.sqlite3

python manage.py makemigrations
python manage.py migrate
python manage.py create_test_users
python manage.py create_test_data
