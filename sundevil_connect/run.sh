#!/bin/bash

echo "SunDevil Connect - Phase 3 Part 1 By: Michael Krasnik & Andrew Tellez"
echo ""

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

if [ ! -f "db.sqlite3" ]; then
    python3 manage.py makemigrations portal
    python3 manage.py makemigrations core
    python3 manage.py migrate
    python3 manage.py shell < create_test_users.py
fi
echo ""
echo "Setup done. Starting server..."
echo ""
echo "Test Accounts created for grading:"
echo "Admin: username: admin, password: admin123"
echo "Student: username: mkrasnik , password: pass123"
echo "Student: username: atelle10, password: pass123"
echo ""

python3 manage.py runserver
