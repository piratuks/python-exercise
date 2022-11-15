# python-exercise

# Super user:

email: admin@example.com <br />
user: admin <br />
password: admin1234@ <br />

# Create super user:

python manage.py createsuperuser --email admin@example.com --username admin

# Migration:

python manage.py makemigrations
python manage.py migrate

# Clear data:

python manage.py flush

# Populate data:

python manage.py loaddata restaurants.json
python manage.py loaddata menus.json
python manage.py loaddata menu-items.json
python manage.py loaddata menu-menuItems-ref.json
python manage.py loaddata menu-votes.json

# Documentation:

http://127.0.0.1:8000/documentation/swagger.json
http://127.0.0.1:8000/documentation/swagger.yaml
http://127.0.0.1:8000/documentation/swagger/
http://127.0.0.1:8000

# Notes:

Supported authentication is TokenAuthentication
TokenAuthentication are exposed
For swagger authorization enter value "Token <token_value>"

# ENV:

python3 -m venv env
env\Scripts\activate
pip install -r requirements.txt

# Run:

python manage.py runserver
pylint exercise.quickstart --generated-members=objects
autopep8 --in-place --aggressive --aggressive <.py file>
docker-compose up -> http://localhost:8000/
