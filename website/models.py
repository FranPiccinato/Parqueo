from . import db
import re
from flask import flash, redirect, url_for, render_template
from sqlalchemy_utils import create_view
from sqlalchemy import select, func, Time
from sqlalchemy.sql import and_, or_, text
from datetime import datetime
from flask_login import UserMixin, login_user # Métodos para manejar la gestión de sesiones y autenticación 


class Usuario(db.Model, UserMixin): # Modelo SQLAlchemy para le estructura de la tabla

    id = db.Column(db.Integer, primary_key=True)
    
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True)
    fecha = db.Column(db.Date, nullable=False)
    contra = db.Column(db.String(150), nullable=False)
    ncarne = db.Column(db.Integer, nullable=True)
    
    vehiculo = db.relationship('Vehiculo')
    vehiculo = db.relationship('Actividad')
    rol = db.Column(db.Integer,  db.ForeignKey('rol.id'), nullable=False)
      
    def loginUsuario(correo, contra):
        usuario = Usuario.query.filter_by(correo=correo.lower()).first() #Obtiene el primer usuario donde el correo sea igual al correo ingresado 
        if usuario: # Si existe
            if usuario.contra == contra:
                if usuario.contra == 'Ulacit123': # Si la contraseña es Ulacit123 redirige a la pantalla de cambio de contraseña
                    login_user(usuario, remember=True)
                    return redirect(url_for('auth.cambioLogin'))
                else:
                    login_user(usuario, remember=True) # Recuerda el usuario que se encuentra ingresado
                    if usuario.rol == 3 or usuario.rol == 4:
                        return redirect(url_for('auth.dashboard'))
                    elif usuario.rol == 1: # Si ingresa un Admin redirige a la pantalla del admin
                        return redirect(url_for('auth.registrarUsuarios'))
                    elif usuario.rol == 2: 
                        return redirect(url_for('auth.inicioParqueo'))
            else:
                flash('Contraseña incorrecta',  category='error')  
        else:
            flash('Usuario incorrecto',  category='error') 
        return render_template("login.html", correo=correo)

class Rol(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)

    usuario = db.relationship('Usuario')

class Administrador(Usuario):

    def registrarUsuario(nombre, id, correo, ncarne, fecha, rol, self):
        existeCarne = None
        existeCorreo = Usuario.query.filter_by(correo=correo).first() 
        existeId = Usuario.query.filter_by(id=id).first()
        
        nAccion = 0
        if ncarne != '':
            existeCarne = Usuario.query.filter_by(ncarne=ncarne).first()
            
        if rol == 'Estudiante':
            rol = 3
        elif rol == 'Guarda':
            rol = 2
        else:
            rol = 4

        if len(nombre) < 1:
            flash('El nombre debe de contener más de 1 carácter.',  category='error')
        elif len(correo) < 4:
            flash('El correo debe de contener más de 4 caracteres.',  category='error')
        elif existeCorreo:
            flash(f'El correo {correo} ya está registrado',  category='error')
        elif existeCarne and rol == 3:
            flash(f'El número de carné {ncarne} ya está registrado',  category='error')
        elif len(ncarne) > 0 and rol != 3:
            flash('El número de carné es solo para el rol Estudiante',  category='error')
        elif existeId:
            flash(f'La identificación {id} ya está registrada',  category='error')
        elif len(id) < 1:
            flash('La cédula no puede quedar vacía',  category='error')
        elif ncarne == '' and rol == 3:
            flash('El número de carné no puede quedar vacío',  category='error')
        elif ncarne == '' and rol != 3:
            ncarne = None
            nAccion = 1
        else:
            nAccion = 1
        if nAccion == 1:
            nuevoUsuario = self(id=id, nombre=nombre, correo=correo.lower(), ncarne=ncarne, fecha= fecha, rol=rol, contra = 'Ulacit123') # Crea un nuevo usuario y pone la contraseña por default
            db.session.add(nuevoUsuario) # Se agrega a la base de datos
            db.session.commit()  # Hace un commit a la base de datos para guardar los datos
            flash('Cuenta creada con éxito.',  category='success')
            return redirect(url_for('auth.registrarUsuarios'))

        return render_template("admin_usuarios.html", id=id, nombre=nombre, correo=correo, ncarne=ncarne, fecha=fecha, rol=rol )

    def registrarParqueo(nombre, capacidad_regulares, capacidad_motos, capacidad_ley):
        existeParqueo= Parqueo.query.filter_by(nombre=nombre).first() 

        if len(nombre) < 2:
            flash('El nombre debe de contener más de 2 caracteres.',  category='error')
        elif existeParqueo:
            flash(f'El parqueo {nombre} ya está registrado',  category='error')
        else:
            nuevoParqueo = Parqueo(nombre=nombre, capacidad_regulares=capacidad_regulares , capacidad_motos=capacidad_motos, capacidad_ley= capacidad_ley) # Crea un nuevo parqueo
            db.session.add(nuevoParqueo)  # Se agrega a la base de datos
            db.session.commit()  # Hace un commit a la base de datos para guardar los datos
            flash('Parqueo creado con éxito.',  category='success')
            return redirect(url_for('auth.registrarParqueos'))

        return render_template("admin_parqueos.html", nombre=nombre, capacidad_regulares=capacidad_regulares , capacidad_motos=capacidad_motos, capacidad_ley= capacidad_ley)

    def registrarVehiculo(marca, tipo, color, dueno, placa, espacio):

        cont = 0
        cantidad = Vehiculo.query.filter_by(id_usuario=dueno)
        existePlaca= Vehiculo.query.filter_by(placa=placa.upper()).first() 

        for c in cantidad:
            cont += 1
        
        ley = False
        if espacio == 'on' or espacio == 'True': 
            ley = True
        else:
            ley = False

        if color == None or len(color) < 2:
            print('Color')
        elif len(placa) < 1:
            flash('La placa debe de contener más de 1 carácter.',  category='error')    
        elif len(placa) > 10:
            flash('La placa puede contener máximo 10 caracteres.',  category='error')
        elif not re.search(r'^(?=[^A-Z]*[A-Z])(?=[^0-9]*[0-9])', placa):
            flash('La placa solo puede contener números y letras',  category='error')      
        elif cont == 2:
             flash('El dueño ya tiene 2 vehículos registrados.',  category='error')   
        elif existePlaca:
             flash(f'La placa {placa} ya se encuentra registrada.',  category='error')  
        else:
            nuevoVehiculo = Vehiculo(marca=marca, tipo=tipo , color=color, placa = placa.upper(), espacio=ley, id_usuario = dueno) # Crea un nuevo vehículo
            db.session.add(nuevoVehiculo) # Se agrega a la base de datos
            db.session.commit() # Hace un commit a la base de datos para guardar los datos
            flash('Vehículo creado con éxito.',  category='success')
    
            return redirect(url_for('auth.registrarVehiculos'))
        return render_template("admin_vehiculos.html", marca=marca, tipo=tipo , color=color, dueno=dueno, placa = placa, espacio=ley, usuario= Usuario.query.all())



class Estudiante(Usuario):

    def verEstatus():
        print("En progreso")

class PersonalAdmin(Usuario):
    def verEstatus():
        print("En progreso")
    

class Guarda(Usuario):
    def ingresarPlaca(nombre, idparqueo, placa, cedula, tipo, ley): 
        vehiculo = Vehiculo.query.filter_by(placa=placa.upper()).first()
        cantidadVehiculos = Vehiculo.query.filter_by(id_usuario=cedula).count()
        usuario = Usuario.query.filter_by(id = cedula).first()
        ultimaEntrada = view_entradas.query.filter_by(id_placa = placa.upper()).first()
        ultimaEntradaFallida = view_fallidos.query.filter_by(id_placa = placa.upper()).first()
        ultimaEntradaUsuario = None
        ultimaFallidaUsuario = view_entradas.query.filter_by(id_usuario = cedula).first()
        intentosFallidos = view_fallidos.query.filter_by(id_placa = placa.upper()).all()
        espaciosOcupados = None
        fecha = datetime.today()

        espacio = False
        if ley == 'on': 
            espacio = True
        else:
            espacio = False

        if cedula != None and  usuario != None:
            if usuario.rol == 1 or usuario.rol == 2:
                flash('La cédula ingresada no pertenece a un estudiante o personal administrativo',  category='error')
                return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = False)
            
        if cedula != None and vehiculo:
            flash('La placa ya se encuentra registrada en el sistema',  category='error')
            return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = False)

        if vehiculo:
            espaciosOcupados = view_resumen.query.filter_by(id_parqueo = idparqueo, tipo = vehiculo.tipo, espacio = vehiculo.espacio).first()
            ultimaEntradaUsuario = view_entradas.query.filter_by(id_usuario = vehiculo.id_usuario).first()
        
        if vehiculo and ultimaEntradaUsuario != None:
            seEncuentra = view_entradas.query.filter_by(id_usuario = vehiculo.id_usuario).first()
            flash(f'El dueño del vehículo ya se encuentra en el parqueo {seEncuentra.id_parqueo}',  category='error')
            return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo, registrado = True)        
       
       
        if ultimaEntrada:
            if ultimaEntrada.id_parqueo != int(idparqueo):
                flash('El vehículo se encuentra en otro parqueo',  category='error')
            else:
                flash('El vehículo aún se encuentra en el parqueo',  category='error')
            return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = True)
        else:
            if not espaciosOcupados and vehiculo:
                nuevoIngreso =  Actividad(fecha= fecha, actividad = "Ingreso", id_placa = placa.upper(), id_parqueo = idparqueo, id_usuario = vehiculo.id_usuario) 
                db.session.add(nuevoIngreso) 
                db.session.commit() 
                flash('El vehículo puede ingresar',  category='success')
                return render_template("guarda_ingresos.html", imagen = "semaforoVerde.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = True)
            elif espaciosOcupados:
                Guarda.Ocupados(vehiculo, espaciosOcupados, fecha, placa, idparqueo, nombre)
                flash('El vehículo puede ingresar',  category='success')
                return render_template("guarda_ingresos.html", imagen = "semaforoVerde.png", nombre=nombre, placa = placa, id=idparqueo, registrado = True)


            #Ingresos fallidos

            if not vehiculo and ultimaEntradaFallida != None:
                usuario = Usuario.query.filter_by(id = ultimaEntradaFallida.id_usuario).first()
                if len(intentosFallidos) == 1 and usuario.rol == 3:
                    flash('El vehículo del estudiante ya tuvo un ingreso fallido',  category='error')
                    return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = True)
                elif len(intentosFallidos) > 2 and usuario.rol == 4:
                    flash('El vehículo del personal admnistrativo ya tuvo 3 ingresos fallidos',  category='error')
                    return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = True)
                else:
                    if not espaciosOcupados and not vehiculo:
                        nuevoIngreso =  Actividad(fecha= fecha, actividad = "Ingreso Fallido", tipo = ultimaEntradaFallida.tipo, espacio = ultimaEntradaFallida.espacio, id_placa = placa.upper(), id_parqueo = idparqueo, id_usuario = usuario.id) 
                        db.session.add(nuevoIngreso) 
                        db.session.commit() 
                        flash('El vehículo puede ingresar',  category='success')
                        return render_template("guarda_ingresos.html", imagen = "semaforoVerde.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = True)
                    elif espaciosOcupados:
                        Guarda.Ocupados(vehiculo, espaciosOcupados, fecha, placa, idparqueo, nombre)
                        flash('El vehículo puede ingresar',  category='success')
                        return render_template("guarda_ingresos.html", imagen = "semaforoVerde.png", nombre=nombre, placa = placa, id=idparqueo, registrado = True)    
           
            
            elif not vehiculo and cedula == None:
                flash('El vehículo no está registrado, ingrese también la cédula',  category='warning')
                return render_template("guarda_ingresos.html", imagen = "semaforo.png", nombre=nombre, placa = placa, id=idparqueo, registrado = False)
           
            elif not vehiculo and ultimaFallidaUsuario:
                flash(f'La persona ya se encuentra en el parqueo con otro vehículo',  category='error')
                return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo, registrado = False)
            
            elif not vehiculo and usuario:
                espaciosOcupados = view_resumen.query.filter_by(id_parqueo = idparqueo, tipo = tipo, espacio = espacio).first()

                if cantidadVehiculos > 1:
                    flash('La persona ya cuenta con 2 vehículos registrados',  category='error')
                    return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = True)
                if ultimaEntrada:
                    if ultimaEntrada.id_parqueo != int(idparqueo):
                        flash('El vehículo se encuentra en otro parqueo',  category='error')
                    else:
                        flash('El vehículo aún se encuentra en el parqueo',  category='error')
                    return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = True)
                else:
                    if not espaciosOcupados and not vehiculo:
                        nuevoIngreso =  Actividad(fecha= fecha, actividad = "Ingreso Fallido", tipo = tipo, espacio = espacio, id_placa = placa.upper(), id_parqueo = idparqueo, id_usuario = cedula) 
                        db.session.add(nuevoIngreso) 
                        db.session.commit() 
                        flash('El vehículo puede ingresar',  category='success')
                        return render_template("guarda_ingresos.html", imagen = "semaforoVerde.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = True)
                    elif espaciosOcupados:
                        Guarda.Ocupados(vehiculo, espaciosOcupados, fecha, placa, idparqueo, nombre)
                        flash('El vehículo puede ingresar',  category='success')
                        return render_template("guarda_ingresos.html", imagen = "semaforoVerde.png", nombre=nombre, placa = placa, id=idparqueo, registrado = True)

    def egresoVehiculos(nombre, idparqueo, placa):
        vehiculo = Vehiculo.query.filter_by(placa=placa.upper()).first()
        ultimaEntrada = view_entradas.query.filter_by(id_placa = placa.upper(), id_parqueo = idparqueo).first()
        ultimaFallida = view_fallidos.query.filter_by(id_placa = placa.upper()).first()
        fecha = datetime.today()

        if ultimaEntrada:
            if not ultimaFallida:
                nuevoEgreso =  Actividad(fecha= fecha, actividad = "Egreso", id_placa = placa.upper(), id_parqueo = idparqueo, id_usuario = vehiculo.id_usuario) 
            else:
                nuevoEgreso =  Actividad(fecha= fecha, actividad = "Egreso", id_placa = placa.upper(), id_parqueo = idparqueo, id_usuario = ultimaFallida.id_usuario) 
            db.session.add(nuevoEgreso) 
            db.session.commit() 
            flash('El vehículo puede salir',  category='success')
            return render_template("guarda_egresos.html", nombre=nombre, id=idparqueo)
        else:
            flash('El vehículo no se encuentra en el parqueo',  category='error')
            return render_template("guarda_egresos.html", nombre=nombre, id=idparqueo)
        
    def Ocupados(vehiculo, espaciosOcupados, fecha, placa, idparqueo, nombre):
        if vehiculo.tipo == "Carro" and vehiculo.espacio == True:
            if espaciosOcupados.ocupados < espaciosOcupados.capacidad_ley:
                nuevoIngreso =  Actividad(fecha= fecha, actividad = "Ingreso", id_placa = placa.upper(), id_parqueo = idparqueo, id_usuario = vehiculo.id_usuario) 
                db.session.add(nuevoIngreso) 
                db.session.commit()
            else:
                flash('Los espacios ley 7600 están llenos',  category='error')
                return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, id=idparqueo, placa = placa,  registrado = True)
        elif vehiculo.tipo == "Carro" and vehiculo.espacio == False:
            if espaciosOcupados.ocupados < espaciosOcupados.capacidad_regulares:
                nuevoIngreso =  Actividad(fecha= fecha, actividad = "Ingreso", id_placa = placa.upper(), id_parqueo = idparqueo, id_usuario = vehiculo.id_usuario) 
                db.session.add(nuevoIngreso) 
                db.session.commit() 
            else:
                flash('Los espacios regulares están llenos',  category='error')
                return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = True)
        elif vehiculo.tipo == "Moto":
            if espaciosOcupados.ocupados < espaciosOcupados.capacidad_motos:
                nuevoIngreso =  Actividad(fecha= fecha, actividad = "Ingreso", id_placa = placa.upper(), id_parqueo = idparqueo, id_usuario = vehiculo.id_usuario) 
                db.session.add(nuevoIngreso) 
                db.session.commit()
            else:
                flash('Los espacios de motos están llenos',  category='error')
                return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = True)
        else:
            flash('El vehículo no está registrado',  category='error')
            return render_template("guarda_ingresos.html", imagen = "semaforoRojo.png", nombre=nombre, placa = placa, id=idparqueo,  registrado = True)
       
       

    

class Actividad(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    actividad = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=True)
    espacio = db.Column(db.Boolean, nullable=True)
    id_placa =  db.Column(db.String, nullable=False, unique=True)
    id_parqueo = db.Column(db.Integer, db.ForeignKey('parqueo.id'), nullable=False)
    id_placa =  db.Column(db.String, nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

class Parqueo(db.Model): # Modelo SQLAlchemy para le estructura de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), unique=True, nullable=False)
    capacidad_regulares = db.Column(db.Integer, nullable=False)
    capacidad_motos = db.Column(db.Integer, nullable=False)
    capacidad_ley = db.Column(db.Integer, nullable=False)
    actividad = db.relationship('Actividad')

class Vehiculo(db.Model): # Modelo SQLAlchemy para le estructura de la tabla
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(100), nullable=False)
    placa = db.Column(db.String(100), nullable=False, unique=True)
    espacio = db.Column(db.Boolean, nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))


class view_salidas(db.Model):
    __table__ = create_view(
    name="salidas_mas_recientes",    
    selectable=select(Actividad.id_placa, func.max(Actividad.fecha).label('egreso'))
               .where(Actividad.actividad == 'Egreso').group_by(Actividad.id_placa),
    metadata = db.metadata,
    replace=True
    )

class view_entradas(db.Model):
    __table__ = create_view(
    name="entradas_mas_recientes",    
    selectable=select(Actividad.id_placa, Actividad.id_usuario, Actividad.id_parqueo, Vehiculo.tipo, Vehiculo.espacio, func.max(Actividad.fecha).label('ingreso'))
                .join(view_salidas, Actividad.id_placa==view_salidas.id_placa,isouter=True)
                .join(Vehiculo, Actividad.id_placa == Vehiculo.placa,isouter=True)
                .where(and_(Actividad.actividad == 'Ingreso', or_(Actividad.fecha > view_salidas.egreso, view_salidas.egreso == None)))
                .group_by(Actividad.id_placa, Actividad.id_usuario, Actividad.id_parqueo, Vehiculo.tipo, Vehiculo.espacio)
                .union(
                    select(Actividad.id_placa, Actividad.id_usuario, Actividad.id_parqueo, Actividad.tipo, Actividad.espacio, func.max(Actividad.fecha).label('ingreso'))
                    .join(view_salidas, Actividad.id_placa==view_salidas.id_placa,isouter=True)
                    .where(and_(Actividad.actividad == 'Ingreso Fallido', or_(Actividad.fecha > view_salidas.egreso, view_salidas.egreso == None)))
                    .group_by(Actividad.id_placa, Actividad.id_usuario, Actividad.id_parqueo, Actividad.tipo, Actividad.espacio)
                ),
                metadata = db.metadata,
                replace=True
    )

class view_resumen(db.Model):
    __table__ = create_view(
    name="resumen_parqueo",    
    selectable=select(view_entradas.id_parqueo, view_entradas.tipo, view_entradas.espacio, Parqueo.capacidad_regulares, Parqueo.capacidad_motos, 
                      Parqueo.capacidad_ley, func.count('*').label('ocupados'))
                .join(Parqueo, view_entradas.id_parqueo == Parqueo.id)
                .group_by(view_entradas.id_parqueo, view_entradas.tipo, view_entradas.espacio, Parqueo.nombre, Parqueo.capacidad_regulares, 
                          Parqueo.capacidad_motos, Parqueo.capacidad_ley)
                .order_by(view_entradas.id_parqueo, view_entradas.tipo, view_entradas.espacio),
                metadata = db.metadata,
                replace=True
    )

class view_fallidos(db.Model):
    __table__ = create_view(
    name="ingresos_fallidos",    
    selectable=select(Actividad.id_placa, Actividad.id_usuario, Actividad.id_parqueo, Actividad.tipo, Actividad.espacio, Actividad.fecha)
                .where(Actividad.actividad == 'Ingreso Fallido'),
                metadata = db.metadata,
                replace=True
    )

class view_aprobacion(db.Model):
    __table__ = create_view(
    name="vehiculos_aprobacion",    
    selectable=select(view_fallidos.id_placa, view_fallidos.id_usuario, view_fallidos.tipo, view_fallidos.espacio, view_fallidos.fecha).distinct(view_fallidos.id_placa)
               .join(Vehiculo, view_fallidos.id_placa == Vehiculo.placa, isouter=True)
               .where(Vehiculo.placa == None),
                metadata = db.metadata,
                replace=True
    )

class view_horaEntrada(db.Model):
    __table__ = create_view(
        name='entrada',
        selectable=select(
                Actividad.id_parqueo,
                Actividad.id_placa,
                Actividad.id_usuario,
                func.date(Actividad.fecha).label('fecha'),
                func.cast(Actividad.fecha, Time).label('hora_entrada'),
                func.row_number().over(
                    partition_by=[
                        Actividad.id_parqueo,
                        Actividad.id_placa,
                        Actividad.id_usuario,
                        func.date(Actividad.fecha)
                    ],
                   order_by= func.cast(Actividad.fecha, Time)
                ).label('rn')
        ).where(
            Actividad.actividad.in_(['Ingreso', 'Ingreso Fallido'])
        ),
        metadata=db.metadata,
        replace=True
    )

class view_horaSalida(db.Model):
    __table__ = create_view(
        name='salida',
        selectable=select(
                Actividad.id_parqueo,
                Actividad.id_placa,
                Actividad.id_usuario,
                func.date(Actividad.fecha).label('fecha'),
                func.cast(Actividad.fecha, Time).label('hora_salida'), 
                func.row_number().over(
                    partition_by=[
                        Actividad.id_parqueo,
                        Actividad.id_placa,
                        Actividad.id_usuario,
                        func.date(Actividad.fecha)
                    ],
                    order_by= func.cast(Actividad.fecha, Time)
                ).label('rn')
        ).where(
            Actividad.actividad == 'Egreso'
        ),
        metadata=db.metadata,
        replace=True
    )

class view_uso(db.Model):
    __table__ = create_view(
        name='uso_parqueo',
        selectable=select(
                view_horaEntrada.id_parqueo,
                view_horaEntrada.__table__.c.id_placa,
                view_horaEntrada.__table__.c.id_usuario,
                view_horaEntrada.__table__.c.fecha.label('fecha'),
                view_horaEntrada.__table__.c.hora_entrada.label('entrada'),
                view_horaSalida.__table__.c.hora_salida.label('salida')
        ).select_from(
            view_horaEntrada.__table__.outerjoin(
                view_horaSalida.__table__,
                (view_horaEntrada.__table__.c.id_parqueo == view_horaSalida.__table__.c.id_parqueo) &
                (view_horaEntrada.__table__.c.id_placa == view_horaSalida.__table__.c.id_placa) &
                (view_horaEntrada.__table__.c.id_usuario == view_horaSalida.__table__.c.id_usuario) &
                (view_horaEntrada.__table__.c.fecha == view_horaSalida.__table__.c.fecha) &
                (view_horaEntrada.__table__.c.rn == view_horaSalida.__table__.c.rn)
            )
        ).order_by(
            view_horaEntrada.__table__.c.id_placa,
            view_horaEntrada.__table__.c.fecha,
            view_horaEntrada.__table__.c.hora_entrada
        ),
        metadata=db.metadata,
        replace=True
    )
