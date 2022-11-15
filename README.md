# Super user:

email: admin@example.com <br />
user: admin <br />
password: admin1234@ <br />

# Create super user:

python manage.py createsuperuser --email admin@example.com --username admin <br />

# Migration:

python manage.py makemigrations <br />
python manage.py migrate <br />

# Clear data:

python manage.py flush <br />

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

Supported authentication is TokenAuthentication <br />
TokenAuthentication are exposed <br />
For swagger authorization enter value "Token <token_value>" <br />

# ENV:

python3 -m venv env <br />
env\Scripts\activate <br />
pip install -r requirements.txt <br />
pip freeze <br />

# Run:

python manage.py runserver <br />
pylint exercise.quickstart --generated-members=objects <br />
autopep8 --in-place --aggressive --aggressive <.py file> <br />
docker-compose up -> http://localhost:8000/ <br />
