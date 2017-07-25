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





if __name__ == '__main__':
	app.secret_key= 'Super_secretKey'
	app.run(host='0.0.0.0', port=8080, debug=True)
