import httplib2
import json
import random
import string

# Importing the database classes
from db import Base, Category, Items, User

# Importing necessary sqlalchemy modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

# Importing Google Sign IN OAuth Libs
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

# Importing neccessary flask modules
from flask import Flask, render_template, url_for, request, jsonify, flash, redirect
from flask import session as login_session
from flask import make_response

# Creating instance of Flask
app = Flask(__name__, template_folder='templates')

# Connect to the database
engine = create_engine('sqlite:///catalog.db')

# Bind engine to Base
Base.metadata.bind = engine

# Creating instance of sessionmaker
DBSession = sessionmaker(bind=engine)

# Instatiate the DBSession Class
session = DBSession()

# Fetching Client_id from client_secrets.json
CLIENT_ID = json.loads(
    open('Client_Secrets/client_secrets.json', 'r').read())['web']['client_id']


# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


# Create an anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Route for Google Sign in Authentication
@app.route('/gconnect', methods= ['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'Client_Secrets/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    # Verify that user is already logged in or not
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    url1 = (
        'https://www.googleapis.com/oauth2/v1/userinfo?access_token=%s&alt=%s' %
        (access_token, 'json'))
    data = json.loads(h.request(url1, 'GET')[1])

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])

    # If user not exists create one
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<img src="'
    output += login_session['picture']
    output += '" id="user_img" alt="profile_pic">'

    return output


# Route for showing all categories
@app.route('/')
@app.route('/categories')
def showCategories():
    categories = session.query(Category).all()
    if 'username' in login_session:
        return render_template('categories.html', categories=categories)
    else:
        return render_template('public_categories.html', categories=categories)


# Route to show specific category items
@app.route('/categories/<int:category_id>/items')
def showItems(category_id):
    category = session.query(Category).filter_by(id= category_id).one()
    items = session.query(Items).filter_by(category_id=category_id).all()
    if 'username' in login_session:
        return render_template(
            'items.html',
            items=items,
            category_id=category_id)
    else:
        return render_template(
            'public_items.html',
            items=items,
            category_id=category_id, category_name=category.name)


# Route to create a new item for a category_id
@app.route('/categories/<int:category_id>/items/new', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' in login_session:
        if request.method == 'GET':
            category = session.query(Category).filter_by(id= category_id).one()
            return render_template('newItem.html', category_id=category_id, category_name=category.name)
        elif request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            desc = request.form['desc']
            item = Items(
                name=name,
                price=price,
                desc=desc,
                category_id=category_id,
                user_id= login_session['user_id'])
            session.add(item)
            session.commit()
            flash('A New Item Added')
            return redirect(url_for('showItems', category_id=item.category_id))
    else:
        response = make_response(json.dumps('You are not Authorized'), 403)
        response.headers['Content-Type'] = 'application/json'
        return response


# Route to edit a specific item of a category_id
@app.route(
    '/categories/<int:category_id>/items/<int:item_id>/edit',
    methods=[
        'GET',
        'POST'])
def editItem(category_id, item_id):
    if 'username' in login_session:
        item = session.query(Items).filter(Items.id== item_id, Items.category_id== category_id, Items.user_id== login_session['user_id']).one()

        # If no item matches current user_id returns error
        if not item:
            return jsonify({"error": "You can delete your items only"})

        if request.method == 'GET':
            return render_template('edit_item.html', item=item)
        elif request.method == 'POST':
            item.name = request.form['name']
            item.price = request.form['price']
            item.desc = request.form['desc']
            session.add(item)
            session.commit()
            flash('Item Edit Successfully')
            return redirect(url_for('showItems', category_id=item.category_id))
    else:
        response = make_response(json.dumps('You are not Authorized'), 403)
        response.headers['Content-Type'] = 'application/json'
        return response


# Route to delete a specific item of a category_id
@app.route(
    '/categories/<int:category_id>/items/<int:item_id>/delete',
    methods=[
        'GET',
        'POST'])
def delItem(category_id, item_id):
    if 'username' in login_session:
        item = session.query(Items).filter(Items.id== item_id, Items.category_id== category_id, Items.user_id== login_session['user_id']).one()

        # If no item matches current user_id returns error
        if not item:
            return jsonify({"error": "You can delete your items only"})

        if request.method == 'GET':
            return render_template('delete_item.html', item=item)
        elif request.method == 'POST':
            session.delete(item)
            session.commit()
            flash('Item Deleted Successfully')
            return redirect(url_for('showItems', category_id=item.category_id))
    else:
        response = make_response(json.dumps('You are not Authorized'), 403)
        response.headers['Content-Type'] = 'application/json'
        return response


# API Endpoint for All Categories
@app.route('/categories/json')
def categoriesEndpoint():
    categories = session.query(Category).all()
    if categories:
        return jsonify(category=[i.serialize for i in categories])
    else:
        return jsonify({"error": "%s Not Found" % '404'})


# API Endpoint for Items of a Specific category
@app.route('/categories/<int:category_id>/json')
def category_Id_Endpoint(category_id):
    items = session.query(Items).filter_by(category_id=category_id).all()
    if items:
        return jsonify(category=[i.serialize for i in items])
    else:
        return jsonify({"error": "%s Not Found" % '404'})


# API Endpoint for a specific item
@app.route('/items/<int:item_id>/json')
def category_item_Endpoint(item_id):
    item = session.query(Items).filter_by(id=item_id).one()
    if not item:
        return jsonify({"error": "%s Not Found" % '404'})
    else:
        return jsonify(item=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'Super_secretKey'
    app.run(host='0.0.0.0', port=8080, debug=True)
