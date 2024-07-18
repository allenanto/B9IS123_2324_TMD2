from flask import Flask, render_template, request, redirect, url_for
from flask import flash, session
from models import db, User, Property, Admin
from flask_login import logout_user
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
# import jsonify

app = Flask(__name__, static_url_path='/static')
app.secret_key = Config.SECRET

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

#for handling sessions and users
authenticated_user = None
admin = None

@app.route('/')
def index():
    if authenticated_user:
        properties = Property.query.all()
        return render_template('index.html', properties=properties)
    else:
        return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_password = generate_password_hash(password)

        existing_user = User.query.filter_by(username=username).first()
        if not email or not username or not password:
            flash('All fields are required.', 'error')
            return redirect(request.url)
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
        else:
            new_user = User(username=username, password=hashed_password, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now login.', 'success')
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global authenticated_user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Both username and password are required.', 'error')
            return redirect(request.url)
            
        user = User.query.filter_by(username=username).first_or_404()

        if user:
            #TODO
            # user_dict = jsonify(user.to_dict())
            # print(user_dict)
            # if check_password_hash(user_dict["password"],password):
                authenticated_user = username
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    global authenticated_user
    authenticated_user = None
    return redirect('/login')

@app.route('/book/<int:property_id>', methods=['POST'])
def book_property(property_id):
    global authenticated_user
    if authenticated_user:
        property = Property.query.get_or_404(property_id)
        property.available = False
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return redirect("/login")

@app.route('/admin')
def admin_index():
    global admin
    if admin:
        return redirect("/admin/dashboard")
    else:
        return redirect('/admin/login')

@app.route('/admin/register', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            flash('Username already exists. Please choose a different one.', 'error')

        new_admin = Admin(username=username, password=password)
        db.session.add(new_admin)
        db.session.commit()

        flash('Admin registration successful! You can now login.', 'success')
        return redirect('/admin/login')

    return render_template('register_admin.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    global admin
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.password == password:
            session['admin_logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect('/admin/dashboard')
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login_admin.html')

# from functools import wraps

# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not session.get('admin_logged_in'):
#             return redirect(url_for('admin_login'))
#         return f(*args, **kwargs)
#     return decorated_function

@app.route('/admin/dashboard')
def admin_dashboard():
    properties = Property.query.all()
    return render_template('dashboard_admin.html', properties=properties)

@app.route('/admin/create_property', methods=['GET', 'POST'])
def create_property():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        price = float(request.form['price'])
        available = request.form.get('available', "False")
        new_property = Property(name=name, description=description, location=location, price=price, available=available)
        db.session.add(new_property)
        db.session.commit()
        flash('Property created successfully!', 'success')
        return redirect('/admin/dashboard')
    return render_template('create_property.html')

@app.route('/admin/update_property/<int:property_id>', methods=['GET', 'POST'])
def update_property(property_id):
    property = Property.query.get_or_404(property_id)
    if request.method == 'POST':
        property.name = request.form['name']
        property.description = request.form['description']
        property.location = request.form['location']
        property.price = float(request.form['price'])
        property.available = request.form.get('available', False)
        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect('/admin/dashboard')
    return render_template('update_property.html', property=property)

@app.route('/admin/delete_property/<int:property_id>')
def delete_property(property_id):
    property = Property.query.get_or_404(property_id)
    db.session.delete(property)
    db.session.commit()
    flash('Property deleted successfully!', 'success')
    return redirect('/admin/dashboard')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
