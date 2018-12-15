Place your catalog project in this directory.




## pagaes

website has multiple pages

	/ 
		is the main page enlisting categories and recent items. a button to logon is given.

	/catalog/Snowboarding/items
		example for viewing a category items.
		/catalog/<string:category_name>/items

	/catalog/Snowboarding/Snowboard
		example for viewing an item description. 
		/catalog/<string:category_name>/<string:item_name>


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
		id
		name
		email
		password_hash

	Category
		id
		name
		user_id

	Item
		id
		name
		description
		category_id
		user_id

