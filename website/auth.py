from flask import Blueprint, render_template, request, flash, redirect, url_for
import re
from flask_login import login_required, logout_user, current_user
from .models import Usuario, Administrador, Parqueo, Guarda, view_resumen, Vehiculo, view_fallidos, view_aprobacion, view_uso
from . import db
from sqlalchemy import asc
from datetime import datetime

auth = Blueprint('auth', __name__)

# Inicio de sesión y admin

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo') # Obtiene los valores del form
        contra = request.form.get('contrasena')
        return Administrador.loginUsuario(correo, contra)
            
    return render_template("/login.html") # Carga login.html

@auth.route('/registrar-usuarios', methods=['GET', 'POST'])
@login_required
def registrarUsuarios():
    esAdmin()
    if request.method == 'POST': 
        nombre = request.form.get('nombreUsuario') # Obtiene los valores del form
        id = request.form.get('idUsuario')
        correo = request.form.get('correoUsuario')
        nCarne = request.form.get('nCarne')
        fecha = request.form.get('fechaUsuario')
        rol = request.form.get('rol')
        
        match rol:    
            case 'Estudiante':
                return Administrador.registrarUsuario(nombre, id, correo, nCarne, fecha, rol, Usuario)
            
            case 'Personal Administrativo':
                return Administrador.registrarUsuario(nombre, id, correo, nCarne, fecha, rol, Usuario)
            
            case 'Guarda':
                return Administrador.registrarUsuario(nombre, id, correo, nCarne, fecha, rol, Usuario)

    return render_template("admin_usuarios.html") # Carga admin_usuarios.html

@auth.route('/registrar-parqueos', methods=['GET', 'POST'])
@login_required
def registrarParqueos():
    esAdmin()
    if request.method == 'POST':
        nombre = request.form.get('nombreParqueo') # Obtiene los valores del form
        capacidadES = request.form.get('capacidadES')
        capacidadMotos = request.form.get('capacidadMoto')
        capacidadLey = request.form.get('capacidadLey')

        return Administrador.registrarParqueo(nombre, capacidadES, capacidadMotos, capacidadLey)
    
    return render_template("admin_parqueos.html") # Carga admin_parqueos.html

@auth.route('/registrar-vehiculos', methods=['GET', 'POST'])
@login_required
def registrarVehiculos():
    esAdmin()
    if len(request.query_string) > 0:
        placa = request.args.get('placa')
        tipo = request.args.get('tipo')
        dueno = request.args.get('dueno')
        espacio = request.args.get('espacio')
        marca = request.form.get('marcaVehiculo')
        color = request.form.get('colorVehiculo')
        
        return Administrador.registrarVehiculo(marca, tipo, color, dueno, placa, espacio)

    if request.method == 'POST':
        marca = request.form.get('marcaVehiculo') # Obtiene los valores del form
        tipo = request.form.get('tipoVehiculo')
        color = request.form.get('colorVehiculo')
        dueno = request.form.get('duenoVehiculo')
        placa = request.form.get('noPlaca')
        espacio = request.form.get('espacioLey')

        return Administrador.registrarVehiculo(marca, tipo, color, dueno, placa, espacio)
      
    return render_template("admin_vehiculos.html",  usuario= Usuario.query.all()) # Carga admin_vehículos.html y pasa la variable usuario para utilizarla en el archivo .html

@auth.route('/ingresos-fallidos', methods=['GET', 'POST'])
@login_required
def ingresosFallidos():
    esAdmin()
    fecha = request.form.get('filtrarFecha')
    reporte = view_fallidos.query.all()
    fechas = []
    existe = False
    if request.method == 'POST':
        fecha = request.form.get('filtrarFecha')
        for r in reporte:
            matches = datetime.date(r.fecha)
            if str(matches) == fecha:
                existe = True
                fechas.append([r.id_placa, r.fecha])
            elif len(fechas) < 0:
                existe = False
                break

        if not existe:
            flash("No se encontraron registros en esa fecha", category='error')
        return render_template('admin_fallidos.html', reporte = reporte, fecha = fecha, reporteFechas = fechas, existe = existe)
    return render_template('admin_fallidos.html', reporte = reporte, fecha = fecha, reporteFechas = fechas, existe = existe)


@auth.route('/reporte-ocupacion', methods=['GET', 'POST'])
@login_required
def reporteOcupacionAdmin():
    esAdmin()
    return render_template('admin_ocupacion.html', reporte = view_resumen.query.all())

@auth.route('/vehiculos-aprobacion', methods=['GET', 'POST'])
@login_required
def vehiculosAprobacion():
    esAdmin()
    mes = request.form.get('filtrarMes')
    reporte = view_aprobacion.query.all()
    fechas = []
    existe = False
    if request.method == 'POST':
        if request.form['btnAprobar'] == 'filtrar':       
            mes = request.form.get('filtrarMes')
            for r in reporte:
                matches = datetime.date(r.fecha)
                if str(matches.month) == mes:
                    existe = True
                    fechas.append([r.id_placa, r.fecha, r.id_usuario])
                elif len(fechas) < 0:
                    existe = False
                    break
            if mes == None or not existe and int(mes) != 0:
                flash("No se encontraron registros en esa fecha", category='error')
            return render_template('admin_aprobacion.html', reporte = reporte, reporteFechas = fechas, existe = existe, mes = mes)

        else: 
             boton = request.form.get('btnAprobar')
             vehiculo = view_aprobacion.query.filter_by(id_placa = boton).first()
             flash("Para completar aprobación ingrese marca y color", category='warning')
             return redirect(url_for('auth.registrarVehiculos',tipo=vehiculo.tipo , dueno= str(vehiculo.id_usuario), placa = vehiculo.id_placa, espacio=vehiculo.espacio))
    
    return render_template('admin_aprobacion.html', reporte = reporte, reporteFechas = fechas, existe = existe, mes = mes)

@auth.route('/cambio', methods=['GET', 'POST'])
@login_required
def cambioLogin():
    if current_user.contra != 'Ulacit123':
        flash('Acceso denegado', category='error')
        return redirect(url_for('auth.logout'))
    if request.method == 'POST':
        nuevaContra = request.form.get('cambioContrasena') # Obtiene los valores del form
        contra = request.form.get('confirmarContrasena')
        id = current_user.id
        if len(nuevaContra) < 5:
            flash('La contraseña debe de ser mayor a 5 caracteres', category='error')
        elif nuevaContra == 'Ulacit123':
            flash('Elija otra contraseña', category='error')
        elif not re.search(r'^(?=[^A-Z]*[A-Z])(?=[^0-9]*[0-9])', nuevaContra):
            flash('La contraseña debe contener números y mayúsculas',  category='error')   
        else:
            if nuevaContra == contra: # Verifica que las contraseñas sean iguales
                usuario = Usuario.query.filter_by(id=id).first() # Obtiene el usuario 
                usuario.contra = nuevaContra # Se hace un UPDATE de la contrasena 
                db.session.commit() # Hace un commit a la base de datos para guardar el cambio
                return redirect(url_for('auth.login')) # Redirige a la pantalla de login 
            else:
                flash('Las contraseñas no son iguales', category='error')
        
    return render_template("cambioContra.html") # Carga cambioContra.html

@auth.route('/logout') # Cierra sesión del usuario actual
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login')) # Redirige a la pantalla de login 

def esAdmin():
    if current_user.rol != 1:
        flash('Acceso denegado', category='error')
        return redirect(url_for('auth.logout'))

# Guardas

@auth.route('/vigilar-parqueo')
@login_required
def inicioParqueo():
    esGuarda()
    return render_template('guarda_inicio.html', parqueo = Parqueo.query.order_by(asc(Parqueo.id)))

@auth.route('/ingreso-al-parqueo/<nombre>&<id>', methods=['GET', 'POST'])
@login_required
def ingresoParqueo(nombre, id):
    esGuarda()
    if request.method == 'POST':
        placa = request.form.get('placaVehiculo')
        cedula = request.form.get('cedulaUsuario')
        tipo = request.form.get('tipoVehiculo')
        ley = request.form.get('espacioLey')

        return Guarda.ingresarPlaca(nombre, id, placa, cedula, tipo, ley)
    
    return render_template('guarda_ingresos.html', nombre = nombre, id = id)

@auth.route('/egreso-parqueo/<nombre>&<id>', methods=['GET', 'POST'])
@login_required
def egresoParqueo(nombre, id):
    esGuarda()
    if request.method == 'POST':
        placa = request.form.get('placaVehiculo')
        return Guarda.egresoVehiculos(nombre, id, placa)
    return render_template('guarda_egresos.html', nombre = nombre, id = id)

@auth.route('/reporte-ocupacion/<nombre>&<id>')
@login_required
def reporteOcupacion(nombre, id):
    esGuarda()
    return render_template('guarda_reportes.html', nombre = nombre, id = id, reporte = view_resumen.query.filter_by(id_parqueo = id).all(), parqueo = Parqueo.query.filter_by(id = id).first())

def esGuarda():
    if current_user.rol != 2:
        flash('Acceso denegado', category='error')
        return redirect(url_for('auth.logout'))
    

# Estudiantes / Personal administrativo 
@auth.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol == 3:  # Estudiante
        return render_template('estudiante_inicio.html')
    elif current_user.rol == 4:  # Personal Administrativo
        return render_template('personal_inicio.html')
    else:
        flash('Acceso denegado', category='error')
        return redirect(url_for('auth.logout'))

@auth.route('/vehiculo-estatus')
@login_required
def vehiculo_estatus():
    if current_user.rol in [3, 4]:  # Rol 3 para Estudiantes y 4 para Personal Administrativo
        vehiculos = Vehiculo.query.filter_by(id_usuario=current_user.id).all()
        fallidos = view_aprobacion.query.filter_by(id_usuario = current_user.id).all()
        return render_template('vehiculo_estatus.html', vehiculos=vehiculos, ingresosFallidos = fallidos )
    else:
        flash('Acceso denegado', category='error')
        return redirect(url_for('auth.logout'))

@auth.route("/uso-del-parqueo")
@login_required
def usoParqueo():
    mes = datetime.now().month
    reporte = view_uso.query.filter_by(id_usuario = current_user.id).all()
    if current_user.rol in [3, 4]:  

        return render_template('uso_parqueo.html', reporte = reporte, mes = mes)
    else:
        flash('Acceso denegado', category='error')
        return redirect(url_for('auth.logout'))