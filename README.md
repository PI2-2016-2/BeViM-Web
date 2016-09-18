### BeViM-Web

It is a web application created for an mechanical vibration test equipment.  The application was developed in Python 3.4 with Django 1.9.

### Installation instructions:

* Install virtualenv

    	pip install virtualenv
	
* Create a virtual-env to the project

    **The "-p" option should be used if you have another versions of python installed**
        
        virtualenv bevim-env -p /path/to/python3.4

* Activate the virtualenv
        
        source /path/to/bevim-env

* Clone the repository

        git clone https://github.com/PI2-2016-2/BeViM-Web.git

* Install dependencies
    
        pip install -r path-to-repository/requirements.txt
    

### Running the app

* Create the database on MySQL
        
        CREATE DATABASE bevim-web; 

* Put your username and password from database on _settings.py_ file

        DATABASES = {
            'default':{
                ...
                'USER': 'your_username'
                'PASSWORD': 'your_password'
            }
        }

* Create migrations
        
        python manage.py makemigrations

* Run migrations
        
        python manage.py migrate
     
* Run the app
        
        python manage.py runserver

