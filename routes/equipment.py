from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from app import db
from app.models import Equipment, Category, Image, Maintenance
from app.forms import EquipmentForm, MaintenanceForm
from app.utils import save_file_with_hash

bp = Blueprint('equipment', __name__, url_prefix='/equipment')

UPLOAD_FOLDER = 'static/uploads/'

@bp.route('/')
@login_required
def list_equipment():
    query = Equipment.query
    if request.args.get('category'):
        query = query.filter_by(category_id=request.args['category'])
    if request.args.get('status'):
        query = query.filter_by(status=request.args['status'])
    if request.args.get('start_date') and request.args.get('end_date'):
        start = datetime.strptime(request.args['start_date'], '%Y-%m-%d')
        end = datetime.strptime(request.args['end_date'], '%Y-%m-%d')
        query = query.filter(Equipment.purchase_date.between(start, end))

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Equipment.purchase_date.desc()).paginate(page=page, per_page=10)
    return render_template('index.html', equipment=pagination.items, pagination=pagination, categories=Category.query.all(), active='equipment')

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_equipment():
    if current_user.role != 'admin':
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('equipment.list_equipment'))

    form = EquipmentForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        image_id = None
        if form.image.data:
            file = form.image.data.read()
            filename, mime_type, hash_value = save_file_with_hash(file, form.image.data.filename)
            existing_image = Image.query.filter_by(md5_hash=hash_value).first()
            if not existing_image:
                image = Image(filename=filename, mime_type=mime_type, md5_hash=hash_value)
                db.session.add(image)
                db.session.flush()
                image_id = image.id
            else:
                image_id = existing_image.id

        equipment = Equipment(
            name=form.name.data,
            inventory_number=form.inventory_number.data,
            category_id=form.category.data,
            purchase_date=form.purchase_date.data,
            price=form.price.data,
            status=form.status.data,
            note=form.note.data,
            image_id=image_id
        )
        try:
            db.session.add(equipment)
            db.session.commit()
            flash('Оборудование успешно добавлено.', 'success')
            return redirect(url_for('equipment.view_equipment', id=equipment.id))
        except:
            db.session.rollback()
            flash('Ошибка при сохранении. Проверьте данные.', 'danger')

    return render_template('equipment_form.html', form=form, edit_mode=False, active='equipment')

@bp.route('/<int:id>', methods=['GET', 'POST'])
@login_required
def view_equipment(id):
    equipment = Equipment.query.get_or_404(id)
    form = MaintenanceForm()

    if form.validate_on_submit() and current_user.role in ['admin', 'tech']:
        new_record = Maintenance(
            equipment_id=id,
            date=form.date.data,
            service_type=form.service_type.data,
            comment=form.comment.data
        )
        db.session.add(new_record)
        db.session.commit()
        flash('Запись об обслуживании добавлена.', 'success')
        return redirect(url_for('equipment.view_equipment', id=id))

    return render_template(
        'view_equipment.html',
        equipment=equipment,
        maintenance_history=equipment.maintenance,
        form=form,
        active='equipment'
    )

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_equipment(id):
    equipment = Equipment.query.get_or_404(id)
    if current_user.role != 'admin':
        flash('У вас недостаточно прав.', 'danger')
        return redirect(url_for('equipment.view_equipment', id=id))

    form = EquipmentForm(obj=equipment)
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        equipment.name = form.name.data
        equipment.inventory_number = form.inventory_number.data
        equipment.category_id = form.category.data
        equipment.purchase_date = form.purchase_date.data
        equipment.price = form.price.data
        equipment.status = form.status.data
        equipment.note = form.note.data
        try:
            db.session.commit()
            flash('Данные обновлены.', 'success')
            return redirect(url_for('equipment.view_equipment', id=equipment.id))
        except:
            db.session.rollback()
            flash('Ошибка при обновлении.', 'danger')

    return render_template('equipment_form.html', form=form, edit_mode=True, active='equipment')

@bp.route('/<int:id>/delete')
@login_required
def delete_equipment(id):
    if current_user.role != 'admin':
        flash('Недостаточно прав.', 'danger')
        return redirect(url_for('equipment.list_equipment'))

    equipment = Equipment.query.get_or_404(id)
    try:
        db.session.delete(equipment)
        db.session.commit()
        flash('Оборудование удалено.', 'success')
    except:
        db.session.rollback()
        flash('Ошибка при удалении.', 'danger')

    return redirect(url_for('equipment.list_equipment'))