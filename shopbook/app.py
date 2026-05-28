from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
import os 

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shopbook.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app)

# ====================
# DATABASE MODELS
# ====================

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    unit_price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(120))
    stock_quantity = db.Column(db.Integer,nullable=False,default=0)
    low_stock_threshold = db.Column(db.Integer,default=5)

class Customer(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String)
    balance_due = db.Column(db.Float,default=0)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    customer_id = db.Column(db.Integer,db.ForeignKey('customer.id'), nullable=False)
    date = db.Column(db.Date,nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

class BillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    bill_id = db.Column(db.Integer,db.ForeignKey('bill.id'),nullable=False)
    product_id = db.Column(db.Integer,db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float,nullable=False)
    total_price = db.Column(db.Float, nullable=False)

if __name__ == '__main__':
    app.run(debug=True)
