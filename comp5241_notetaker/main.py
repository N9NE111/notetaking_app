from flask import Flask, render_template_string
from src.database import db
from src.models.note import Note
from src.routes.note import note_bp
import os

def create_app():
    app = Flask(__name__, static_folder='src/static', template_folder='src/static')
    
    os.makedirs('database', exist_ok=True)
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'local-notetaker-app-2024'
    
    db.init_app(app)
    
    app.register_blueprint(note_bp, url_prefix='/api/notes')
    
    @app.route('/')
    def index():
        with open('src/static/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    with app.app_context():
        db.create_all()
        print("Database tables checked!")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
