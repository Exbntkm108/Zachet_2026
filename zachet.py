from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Volunteer
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///volunteers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret-key-for-flashes'  # Нужен для вывода сообщений об успехе

db.init_app(app)

# Создаем таблицы при первом запуске
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    # Получаем всех волонтеров, сортируя по убыванию количества занятий
    volunteers = Volunteer.query.order_by(Volunteer.total_sessions.desc()).all()

    # Считаем общую статистику
    total_volunteers = len(volunteers)
    total_sessions = sum(v.total_sessions for v in volunteers)

    return render_template('index.html',
                           volunteers=volunteers,
                           total_volunteers=total_volunteers,
                           total_sessions=total_sessions)


@app.route('/add', methods=['GET', 'POST'])
def add_volunteer():
    if request.method == 'POST':
        name = request.form['name']
        city = request.form['city']

        new_volunteer = Volunteer(name=name, city=city)
        db.session.add(new_volunteer)
        db.session.commit()

        flash(f'Волонтёр {name} успешно добавлен!', 'success')
        return redirect(url_for('index'))

    return render_template('add_volunteer.html')


@app.route('/log/<int:vol_id>', methods=['GET', 'POST'])
def log_session(vol_id):
    volunteer = Volunteer.query.get_or_404(vol_id)

    if request.method == 'POST':
        try:
            sessions_added = int(request.form['sessions'])
            if sessions_added <= 0:
                raise ValueError

            volunteer.total_sessions += sessions_added

            # Здесь можно добавить запись в отдельную таблицу History,
            # если нужно хранить историю по неделям/дням

            db.session.commit()
            flash(f'Активность обновлена! У {volunteer.name} теперь {volunteer.total_sessions} занятий.', 'info')
            return redirect(url_for('index'))
        except ValueError:
            flash('Введите корректное положительное число занятий.', 'danger')

    return render_template('log_session.html', volunteer=volunteer)


if __name__ == '__main__':
    app.run(debug=True)