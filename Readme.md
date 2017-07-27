# Item catalog
Item catalog is a python-flask based web application that provides the user with ability to read, write, update, delete an item from the database.

# Getting Started

## Requirements

- Must have Python installed on system
- Must have SqlAlchemy (Python's External Lib) installed on system
- Must have Flask (Python's External Lib) installed on system
- Must have Vagrant Installed on system

### How to Install SQLAlchemy and Flask Framework

- Copy & paste below commands one by one to terminal to install **SQLAlchemy**

> pip install sqlalchemy & pip install flask-sqlalchemy

- Copy & Paste below command to terminal to install **Flask**

> pip install flask


**Note :-** 
If you are on Linux & Mac just run above commands with **sudo** Example shown below 
> sudo pip install flask    

If you are on Windows you need **Git Bash** Installed on your system
> [Click Here](https://git-scm.com/download) to download Git Bash


### Steps To Run The Project

1.  Unzip the catalog.zip file
2.  Open terminal & Go to project directory
3.  Run `python db.py` command to create database schema
4.  Run `python lotsofitems.py` command to populate the database
5.  Run `python app.py` to start the server
6.  Finally Now open any browser and type in the following url : `http://localhost:8080`


#### JSON Endpoints

- JSON Endpoint for All Categories http://localhost:8080/categories/json
- JSON Endpoint for Items of a Specific category http://localhost:8080/categories/{category_id_here}/json
- JSON Endpoint for a specific item http://localhost:8080/items/{item_id_here}/json


#### Clone Or Download This Repo At [Item-Catalog](https://github.com/imrshu/Item-Catalog.git)
