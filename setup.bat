@echo off

echo ===============================
echo Setting up JEE CBT Django App
echo ===============================

echo.
echo Installing pip requirements...
python -m pip install -r requirements.txt

echo.
echo Creating migrations...
python manage.py makemigrations

echo.
echo Applying migrations...
python manage.py migrate

echo.
echo Create a Django superuser (for the administrator panel):
python manage.py createsuperuser

echo.
echo ========================================
echo Setup complete.
echo ========================================
echo.

echo Next steps:
echo.
echo 1. Run the development server:
echo    python manage.py runserver
echo.
echo 2. Open the site:
echo    http://127.0.0.1:8000/
echo.
echo 3. Open the admin panel:
echo    http://127.0.0.1:8000/admin/
echo.
echo 4. Import a JEE test:
echo    python manage.py import_jee_test
echo.

pause