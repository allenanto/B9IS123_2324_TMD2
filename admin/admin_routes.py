from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from . import admin_bp
from .admin_models import Admin

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('admin_login.html')

@admin_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')
