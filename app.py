from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@localhost/aniswar_ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    manufacturer_name = db.Column(db.String(100))
    inventory_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Product {self.id}>'

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    user_password = db.Column(db.String(100))  # Password should be encrypted in real-world applications
    user_preferences = db.Column(db.String(20))

    def __repr__(self):
        return f'<Product {self.id}>'

class ProductsBought(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    user_name = db.Column(db.String(100))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    date_of_purchase = db.Column(db.Date)

    def __repr__(self):
        return f'<Product {self.id}>'


# Routes

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


# CRUD operations for products
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    output = [{'id': product.product_id, 'name': product.name, 'description': product.description, 'manufacturer_name': product.manufacturer_name, 'inventory_count': product.inventory_count} for product in products]
    return render_template('products.html', products=output)

# CRUD operation for adding a product
@app.route('/add_product', methods=['POST'])
def add_product():
    # Get data from the request
    data = request.json

    # Extract product details
    name = data.get('name')
    description = data.get('description')
    manufacturer_name = data.get('manufacturer_name')
    inventory_count = data.get('inventory_count')

    # Create a new product object
    new_product = Product(name=name, description=description, manufacturer_name=manufacturer_name, inventory_count=inventory_count)

    try:
        # Add the new product to the database session
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully'}), 200
    except Exception as e:
        # Rollback the session if an error occurs
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@app.route('/delete_product/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    else:
        return jsonify({'message': 'Product not found'}), 404

# CRUD operations for users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    output = [{'id': user.user_id, 'user_name': user.user_name, 'user_password': user.user_password, 'user_preferences': user.user_preferences} for user in users]
    return render_template('users.html', users=output)

# CRUD operation for adding a user
@app.route('/add_user', methods=['POST'])
def add_user():
    # Get data from the request
    data = request.json

    # Extract user details
    user_name = data.get('user_name')
    user_password = data.get('user_password')
    user_preferences = data.get('user_preferences')

    # Create a new user object
    new_user = User(user_name=user_name, user_password=user_password, user_preferences=user_preferences)

    try:
        # Add the new user to the database session
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User added successfully'}), 200
    except Exception as e:
        # Rollback the session if an error occurs
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# CRUD operation for deleting a user
@app.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    # Query the database to find the user by ID
    user = User.query.get(id)
    
    if user:
        try:
            # Delete the user from the database session
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'User deleted successfully'}), 200
        except Exception as e:
            # Rollback the session if an error occurs
            db.session.rollback()
            return jsonify({'message': str(e)}), 500
    else:
        # Return 404 if the user is not found
        return jsonify({'message': 'User not found'}), 404


# CRUD operations for products bought
@app.route('/products_bought', methods=['GET'])
def get_products_bought():
    products_bought = ProductsBought.query.all()
    output = [{'id': product_bought.id, 
               'user_id': product_bought.user_id, 
               'product_id': product_bought.product_id, 
               'user_name': product_bought.user_name, 
               'product_name': product_bought.product_name, 
               'quantity': product_bought.quantity, 
               'date_of_purchase': product_bought.date_of_purchase} 
              for product_bought in products_bought]
    users = User.query.all()
    users_output = [{'id': user.user_id, 'user_name': user.user_name} for user in users]
    products = Product.query.all()
    products_output = [{'id': product.product_id, 'name': product.name} for product in products]
    return render_template('productsbought.html', products_bought=output, users = users_output, products = products_output)


from datetime import datetime

@app.route('/add_productsbought', methods=['POST'])
def add_productsbought():
    # Get data from the request
    data = request.json

    # Extract product bought details
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    date_of_purchase = data.get('date_of_purchase')

    try:
        # Fetch the username and product name based on their IDs
        user = User.query.get(user_id)
        product = Product.query.get(product_id)

        if user is None:
            return jsonify({'message': 'User not found'}), 404

        if product is None:
            return jsonify({'message': 'Product not found'}), 404

        if int(quantity) > product.inventory_count:
            return jsonify({'message': 'Quantity exceeds available product quantity'}), 400
        
        product.inventory_count -= int(quantity)

        # Create a new ProductsBought object with username and product name
        new_productsbought = ProductsBought(
            user_id=user_id,
            product_id=product_id,
            user_name=user.user_name,
            product_name=product.name,
            quantity=quantity,
            date_of_purchase=datetime.strptime(date_of_purchase, '%Y-%m-%d')  # Parse date string to datetime object
        )

        # Add the new products bought entry to the database session
        db.session.add(new_productsbought)
        db.session.commit()
        return jsonify({'message': 'Products bought entry added successfully'}), 200
    except Exception as e:
        # Rollback the session if an error occurs
        db.session.rollback()
        return jsonify({'message': str(e)}), 500



@app.route('/delete_products_bought/<int:id>', methods=['DELETE'])
def delete_products_bought(id):
    product_bought = ProductsBought.query.get(id)
    if product_bought:
        product = Product.query.get(product_bought.product_id)
        product.inventory_count += int(product_bought.quantity)

        db.session.delete(product_bought)
        db.session.commit()
        return jsonify({'message': 'Products bought entry deleted successfully'}), 200
    else:
        return jsonify({'message': 'Products bought entry not found'}), 404


# Check if tables exist before creating them
def create_tables_if_not_exist():
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        if 'product' not in existing_tables:
            Product.__table__.create(db.engine)
        if 'user' not in existing_tables:
            User.__table__.create(db.engine)
        if 'products_bought' not in existing_tables:
            ProductsBought.__table__.create(db.engine)

# Create the tables if they don't exist
create_tables_if_not_exist()

if __name__ == '__main__':
    app.run(debug=True)
