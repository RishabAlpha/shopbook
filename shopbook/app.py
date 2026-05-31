from flask import Flask, render_template , request, redirect, url_for
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


@app.route('/')
def dashboard():
    total_cust = Customer.query.count()
    total_prod = Product.query.count()

    return render_template('dashboard.html', customer_count=total_cust, product_count=total_prod)

@app.route('/products/add', methods=['GET','POST'])
def add_product():
    if request.method == "POST":
        p_name = request.form.get('name')
        p_price = float(request.form.get('unit_price'))
        p_stock = int(request.form.get('stock_quantity'))

        new_product = Product(name=p_name, unit_price=p_price, stock_quantity=p_stock)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('dashboard'))
        
    return render_template('products_add.html')

@app.route('/products')
def list_products():
    all_products = Product.query.all()

    return render_template('products_list.html',products=all_products)



if __name__ == '__main__':
    app.run(debug=True)
