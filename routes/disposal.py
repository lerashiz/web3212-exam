from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from app import db
from app.models import Equipment, Disposal
from app.forms import DisposalForm
from app.utils import save_file_with_hash

bp = Blueprint('disposal', __name__, url_prefix='/disposal')

DISPOSAL_FOLDER = 'static/disposals/'

@bp.route('/')
@login_required
def disposal_report():
    if current_user.role != 'admin':
        flash('У вас недостаточно прав для просмотра отчёта.', 'danger')
        return redirect(url_for('equipment.list_equipment'))

    disposals = Disposal.query.join(Equipment).order_by(Disposal.disposal_date.desc()).all()
    return render_template('disposal_report.html', disposals=disposals, active='disposal')

@bp.route('/<int:id>', methods=['GET', 'POST'])
@login_required
def dispose_equipment(id):
    if current_user.role != 'admin':
        flash('Недостаточно прав для списания оборудования.', 'danger')
        return redirect(url_for('equipment.view_equipment', id=id))

    equipment = Equipment.query.get_or_404(id)
    form = DisposalForm()

    if form.validate_on_submit():
        if form.attachment.data:
            file = form.attachment.data.read()
            filename, mime_type, hash_value = save_file_with_hash(file, form.attachment.data.filename, folder=DISPOSAL_FOLDER)

            disposal = Disposal(
                equipment_id=id,
                reason=form.reason.data,
                pdf_filename=filename,
                disposal_date=datetime.utcnow()
            )
            equipment.status = 'disposed'
            try:
                db.session.add(disposal)
                db.session.commit()
                flash('Оборудование успешно списано.', 'success')
                return redirect(url_for('disposal.disposal_report'))
            except:
                db.session.rollback()
                flash('Ошибка при списании оборудования.', 'danger')

    return render_template('disposal_page.html', form=form, equipment=equipment, active='disposal')