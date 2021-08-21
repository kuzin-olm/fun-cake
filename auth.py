import functools
import uuid

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.models import db, User

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         error = None
#
#         if not username:
#             error = 'Введите имя пользователя.'
#         elif not password:
#             error = 'Введите пароль.'
#         elif User.query.filter_by(name=username).one_or_none() is not None:
#             error = f"Пользователь {username} уже зарегестрирован."
#
#         if error is None:
#             # TODO мэйби генерить уид только при логине? а при логауте удалять - надежность там все дела
#             user_uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, username).hex)
#             user = User(name=username, pswd=generate_password_hash(password), uid=user_uid)
#             db.session.add(user)
#             db.session.commit()
#             return redirect(url_for('auth.login'))
#
#         flash(error)
#
#     return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None
        user = User.query.filter_by(name=username).one_or_none()

        if user is None:
            error = 'Не верное имя пользователя.'
        elif not check_password_hash(user.pswd, password):
            error = 'Не верный пароль.'

        if error is None:
            session.clear()
            session['user_id'] = user.uid
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(uid=user_id).one_or_none()


@bp.route('/logout')
def logout():
    session.clear()
    # return redirect(url_for('index'))
    return redirect(request.referrer)
