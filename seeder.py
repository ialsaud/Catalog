##
# some of the code below is used from the restaurent exercise in oauth lesson.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Category, Item, Base

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


session.query(User).delete()
session.query(Category).delete()
session.query(Item).delete()



# User
#    id .pk
#    name
#    email .idx
#    password_hash

# Category
#    id pk
#    name idx
#    user_id fk

# Item
#    id .pk
#    name .idx
#    description
#    category_id .fk
#    user_id .fk




users = [
         {'username':'admin', 'email':'admin@email.com'}
        ]

catagories = {
               'tables':'admin',
               'chairs':'admin',
               'lights':'admin' 
            }
      

items = {'chairs':[
            {'name':'small wood chair','description':'''light but uncomfortable
             chair Lorem Ipsum is simply dummy text of the printing and 
             typesetting industry. Lorem Ipsum has been the industry's 
             standard dummy text ever since the 1500s, when an unknown 
             printer took a galley of type and scrambled it to make a 
             type specimen book. It has survived not only five centuries, 
             but also the leap into electronic typesetting, remaining 
             essentially'''}, 

             {'name':'big wood chair','description':'''heavy but uncomfortable
             chair Lorem Ipsum is simply dummy text of the printing and 
             typesetting industry. Lorem Ipsum has been the industry's 
             standard dummy text ever since the 1500s, when an unknown 
             printer took a galley of type and scrambled it to make a 
             type specimen book. It has survived not only five centuries, 
             but also the leap into electronic typesetting, remaining 
             essentially'''}, 

             {'name':'big fabric chair','description':'''heavy comfortable
             chair Lorem Ipsum is simply dummy text of the printing and 
             typesetting industry. Lorem Ipsum has been the industry's 
             standard dummy text ever since the 1500s, when an unknown 
             printer took a galley of type and scrambled it to make a 
             type specimen book. It has survived not only five centuries, 
             but also the leap into electronic typesetting, remaining 
             essentially'''}, 

             {'name':'leather chair','description':'''heavy comfortable
             chair Lorem Ipsum is simply dummy text of the printing and 
             typesetting industry. Lorem Ipsum has been the industry's 
             standard dummy text ever since the 1500s, when an unknown 
             printer took a galley of type and scrambled it to make a 
             type specimen book. It has survived not only five centuries, 
             but also the leap into electronic typesetting, remaining 
             essentially'''}

              ], 


         'tables':[
            {'name':'small wood table','description':'''light and unfunctional
             table Lorem Ipsum is simply dummy text of the printing and 
             typesetting industry. Lorem Ipsum has been the industry's 
             standard dummy text ever since the 1500s, when an unknown 
             printer took a galley of type and scrambled it to make a 
             type specimen book. It has survived not only five centuries, 
             but also the leap into electronic typesetting, remaining 
             essentially'''}, 

             {'name':'big wood table','description':'''heavy but spacious
             table Lorem Ipsum is simply dummy text of the printing and 
             typesetting industry. Lorem Ipsum has been the industry's 
             standard dummy text ever since the 1500s, when an unknown 
             printer took a galley of type and scrambled it to make a 
             type specimen book. It has survived not only five centuries, 
             but also the leap into electronic typesetting, remaining 
             essentially'''}, 

             {'name':'big plastic table','description':'''light and cheap
             table Lorem Ipsum is simply dummy text of the printing and 
             typesetting industry. Lorem Ipsum has been the industry's 
             standard dummy text ever since the 1500s, when an unknown 
             printer took a galley of type and scrambled it to make a 
             type specimen book. It has survived not only five centuries, 
             but also the leap into electronic typesetting, remaining 
             essentially'''}, 

             {'name':'marble table','description':'''heavy fancy
             table Lorem Ipsum is simply dummy text of the printing and 
             typesetting industry. Lorem Ipsum has been the industry's 
             standard dummy text ever since the 1500s, when an unknown 
             printer took a galley of type and scrambled it to make a 
             type specimen book. It has survived not only five centuries, 
             but also the leap into electronic typesetting, remaining 
             essentially'''}
             ]
        }



for user in users:
   temp = User(username=user['username'], email=user['email'])
   temp.hash_password('123')
   session.add(temp)
   session.commit()

print "added users"

for category in catagories.keys():
   user = session.query(User).filter_by(username=catagories[str(category)]).first()
   session.add(Category(name=category, user=user))
   session.commit()

print "added catagories"

for category_name in items.keys():
   category = session.query(Category).filter_by(name=category_name).first()
   for item in items[category_name]:
      session.add(Item(name=item['name'], description=item['description'], category=category, user=category.user))
      session.commit()


print "added items"

print "done!"
