## VirCom: Virtual Online Community 
This repository has been created for BOUN SWE 573 course project.

Community Website: https://vircom.appspot.com/vircom/

### LOCAL USE

First of all, Project requires Python 3.4 or higher version. To get Python, you can follow the instructions on https://www.python.org/downloads/.

Now, open the Project the Project and to be able to work on the Project you need to activate virtual environment by running the commands below on your command line/terminal;

virtualenv env
source env/bin/activate

To get the requirements, run the following command;
pip install -r requirements.txt

For database, you need to download PostgreSQL. You can download it from https://www.postgresql.org/download/.

After you download PostgreSQL, create a user and database on your PostgreSQL Admin panel. You can also use default user and database.

In settings.py in your project, enter your database name, user name and password of your PostgreSQL database in DATABASES dictionary.
Also, change the STATIC_URL to ‘/static/’.

You can run Django migrations to set up your models by running commands below:
python manage.py makemigrations
python manage.py makemigrations polls
python manage.py migrate

Now, you are ready for running your app locally! Run the command below:
python manage.py runserver
and in your browser, go to
http://localhost:8000


