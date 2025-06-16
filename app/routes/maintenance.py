from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from app.models import Maintenance, Equipment
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

@bp.route('/calendar')
@login_required
def calendar():
    if current_user.role not in ['admin', 'tech']:
        flash('У вас недостаточно прав для доступа к этой странице.', 'danger')
        return redirect(url_for('equipment.list_equipment'))
    
    return render_template('maintenance_calendar.html', active='service')

@bp.route('/api/events')
@login_required
def get_events():
    events = []
    
    # Реальные события обслуживания
    maintenances = Maintenance.query.join(Equipment).all()
    for m in maintenances:
        events.append({
            'title': f'ТО: {m.equipment.name}',
            'start': m.date.isoformat(),
            'color': '#ffc107',
            'extendedProps': {
                'type': 'completed',
                'equipment': m.equipment.name,
                'service_type': m.service_type,
                'comment': m.comment
            }
        })
    
    # Плановые события (генерируем на основе последних обслуживаний)
    for m in maintenances[-10:]:  # Берем 10 последних обслуживаний для генерации плановых
        next_date = m.date + timedelta(days=180)  # Плановое через 6 месяцев
        if next_date > datetime.now().date():
            events.append({
                'title': f'План: {m.equipment.name}',
                'start': next_date.isoformat(),
                'color': '#28a745',
                'extendedProps': {
                    'type': 'planned',
                    'equipment': m.equipment.name,
                    'service_type': 'Плановое ТО'
                }
            })
    
    return jsonify(events)