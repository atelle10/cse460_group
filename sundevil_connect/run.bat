@echo off
echo SunDevil Connect - Phase 3 Part 1 By: Michael Krasnik ^& Andrew Tellez
echo.

if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate
pip install -r requirements.txt

if not exist "db.sqlite3" (
    python manage.py makemigrations portal
    python manage.py makemigrations core
    python manage.py migrate
    python manage.py shell < create_test_users.py
)
echo.
echo Setup done. Starting server...
echo.
echo Test Accounts created for grading:
echo Admin: username: admin, password: admin123
echo Student: username: mkrasnik , password: pass123
echo Student: username: atelle10, password: pass123
echo.

python manage.py runserver
