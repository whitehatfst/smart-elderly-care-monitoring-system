import os
import datetime

from app import app, db, socketio
from app.mod_user.models import User
from app.runtime_support import ensure_directory, md5_text, SQLITE_DB_PATH

DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_EMAIL = 'admin@example.com'
# 仅用于本地演示，可通过环境变量 DEFAULT_ADMIN_PASSWORD 覆盖
DEFAULT_ADMIN_PASSWORD = os.environ.get('DEFAULT_ADMIN_PASSWORD', '123abc')
LEGACY_ADMIN_EMAILS = {'', None, 'admin@test.com'}
LEGACY_ADMIN_PASSWORD_HASHES = {md5_text('123'), md5_text(DEFAULT_ADMIN_PASSWORD)}


def ensure_default_admin():
    admin_user = User.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first()
    default_email_user = User.query.filter_by(email=DEFAULT_ADMIN_EMAIL).first()

    if admin_user is None and default_email_user is None:
        admin = User(
            username=DEFAULT_ADMIN_USERNAME,
            real_name='管理员',
            email=DEFAULT_ADMIN_EMAIL,
            password=md5_text(DEFAULT_ADMIN_PASSWORD),
            isactive='1',
            theme='default',
            created=datetime.datetime.now(),
        )
        db.session.add(admin)
        db.session.commit()
        return

    if admin_user is None:
        return

    updated = False
    if not admin_user.real_name:
        admin_user.real_name = '管理员'
        updated = True
    if not admin_user.isactive:
        admin_user.isactive = '1'
        updated = True
    if not admin_user.theme:
        admin_user.theme = 'default'
        updated = True

    # Migrate the untouched legacy admin account to the documented default credentials.
    if (
        admin_user.email in LEGACY_ADMIN_EMAILS
        and admin_user.password in LEGACY_ADMIN_PASSWORD_HASHES
        and (default_email_user is None or default_email_user.id == admin_user.id)
    ):
        admin_user.email = DEFAULT_ADMIN_EMAIL
        admin_user.password = md5_text(DEFAULT_ADMIN_PASSWORD)
        updated = True

    if updated:
        db.session.commit()


def initialize_database():
    ensure_directory(SQLITE_DB_PATH.parent)
    with app.app_context():
        db.create_all()
        ensure_default_admin()


initialize_database()
socketio.run(app, host='127.0.0.1', debug=False, port=5000)



