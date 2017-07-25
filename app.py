# Importing the database classes
from db import Base, Category, Items

# Importing necessary sqlalchemy modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importing neccessary flask modules
from flask import Flask, render_template, url_for, request, jsonify, flash, redirect

# Creating instance of Flask 
app = Flask(__name__, template_folder= 'templates')

# Connect to the database
engine = create_engine('sqlite:///catalog.db')

# Bind engine to Base
Base.metadata.bind = engine

# Creating instance of sessionmaker
DBSession = sessionmaker(bind=engine)

# Instatiate the DBSession Class
session = DBSession()


# Route for showing all categories 
@app.route('/')
@app.route('/categories')
def showCategories():
	categories = session.query(Category).all()
	return render_template('public_categories.html', categories= categories)


# Route to show specific category items
@app.route('/categories/<int:category_id>/items')
def showItems(category_id):
	items = session.query(Items).filter_by(category_id= category_id).all()
	return render_template('public_items.html', items= items, category_id= category_id)


# Route to create a new item for a category_id
@app.route('/categories/<int:category_id>/items/new', methods= ['GET', 'POST'])
def newItem(category_id):
	if request.method == 'GET':
		return render_template('newItem.html', category_id= category_id)
	elif request.method == 'POST':
		name = request.form['name']
		price = request.form['price']
		desc = request.form['desc']
		item = Items(name= name, price= price, desc= desc, category_id= category_id)
		session.add(item)
		session.commit()
		flash('A New Item Added')
		return redirect(url_for('showItems', category_id= item.category_id))


# Route to edit a specific item of a category_id
@app.route('/categories/<int:category_id>/items/<int:item_id>/edit', methods= ['GET', 'POST'])
def editItem(category_id, item_id):
	item = session.query(Items).filter_by(id= item_id).one()
	if request.method == 'GET':
		return render_template('edit_item.html', item= item)
	elif request.method == 'POST':
		item.name = request.form['name']
		item.price = request.form['price']
		item.desc = request.form['desc']
		session.add(item)
		session.commit()
		flash('Item Edit Succefully')
		return redirect(url_for('showItems', category_id= item.category_id))


# Route to delete a specific item of a category_id
@app.route('/categories/<int:category_id>/items/<int:item_id>/delete', methods= ['GET', 'POST'])
def delItem(category_id, item_id):
	item = session.query(Items).filter_by(id= item_id).one()
	if request.method == 'GET':
		return render_template('delete_item.html', item= item)
	elif request.method == 'POST':
		session.delete(item)
		session.commit()
		flash('Item Deleted Successfully')
		return redirect(url_for('showItems', category_id= item.category_id))


# API Endpoint for All Categories 
@app.route('/categories/json')
def categoriesEndpoint():
	categories = session.query(Category).all()
	if categories:
		return jsonify(category= [i.serialize for i in categories])
	else:
		return jsonify({"error": "%s Not Found" % '404'})


# API Endpoint for Items of a Specific category
@app.route('/categories/<int:category_id>/json')
def category_Id_Endpoint(category_id):
	items = session.query(Items).filter_by(category_id= category_id).all()
	if items:
		return jsonify(category= [i.serialize for i in items])
	else:
		return jsonify({"error": "%s Not Found" % '404'})


# API Endpoint for a specific item 
@app.route('/items/<int:item_id>/json')
def category_item_Endpoint(item_id):
	item = session.query(Items).filter_by(id= item_id).one()
	if not item:
		return jsonify({"error": "%s Not Found" % '404'})
	else:
		return jsonify(item= item.serialize)



if __name__ == '__main__':
	app.secret_key= 'Super_secretKey'
	app.run(host='0.0.0.0', port=8080, debug=True)
