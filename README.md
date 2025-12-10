#create environment in your system
py -3 -m venv .venv

#active the environment
.venv\Scripts\activate

#download 
pip install flask,flask_sqlalchemy,pycache

#first install xampp then create a database name "drivex" (then import the database from the project folder) or in the terminal type the cmd:
1.python
2.from app import app
3.from app import db
4.db.create_all()

#Now Enjoy my Project