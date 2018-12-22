#!/usr/bin/env python2.7
#
#
# Project two submission
# Author: Ibrahim AlSaud
# Date: 12/22/2018
# Project name: catalog


# Refernces
# some of the code below is used from the restaurent exercise in oauth lesson.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Category, Item, Base

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
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
         {'username': 'admin', 'email': 'admin@email.com'}
        ]

catagories = {
               'tables': 'admin',
               'chairs': 'admin',
               'lights': 'admin'
            }
items = {'chairs': [
            {
                'name': 'small wood chair',
                'description': 'light but uncomfortable chair'
            },

            {
                'name': 'big wood chair',
                'description': 'heavy but uncomfortable'
            },

            {
                'name': 'big fabric chair',
                'description': 'heavy comfortable chair'
            },

            {
                'name': 'leather chair',
                'description': 'heavy comfortable chair'
            }
            ],

         'tables': [
            {
                'name': 'small wood table',
                'description': 'light and unfunctional table'
            },

            {
                'name': 'big wood table',
                'description': 'heavy but spacious table'
            },

            {
                'name': 'big plastic table',
                'description': 'light and cheap table'
            },

            {
                'name': 'marble table',
                'description': 'heavy fancy table'
            }
            ]}

for user in users:
    temp = User(username=user['username'], email=user['email'])
    temp.hash_password('123')
    session.add(temp)
    session.commit()

print "added users"

for category in catagories.keys():
    user = session.query(User).filter_by(
        username=catagories[str(category)]).first()
    session.add(Category(name=category, user=user))
    session.commit()

print "added catagories"

for category_name in items.keys():
    category = session.query(Category).filter_by(
        name=category_name).first()
    for item in items[category_name]:
        session.add(
            Item(
                name=item['name'],
                description=item['description'],
                category=category,
                user=category.user))
        session.commit()

print "added items"

print "done!"
