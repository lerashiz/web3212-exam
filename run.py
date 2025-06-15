from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
from flask_migrate import upgrade
import os
from flask import redirect, url_for

app = create_app()

@app.before_request
def initialize():
    # Выполнить миграции
    upgrade()

    # Создать админа при первом запуске, если его нет
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin', password_hash=generate_password_hash('admin123'), role='admin')
        db.session.add(user)
        db.session.commit()
        print("✅ Создан пользователь admin / admin123")

@app.route('/')
def home():
    return redirect(url_for('equipment.list_equipment'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
