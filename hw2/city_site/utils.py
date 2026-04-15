from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user
from datetime import datetime, timedelta

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        # Проверка бана для администратора – если забанен, тоже не пускаем
        if not current_user.is_active():
            flash('Ваш аккаунт заблокирован.', 'danger')
            return redirect(url_for('logout'))
        return f(*args, **kwargs)
    return decorated_function

def calculate_ban_until(duration):
    if duration == 'day':
        return datetime.utcnow() + timedelta(days=1)
    elif duration == 'week':
        return datetime.utcnow() + timedelta(weeks=1)
    elif duration == 'month':
        return datetime.utcnow() + timedelta(days=30)
    else:  # forever
        return None