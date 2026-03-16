#!/bin/bash

echo "==============================="
echo "Setting up JEE CBT Django App"
echo "==============================="

# check python
if ! command -v python3 &> /dev/null
then
    echo "Python3 not found. Please install Python 3 first."
    exit
fi

echo ""
echo "Installing pip requirements..."
python3 -m pip install -r requirements.txt

echo ""
echo "Creating migrations..."
python3 manage.py makemigrations

echo ""
echo "Applying migrations..."
python3 manage.py migrate

echo ""
echo "Create a Django superuser (for the administrator panel):"
python3 manage.py createsuperuser

echo ""
echo "========================================"
echo "Setup complete."
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Run the development server:"
echo "   python3 manage.py runserver"
echo ""
echo "2. Open the site:"
echo "   http://127.0.0.1:8000/"
echo ""
echo "3. Open the admin panel:"
echo "   http://127.0.0.1:8000/admin/"
echo ""
echo "4. Import a JEE test:"
echo "   python3 manage.py import_jee_test"
echo ""
echo "========================================"