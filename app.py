from flask import Flask, render_template, request, redirect, url_for
from flask import flash
from models import db, User, Property

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
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_user = User.query.filter_by(username=username).first()
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
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            authenticated_user = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    properties = Property.query.filter_by(available=True).all()
    return render_template('dashboard.html', properties=properties)

if __name__ == '__main__':
    app.run(debug=True)
