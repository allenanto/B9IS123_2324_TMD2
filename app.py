from flask import Flask, render_template, request, redirect, url_for
from flask import flash, session
from models import db, User, Property, Admin
from flask_login import logout_user

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'secret_key'  # Replace with your actual secret key


# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

authenticated_user = None

@app.route('/')
def index():
    if authenticated_user:
        properties = Property.query.all()
        return render_template('index.html', properties=properties)
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_user = User.query.filter_by(username=username).first()
        if not email or username or password:
            flash('All fields are required.', 'error')
            return redirect(request.url)
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
        else:
            new_user = User(username=username, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now login.', 'success')
            return redirect(url_for('login'))
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
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            authenticated_user = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/book/<int:property_id>', methods=['POST'])
def book_property(property_id):
    property = Property.query.get_or_404(property_id)
    property.available = False
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        price = float(request.form['price'])
        # Create a new property entry in the database
        new_property = Property(name=name, description=description, location=location, price=price)
        db.session.add(new_property)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_property.html')

@app.route('/admin/register', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register_admin'))

        new_admin = Admin(username=username, password=password)
        db.session.add(new_admin)
        db.session.commit()

        flash('Admin registration successful! You can now login.', 'success')
        return redirect(url_for('admin_login'))

    return render_template('register_admin.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.password == password:
            session['admin_logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login_admin.html')

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('dashboard_admin.html')


if __name__ == '__main__':
    app.run(debug=True)
