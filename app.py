
# Some helps were taken using OpenAI for finding correct syntaxes and implemented as per the application needs

from flask import Flask, render_template, request, redirect, url_for
from flask import flash, session
from flask_mail import Mail, Message
from models import db, User, Property, Admin
from flask_login import logout_user
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# import jsonify

app = Flask(__name__, static_url_path='/static')
app.secret_key = Config.SECRET

# Configure Appliation and mail setup
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
app.config['MAIL_SERVER'] = Config.MAIL_SERVER
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = Config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = Config.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
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
        email = request.form['email']
        password = request.form['password']
        confirm_pass = request.form['confirm_password']
        hashed_password = generate_password_hash(password)

        existing_user = User.query.filter_by(username=username).first()
        if not email or not username or not password or not confirm_pass:
            flash('All fields are required.', 'error')
            return redirect(request.url)
        if password != confirm_pass:
            flash('Passwords doesnt match', 'error')
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
        if not property.available:
            flash('Property is already booked.')
            return redirect(url_for('index'))

        booking_code = str(uuid.uuid4())
        recipient = User.query.filter_by(username=authenticated_user).first_or_404()

        print(recipient.email)

        subject = 'REMIS'
        message = 'This is your Booking Code \n\n' + booking_code
        msg = Message(subject, sender=Config.MAIL_USERNAME, recipients=[recipient.email])
        msg.body = message
        mail.send(msg)

        # Update property status
        property.available = False
        db.session.commit()

        flash(f'Booking successful! Your booking code is {booking_code}.')
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
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        existing_admin = Admin.query.filter_by(username=username).first()
        
        if not username or not email or not password:
            flash('All fields are required', 'error')

        elif existing_admin:
            flash('Username already exists. Please choose a different one.', 'error')

        elif password != confirm_password:
            flash('Password missmatch', 'error')

        else:
            new_admin = Admin(username=username, email=email, password=password)
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

@app.route('/admin/logout')
def admin_logout():
    global admin
    admin = None
    return redirect('/admin/login')

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
