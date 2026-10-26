# Statement for enabling the development environment,
# 引用方式: app.config.from_object('config'), config.py里面的 key必须是大写的,
#很多地方就不用写配置了, 比如debug=True, SECRET_KEY等,系统自动从下面取值
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - default to a local SQLite file for Windows deployment
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "clouddata.db")
DATABASE_CONNECT_OPTIONS = {"check_same_thread": False}

if not SQLALCHEMY_DATABASE_URI.startswith("sqlite:///"):
    SQLALCHEMY_POOL_SIZE = 50
    SQLALCHEMY_POOL_TIMEOUT = 15
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_MAX_OVERFLOW = 60

SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_ECHO = False

THREADS_PER_PAGE = 4

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
# 请通过环境变量注入，切勿把真实密钥提交到仓库
CSRF_SESSION_KEY = os.environ.get("CSRF_SESSION_KEY", "dev-csrf-key-please-change")

# Secret key for signing cookies
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-please-change")

JSON_AS_ASCII = False

# Json config
#app_path = os.path.realpath(os.path.dirname(__file__))
JSON_CONFIG_PATH = os.path.join(BASE_DIR, "app", "data", "appconfig.json")

