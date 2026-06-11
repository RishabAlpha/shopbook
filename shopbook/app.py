from flask import Flask, render_template , request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from datetime import date

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


@app.route('/customers/add', methods=['GET','POST'])
def add_customer():
    if request.method == "POST":
        c_name = request.form.get('name')
        c_phone = request.form.get('phone')

        new_customer = Customer(name=c_name, phone=c_phone)
        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for('dashboard'))
    return render_template('customers_add.html')

@app.route('/customers')
def list_customers():
    all_customers = Customer.query.all()
    return render_template('customers_list.html', customers=all_customers)

@app.route('/customers/<int:customer_id>')
def view_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    return render_template('customer_view.html', customer=customer)

@app.route('/bills')
def list_bills():
    all_bills = Bill.query.all()
    return render_template('bills_list.html',bills=all_bills)

@app.route('/bills/new', methods=['GET','POST'])
def new_bill():
    if request.method == 'POST':
        # 1. Capture Form Inputs
        cust_id = int(request.form.get('customer_id'))

        # Capture lists of inputs sent from the dynamic rows
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')

        # 2. First, calculate the total invoice cost on the backend for safety
        calculated_grand_total = 0.0
        items_to_save = []

        for i in range(len(product_ids)):
            p_id = int(product_ids[i])
            qty = int(quantities[i])

            # Fetch the product from database to get official price
            product = Product.query.get(p_id)
            row_price = product.unit_price * qty 
            calculated_grand_total += row_price

            # Temporarily stage our item data structure
            items_to_save.append({
                'product_id': p_id,
                'qty': qty,
                'price': product.unit_price,
                'total': row_price
            })

        # 3. Create and Save the Parent Bill Entry
        new_invoice = Bill(
            customer_id=cust_id,
            date=date.today(),
            total_amount=calculated_grand_total
        )

        db.session.add(new_invoice)
        db.session.flush() #This stages the invoice and generates its unique ID without committing yet

        customer_row = Customer.query.get(cust_id)

        customer_row.balance_due += calculated_grand_total

        # 4. Create and Save each BillItem line item mapped to the new Invoice ID
        for item in items_to_save:
            line_item = BillItem(
                bill_id=new_invoice.id,
                product_id=item['product_id'],
                quantity=item['qty'],
                unit_price=item['price'],
                total_price=item['total']
            )
            # Stage this line_item into the database session
            db.session.add(line_item)
            db.session.flush()
        # Permanently commit all staged database changes (Bill & BillItems)
        db.session.commit()

        return redirect(url_for('list_bills'))

    customers = Customer.query.all()
    products = Product.query.all()

    return render_template('bills_new.html', customers=customers, products=products)

if __name__ == '__main__':
    app.run(debug=True)
