from flask import g, redirect, url_for, flash


class AccessMixin:

    def is_accessible(self):
        if g.user:
            return g.user.is_admin
        return False

    def inaccessible_callback(self, name, **kwargs):
        if g.user:
            flash("Нет доступа в админку.", "danger")
            return redirect(url_for('blog.index'))
        return redirect(url_for('auth.login'))
