from app import create_app, db
from app.models import User, Category, Equipment, Maintenance, Disposal, Image
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import os
from app.utils import generate_disposal_pdf

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # --- Пользователи ---
    users = [
        User(username='admin', password_hash=generate_password_hash('admin123'), role='admin'),
        User(username='tech', password_hash=generate_password_hash('tech123'), role='tech'),
        User(username='user', password_hash=generate_password_hash('user123'), role='user')
    ]
    db.session.add_all(users)

    # --- Категории и изображения ---
    category_map = {
        'Компьютеры': 'computer.jpg',
        'Принтеры': 'printer.jpg',
        'Сканеры': 'scanner.jpg'
    }

    categories = []
    image_ids = {}

    for name, filename in category_map.items():
        category = Category(name=name, description=f'{name} офисные')
        db.session.add(category)
        db.session.flush()

        image = Image(
            filename=filename,
            mime_type='image/jpeg',
            md5_hash=f'seed-{filename}'
        )
        db.session.add(image)
        db.session.flush()

        categories.append(category)
        image_ids[category.id] = image.id

    # --- Генерация оборудования ---
    equipment_list = []
    counters = {'Компьютеры': 1, 'Принтеры': 1, 'Сканеры': 1}

    for i in range(15):
        category = random.choice(categories)
        base = category.name.rstrip('ы')
        number = counters[category.name]
        counters[category.name] += 1

        name = f"{base} №{number}"
        status = random.choice(['active', 'repair', 'disposed'])

        eq = Equipment(
            name=name,
            inventory_number=f"INV-{1000 + i}",
            category_id=category.id,
            purchase_date=datetime.today() - timedelta(days=random.randint(100, 2000)),
            price=round(random.uniform(5000, 50000), 2),
            status=status,
            note="Автоматически сгенерировано",
            image_id=image_ids[category.id]
        )
        db.session.add(eq)
        equipment_list.append(eq)
    db.session.flush()

    # --- Обслуживание ---
   
    service_types = ['Диагностика', 'Чистка', 'Обновление ПО', 'Замена комплектующих', 'Профилактика']
    for eq in equipment_list:
    # Прошедшие обслуживания
        for _ in range(random.randint(1, 5)):
            # Генерируем случайное количество дней от 0 до 600
            days_ago = random.randint(0, 600)
            # Вычисляем дату обслуживания
            maintenance_date = datetime.today() - timedelta(days=days_ago)
        
        # Добавляем запись о обслуживании
            db.session.add(Maintenance(
                equipment_id=eq.id,
                date=maintenance_date,
                service_type=random.choice(service_types),
                comment=random.choice([
                    'Выполнено техником',
                    'Замена термопасты',
                    'Очистка от пыли',
                    'Обновление драйверов',
                    'Проверка на вирусы',
                    'Калибровка оборудования'
                ])
            ))
        
        # Ближайшие плановые обслуживания
            if random.random() > 0.3:  
                db.session.add(Maintenance(
                    equipment_id=eq.id,
                    date=datetime.today() + timedelta(days=random.randint(1, 60)),
                    service_type='Плановое ТО',
                    comment='Запланировано'
                ))

    # --- Списание с генерацией PDF ---
    for eq in equipment_list:
        if eq.status == 'disposed':
            pdf_name = f"disposal_{eq.inventory_number}.pdf"
            generate_disposal_pdf(pdf_name, eq.name, "Износ оборудования")
            db.session.add(Disposal(
                equipment_id=eq.id,
                reason='Износ оборудования',
                pdf_filename=pdf_name,
                disposal_date=datetime.today() - timedelta(days=random.randint(1, 300))
            ))

    db.session.commit()