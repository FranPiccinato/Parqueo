from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .database_schema import user, DB_NAME, password, server


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Grupo6'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@{server}:5432/{DB_NAME}' 
    
    db.init_app(app) # Inicialización de la base de datos

    from .views import views # Registrar los Blueprints 
    from .auth import auth
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import Usuario, Rol

    with app.app_context(): 
      db.create_all() # Crea las tablas de la base de datos sino existen
      
      
      if Rol.query.count() == 0:
        roles = [
            Rol(id=1, tipo='Administrador'),
            Rol(id=2, tipo='Guarda'),
            Rol(id=3, tipo='Estudiante'),
            Rol(id=4, tipo='Personal Administrativo')
        ]
        db.session.bulk_save_objects(roles)
        db.session.commit()
    
      if Usuario.query.count() == 0:
        admin = Usuario(id=1, nombre="Admin", correo="admin@ulacit.ed.cr", fecha='2024-01-01', contra='AdminUlacit12', rol=1)
        db.session.add(admin)
        db.session.commit() 

    login_manager = LoginManager() # Gestor de inicio de sesión
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Inicie sesión primero'
    login_manager.init_app(app)

    @login_manager.user_loader # Carga el usuario
    def load_user(id):
        return Usuario.query.get(int(id))

    return app
