"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Receta
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api) # permite llamadas desde React


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200



# ----------------------------
# RUTAS AUTH (sin JWT)
# ----------------------------

@api.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if not data.get("email") or not data.get("password") or not data.get("nombre_dueno"):
        return jsonify({"msg": "Faltan datos"}), 400

    # Verificar si el usuario ya existe
    existe = User.query.filter_by(email=data["email"]).first()
    if existe:
        return jsonify({"msg": "El usuario ya existe"}), 400

    # Crear usuario sin hash de password
    nuevo = User(
        nombre_dueno=data["nombre_dueno"],
        email=data["email"],
        password=data["password"],  # se guarda tal cual
        is_active=True
    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({
        "msg": "Usuario creado correctamente",
        "user": {
            "id": nuevo.id,
            "nombre_dueno": nuevo.nombre_dueno,
            "email": nuevo.email,
            "is_active": nuevo.is_active
        }
    }), 201



@api.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email, password=password).first()
    if not user:
        return jsonify({"msg": "Credenciales inválidas"}), 401

    return jsonify({"msg": "Login exitoso", "user": user.serialize()}), 200




@api.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    return jsonify(user.serialize()), 200



# -----------------------
# 📋 CRUD RECETAS (SIN JWT)
# -----------------------

@api.route('/recetas', methods=['POST'])
def crear_receta():
    data = request.json or {}
    user_id = data.get("user_id")  # ahora se pasa directamente en el JSON

    nueva = Receta(
        nombre_mascota=data["nombre_mascota"],
        peso_mascota=data["peso_mascota"],
        color_mascota=data["color_mascota"],
        especie=data["especie"],
        sexo=data["sexo"],
        nombre_veterinario=data["nombre_veterinario"],
        fecha_atencion=data["fecha_atencion"],
        diagnostico=data["diagnostico"],
        tratamiento=data["tratamiento"],
        user_id=user_id
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify(nueva.serialize()), 201


@api.route('/recetas', methods=['GET'])
def listar_recetas():
    filtros = request.args
    query = Receta.query

    if "nombre" in filtros:
        query = query.filter(Receta.nombre_mascota.ilike(f"%{filtros['nombre']}%"))
    if "fecha" in filtros:
        query = query.filter(Receta.fecha_atencion == filtros["fecha"])
    if "diagnostico" in filtros:
        query = query.filter(Receta.diagnostico.ilike(f"%{filtros['diagnostico']}%"))
    if "tratamiento" in filtros:
        query = query.filter(Receta.tratamiento.ilike(f"%{filtros['tratamiento']}%"))
    if "veterinario" in filtros:
        query = query.filter(Receta.nombre_veterinario.ilike(f"%{filtros['veterinario']}%"))

    recetas = query.all()
    return jsonify([r.serialize() for r in recetas]), 200


@api.route('/recetas/<int:id>', methods=['GET'])
def obtener_receta(id):
    receta = Receta.query.get(id)
    if not receta:
        return jsonify({"msg": "Receta no encontrada"}), 404
    return jsonify(receta.serialize()), 200


@api.route('/recetas/<int:id>', methods=['PUT'])
def editar_receta(id):
    receta = Receta.query.get(id)
    if not receta:
        return jsonify({"msg": "Receta no encontrada"}), 404

    data = request.json or {}
    receta.nombre_mascota = data.get("nombre_mascota", receta.nombre_mascota)
    receta.peso_mascota = data.get("peso_mascota", receta.peso_mascota)
    receta.color_mascota = data.get("color_mascota", receta.color_mascota)
    receta.especie = data.get("especie", receta.especie)
    receta.sexo = data.get("sexo", receta.sexo)
    receta.nombre_veterinario = data.get("nombre_veterinario", receta.nombre_veterinario)
    receta.fecha_atencion = data.get("fecha_atencion", receta.fecha_atencion)
    receta.diagnostico = data.get("diagnostico", receta.diagnostico)
    receta.tratamiento = data.get("tratamiento", receta.tratamiento)

    db.session.commit()
    return jsonify(receta.serialize()), 200


@api.route('/recetas/<int:id>', methods=['DELETE'])
def eliminar_receta(id):
    receta = Receta.query.get(id)
    if not receta:
        return jsonify({"msg": "Receta no encontrada"}), 404

    db.session.delete(receta)
    db.session.commit()
    return jsonify({"msg": "Receta eliminada"}), 200

