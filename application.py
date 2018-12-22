#!/usr/bin/env python2.7
#
#
# Project two submission
# Author: Ibrahim AlSaud
# Date: 12/22/2018
# Project name: catalog


# Refernces
# portions of this code is take from APIs
# /Lesson_4/11_Pale Kale Ocean Eats/Solution Code/views.py
#
# beautifying json with advice from https://stackoverflow.com
# /questions/9105031/how-to-beautify-json-in-python
#
# Gotten some fixes from https://docs.sqlalchemy.org/en/latest/orm
# /contextual.html

from database_setup import Base, Category, Item, User

from flask import Flask, jsonify, request, url_for, abort, g
from flask import render_template, redirect, flash, make_response
from flask import session as login_session
from flask_httpauth import HTTPBasicAuth

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy import create_engine

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import random
import string
import json
import httplib2
import requests


auth = HTTPBasicAuth()

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
session = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

SECRET_KEY = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))


# the universal function to verify users.
@auth.verify_password
def verify_password(username_or_token, password):
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(
            username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False

    g.user = user
    login_session['username'] = user.username
    login_session['email'] = user.email
    login_session['userid'] = user.id

    flash("you are logged in.")
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return True


# the oauth connection function that will handle provider response that
# contains the auth code.
@app.route('/oauth/<provider>', methods=['GET', 'POST'])
def login(provider):
    # STEP 1 - Parse the auth code
    auth_code = request.data

    if provider == 'google':
        # STEP 2 - Exchange for a token
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets(
                'client_secrets.json',
                scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(
                json.dumps('Failed to upgrade the authorization code.'),
                401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        link = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token='
        url = ('%s%s' % (link, access_token))
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])

        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        # # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."),
                401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # # Verify that the access token is valid for this app.
        if result['issued_to'] != CLIENT_ID:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        stored_credentials = login_session.get('credentials')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_credentials is not None and gplus_id == stored_gplus_id:
            response = make_response(
                json.dumps('Current user is already connected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store the access token in the session for later use.
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = gplus_id

        # STEP 3 - Find User or make a new one
        # Get user info
        h = httplib2.Http()
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        name = data['name']
        email = data['email']

        # see if user exists, if it doesn't make a new one
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(username=name, email=email)
            session.add(user)
            session.commit()

        # STEP 4 - Make token
        token = user.generate_auth_token(600)

        # STEP 5 - verify the user
        if verify_password(token, ""):
            print("user is verified")

        return "success"

    else:
        return 'Unrecoginized Provider'


# used by the oauth connect function to authenticate the user.
@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


# handle the user request to login.
@app.route('/login')
def loginpage():

    return render_template('login.html', client_id=CLIENT_ID)


# handle the user requests to logout
@app.route('/logout')
def logoutpage():

    return redirect(url_for('authdisconnect'))


# connects with google to revoke the access token.
@app.route('/auth/disconnect')
def authdisconnect():
    access_token = login_session.get('access_token')
    # check if user is logged in.
    if access_token is None:
        print 'user isn\'t logged in'
        flash("you are not logged in.")
        return redirect(url_for('mainPage'))

    link = 'https://accounts.google.com/o/oauth2/revoke?token='
    url = '%s%s' % (link, login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # successfully revoked token.
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['userid']
        flash("you are logged out.")
        return redirect(url_for('mainPage'))
    else:
        return render_template(
            'error.html',
            client_id=CLIENT_ID,
            message="Failed to revoke token for given user.")


#   /
#       is the main page enlisting categories and recent items.
#       a button to logon is given.
# if user is logged in
#       two changes take affect:the logon button changes into a
#       logout button, an option to add an item is added.
@app.route('/')
@app.route('/catalog')
def mainPage():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.id).all()
    items.reverse()

    if 'username' not in login_session:
        return render_template(
            'mainpage_r.html',
            client_id=CLIENT_ID,
            categories=categories,
            items=items)

    return render_template(
        'mainpage.html',
        client_id=CLIENT_ID,
        categories=categories,
        items=items)


#   /catalog/Snowboarding/items
#       example for viewing a category items.
#       /catalog/<int:category_id>/items
@app.route('/catalog/<int:category_id>/items')
@app.route('/catalog/<int:category_id>')
def categoryDetails(category_id):
    category = session.query(Category).filter_by(id=category_id).first()
    items = session.query(Item).filter_by(category_id=category_id).all()

    if 'username' not in login_session:
        return render_template(
            'category_details_r.html',
            client_id=CLIENT_ID,
            category=category,
            items=items)

    return render_template(
        'category_details.html',
        client_id=CLIENT_ID,
        category=category,
        items=items)


#   /catalog/Snowboarding/Snowboard
#       example for viewing an item description.
#       /catalog/<int:category_id>/<int:item_id>
# if logged in
#       if the item is owned by the logged on user then two new options
#       are added:edit and delete.
@app.route('/catalog/<int:category_id>/<int:item_id>')
def itemDetails(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).first()
    item = session.query(Item).filter_by(id=item_id).first()

    if 'username' not in login_session:
        return render_template(
            'item_details_r.html',
            client_id=CLIENT_ID,
            category=category,
            item=item)

    return render_template(
        'item_details.html',
        client_id=CLIENT_ID,
        category=category,
        item=item)


#   /catalog/Snowboarding/Snowboard/edit
#       a form is only displayed for the owner user to edit the
#       specification of the item, that is title, category, and description.
@app.route(
    '/catalog/<int:category_id>/<string:item_id>/edit',
    methods=['GET', 'POST'])
@app.route(
    '/<int:category_id>/<string:item_id>/edit',
    methods=['GET', 'POST'])
def itemEdit(category_id, item_id):
    if 'username' not in login_session:
        return render_template(
            'error.html',
            client_id=CLIENT_ID,
            message="you are not logged in")

    item = session.query(Item).filter_by(id=item_id).first()

    user = session.query(User).filter_by(id=item.user_id).first()
    if not user:
        return render_template(
            'error.html',
            client_id=CLIENT_ID,
            message="user isn't avalible in our records.")

    if login_session['userid'] != user.id:
        return render_template(
            'error.html',
            client_id=CLIENT_ID,
            message="you don't have permission to edit this item.")

    if request.method == 'GET':
        categories = session.query(Category).all()
        category = session.query(Category).filter_by(
            id=category_id).first()

        return render_template(
            'item_edit.html',
            client_id=CLIENT_ID,
            category=category,
            item=item,
            categories=categories)

    if request.method == "POST":

        item.name = request.form['name']
        item.description = request.form['description']
        item.category_id = request.form['category']

        session.commit()
        flash("an item was edited.")
        return redirect(url_for(
            'itemDetails',
            category_id=item.category_id,
            item_id=item.id))

    return render_template(
        'error.html',
        client_id=CLIENT_ID,
        message="issue with item editing function of the site.")


#   /catalog/Snowboarding/Snowboard/delete
#       displays a confirmation form that makes sure the owner
#       user wants to delete the item.
@app.route(
    '/catalog/<int:category_id>/<string:item_id>/delete',
    methods=['GET', 'POST'])
def itemDelete(category_id, item_id):
    if 'username' not in login_session:
        return render_template(
            'error.html',
            client_id=CLIENT_ID,
            message="you are not logged in")

    item = session.query(Item).filter_by(id=item_id).first()

    user = session.query(User).filter_by(id=item.user_id).first()
    if not user:
        return render_template(
            'error.html',
            client_id=CLIENT_ID,
            message="user isn't avalible in our records.")

    if login_session['userid'] != user.id:
        return render_template(
            'error.html',
            client_id=CLIENT_ID,
            message="you don't have permission to delete this item.")

    if request.method == 'GET':
        category = session.query(Category).filter_by(
            id=category_id).first()
        item = session.query(Item).filter_by(id=item_id).first()

        return render_template(
            'item_delete.html',
            client_id=CLIENT_ID,
            category=category, item=item)

    if request.method == "POST":

        item = session.query(Item).filter_by(id=item_id).first()
        session.delete(item)
        session.commit()

        flash("an item was deleted.")
        return redirect(url_for(
            'categoryDetails',
            category_id=item.category_id))

    return render_template(
        'error.html',
        client_id=CLIENT_ID,
        message="issue with deletion function of the site.")


#   /item/create
#       form page that is only allowed for logged in users.
#       It will enable the user to create a new item.
@app.route('/item/create', methods=['GET', 'POST'])
def itemCreate():

    if 'username' not in login_session:
        return render_template(
            'error.html',
            client_id=CLIENT_ID,
            message="you are not logged in")

    if request.method == 'GET':
        print('cate')
        categories = session.query(Category).all()
        return render_template(
            'item_create.html',
            client_id=CLIENT_ID,
            categories=categories)

    if request.method == "POST":
        print('post')
        if session.query(Item).filter_by(name=request.form['name']).first():
            flash("this item already exists.")
            return redirect(url_for('itemCreate'))

        item = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['category'],
            user_id=login_session['userid'])
        session.add(item)
        session.commit()
        flash("new item was created!")
        return redirect(url_for(
            'itemDetails',
            client_id=CLIENT_ID,
            category_id=item.category_id,
            item_id=item.id))

    return render_template(
        'error.html',
        client_id=CLIENT_ID,
        message="issue with the create item function of the site.")


#   /category/create
#       form page that is only allowed for logged in users.
#       It will enable the user to create a new category.
@app.route('/category/create', methods=['GET', 'POST'])
def categoryCreate():
    if 'username' not in login_session:
        return render_template(
            'error.html',
            client_id=CLIENT_ID,
            message="you are not logged in")

    if request.method == 'GET':

        return render_template('category_create.html', client_id=CLIENT_ID)

    if request.method == "POST":

        if session.query(Category).filter_by(
                name=request.form['name']).first():
            flash("this category already exists.")
            return redirect(url_for('categoryCreate'))

        category = Category(
            name=request.form['name'],
            user_id=login_session['userid'])
        session.add(category)
        session.commit()

        flash("new category was created!")
        return redirect(url_for(
            'categoryDetails',
            client_id=CLIENT_ID,
            category_id=category.id))

    return render_template(
        'error.html',
        client_id=CLIENT_ID,
        message="issue with the category creation function of the site.")


#   /catalog.json
#       displays a json dump of the whole database without the users id.
@app.route('/catalog.json')
def api():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.id).all()

    ret = {"Category": []}

    for category in categories:
        items = session.query(Item).filter_by(category_id=category.id).all()
        if items != []:
            ret["Category"].append({
                "id": category.id,
                "name": category.name,
                "Item": [{
                    "cate_id": item.category_id,
                    "description": item.description,
                    "id": item.id,
                    "title": item.name
                    } for item in items]
                })
        else:
            ret["Category"].append({
                "id": category.id,
                "name": category.name
                })

    return jsonify(ret)


#   /<int:item_id>/item.json
#       displays a json dump of the item id mentioned in the path.
@app.route('/<int:item_id>/item.json')
def itemAPI(item_id):
    item = session.query(Item).filter_by(id=item_id).first()

    if item:
        return jsonify({
                "cate_id": item.category_id,
                "description": item.description,
                "id": item.id,
                "title": item.name
                })

    return render_template(
        'error.html',
        client_id=CLIENT_ID,
        message="item does not exists in the database")


if __name__ == '__main__':
    app.debug = True
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run(host='0.0.0.0', port=5000)
