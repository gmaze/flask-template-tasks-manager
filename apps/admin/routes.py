from flask import (
    render_template,
)
from flask_login import (
    current_user,
    login_required,
)

from apps.admin import blueprint


@blueprint.route('/tasks', methods=['GET'])
@login_required
def admin_tasks():
    if current_user.is_authenticated:
        if current_user.role_level < 100:
            return render_template('home/page-401.html'), 401
        else:
            return render_template('admin/tasks.html')
    else:
        return render_template('home/page-403.html'), 403


@blueprint.route('/users', methods=['GET'])
@login_required
def admin_users():
    if current_user.is_authenticated:
        if current_user.role_level < 100:
            return render_template('home/page-401.html'), 401
        else:
            return render_template('admin/users.html')
    else:
        return render_template('home/page-403.html'), 403


@blueprint.route('/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    if current_user.is_authenticated:
        if current_user.role_level < 100:
            return render_template('home/page-401.html'), 401
        else:
            return render_template('admin/dashboard.html')
    else:
        return render_template('home/page-403.html'), 403


