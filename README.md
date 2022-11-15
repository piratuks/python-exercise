# python-exercise

# Super user:

email: admin@example.com <br />
user: admin <br />
password: admin1234@ <br />

# Create super user:

python manage.py createsuperuser --email admin@example.com --username admin

# Migration:

python manage.py makemigrations <br />
python manage.py migrate <br />

# Clear data:

python manage.py flush 

# Populate data:

python manage.py loaddata restaurants.json <br />
python manage.py loaddata menus.json <br />
python manage.py loaddata menu-items.json <br />
python manage.py loaddata menu-menuItems-ref.json <br />
python manage.py loaddata menu-votes.json <br />

# Documentation:

http://127.0.0.1:8000/documentation/swagger.json <br />
http://127.0.0.1:8000/documentation/swagger.yaml <br />
http://127.0.0.1:8000/documentation/swagger/ <br />
http://127.0.0.1:8000 <br />

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
