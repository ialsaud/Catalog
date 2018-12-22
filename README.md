# Project 2: catalog
Submission attempt to Misk Udacity FSDN two project. 
* **Author** Ibrahim AlSaud
* **Instructor** Elham Jaffar
* **Date** 12/22/2018


# getting started. 

## prepare the following:
* install and run the vagrant virtual machine linked: https://classroom.udacity.com/courses/ud088
* make sure the following the packages are installed, at least check Flask-HTTPAuth:
```
bleach==3.0.2
certifi==2018.11.29
chardet==3.0.4
Click==7.0
Flask==1.0.2
Flask-HTTPAuth==3.2.4
Flask-SQLAlchemy==2.3.2
httplib2==0.12.0
idna==2.8
itsdangerous==1.1.0
Jinja2==2.10
MarkupSafe==1.1.0
oauth2client==4.1.3
packaging==18.0
passlib==1.7.1
pep8==1.7.1
psycopg2-binary==2.7.6.1
pyasn1==0.4.4
pyasn1-modules==0.2.2
pycodestyle==2.4.0
pyparsing==2.3.0
redis==3.0.1
requests==2.21.0
rsa==4.0
six==1.12.0
SQLAlchemy==1.2.15
urllib3==1.24.1
webencodings==0.5.1
Werkzeug==0.14.1
```


## run the following:
```
python database_setup.py
python seeder.py
python application.py
```


## authentication requirements
- please make sure you have your laptop and server connected to the internet for the third party authentication to work. 
- authenticating through the site requires a google plus account. If you have a gmail, it would be as easy as entering the google plus site and confirming the creation of the profile.






# Structure of the site

## pages

website has multiple pages

	/ 
		is the main page enlisting categories and recent items. a button to logon is given.

	/catalog/Snowboarding/items
		example for viewing a category items.
		/catalog/<string:category_name>/items

	/catalog/Snowboarding/Snowboard
		example for viewing an item description. 
		/catalog/<string:category_name>/<string:item_name>

	/login
		page where the user can choose login type to authenticate through the site.


If the user is logged in, then some functionality is added.

	/
		two changes take affect: the logon button changes into a logout button, an option to add an item is added. 

	/catalog/Snowboarding/Snowboard
		if the item is owned by the logged on user then two new options are added: edit and delete.

	/catalog/Snowboarding/Snowboard/edit
		a form is only displayed for the owner user to edit the specification of the item, that is title, category, and description.

	/catalog/Snowboarding/Snowboard/delete
		displays a confirmation form that makes sure the owner user wants to delete the item. 

	/catalog.json
		displays a json dump of the whole database without the users id.



## database

three objects are used in this project
	
	User
		id .pk
		name
		email .idx
		password_hash

	Category
		id pk
		name idx
		user_id fk

	Item
		id .pk
		name .idx
		description
		category_id .fk
		user_id .fk



## Templates and functions


**header**
	the top toolbar that is attached to every page where the user is logged in and it includes the logout button. 

**header_r**
	the opposite of 'header' and has the login button for every page where the user isn't logged in.

**mainPage**
	page with the categories and items.

**itemDetails**
	page that has information about the item i.e. name and description.

**categoryDetails**
	page is for the category specific items.

**login**
	page offers choices (one option for now) to login the site.

**error page**
	page is used to disply an error to the client user which includes an informative message.

**createItem**
	form to enter item information. 

**createCategory**
	form to enter new category information.

**itemEdit**
	form to adjust the contents of an item.





# references
* - snippets of the database code has been reused from the legal tree food exercise in the api lesson. 
* - snippets of the application.py code is take from APIs in /Lesson_4/11_Pale Kale Ocean Eats/Solution Code/views.py
* - beautifying json with advice from https://stackoverflow.com/questions/9105031/how-to-beautify-json-in-python
* - Gotten some fixes from https://docs.sqlalchemy.org/en/latest/orm/contextual.html
* - template orginization is inspired by restaurent exercise used to explain oauth2.0
* - code snippet in login.html template is reused from code in authentication lesson.