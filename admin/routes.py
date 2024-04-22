from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from .forms import PropertyForm
from ..models import Property
from .. import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/properties')
@login_required
def list_properties():
    properties = Property.query.all()
    return render_template('admin/property_list.html', properties=properties)

@admin_bp.route('/properties/<int:property_id>')
@login_required
def view_property(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('admin/property_detail.html', property=property)

@admin_bp.route('/properties/create', methods=['GET', 'POST'])
@login_required
def create_property():
    form = PropertyForm()
    if form.validate_on_submit():
        property = Property(name=form.name.data, location=form.location.data, price=form.price.data)
        db.session.add(property)
        db.session.commit()
        flash('Property created successfully!', 'success')
        return redirect(url_for('admin.list_properties'))
    return render_template('admin/property_form.html', form=form, title='Create Property')

@admin_bp.route('/properties/<int:property_id>/update', methods=['GET', 'POST'])
@login_required
def update_property(property_id):
    property = Property.query.get_or_404(property_id)
    form = PropertyForm()
    if form.validate_on_submit():
        property.name = form.name.data
        property.location = form.location.data
        property.price = form.price.data
        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect(url_for('admin.list_properties'))
    elif request.method == 'GET':
        form.name.data = property.name
        form.location.data = property.location
        form.price.data = property.price
    return render_template('admin/property_form.html', form=form, title='Update Property')

@admin_bp.route('/properties/<int:property_id>/delete', methods=['POST'])
@login_required
def delete_property(property_id):
    property = Property.query.get_or_404(property_id)
    db.session.delete(property)
    db.session.commit()
    flash('Property deleted successfully!', 'success')
    return redirect(url_for('admin.list_properties'))
