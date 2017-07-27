# Importing necessary sqlalchemy modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importing the database classes
from db import Base, Category, Items

# Connect to the database
engine = create_engine('sqlite:///catalog.db')

# Bind engine to Base
Base.metadata.bind = engine

# Creating instance of sessionmaker
DBSession = sessionmaker(bind=engine)

# Instatiate the DBSession Class
session = DBSession()

category1 = Category(name= 'Udacity')
session.add(category1)
session.commit()

category2 = Category(name= 'Google')
session.add(category2)
session.commit()


item1 = Items(name= 'FSND', price= '1000$', desc= 'Full Stack NanoDegree', category= category1)
session.add(item1)
session.commit()

item2 = Items(name= 'Android', price= '2000$', desc= 'Android Nanodegree', category= category1)
session.add(item2)
session.commit()

item3 = Items(name= 'IOS', price= '5000$', desc= 'IOS NanoDegree', category= category1)
session.add(item3)
session.commit()

item4 = Items(name= 'WEB', price= '1000$', desc= 'WEb DEVELOPER', category= category2)
session.add(item4)
session.commit()


print("Items are added")
