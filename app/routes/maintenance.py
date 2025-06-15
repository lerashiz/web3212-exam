from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models import Maintenance
from app import db

bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@bp.route('/')
@login_required
def index():
    if current_user.role not in ['admin', 'tech']:
        flash('У вас недостаточно прав для доступа к этой странице.', 'danger')
        return redirect(url_for('equipment.list_equipment'))

    maintenance_records = Maintenance.query.order_by(Maintenance.date.desc()).all()
    return render_template('maintenance_index.html', maintenance_records=maintenance_records, active='service')