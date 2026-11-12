from pathlib import Path
from flask import Flask
from config import Config
from .database import init_db, close_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    from .routes import main
    app.register_blueprint(main)
    return app
