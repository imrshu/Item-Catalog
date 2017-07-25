from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Creating an instance of declarative_base
Base = declarative_base()


class Category(Base):
    ''' This class shows all categories in the database '''

    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)

    name = Column(String(80), nullable=False)


class Items(Base):
    ''' This class shows items related to each category '''

    __tablename__ = 'menuitems'

    id = Column(Integer, primary_key=True)

    name = Column(String(80), nullable=False)

    price = Column(String)

    desc = Column(String)

    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship(Category)


# Connecting to the database

engine = create_engine('sqlite:///catalog.db')

# Bind engine to Base
Base.metadata.create_all(engine)
