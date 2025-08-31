from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Date, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_dueno: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    recetas = relationship("Receta", back_populates="usuario")


    def serialize(self):
        return {
            "id": self.id,
            "nombre_dueno": self.nombre_dueno,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    
class Receta(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_mascota: Mapped[str] = mapped_column(String(120), nullable=False)
    peso_mascota: Mapped[float] = mapped_column(nullable=False)
    color_mascota: Mapped[str] = mapped_column(String(120), nullable=False)
    especie: Mapped[str] = mapped_column(String(120), nullable=False)
    sexo: Mapped[str] = mapped_column(String(20), nullable=False)
    nombre_veterinario: Mapped[str] = mapped_column(String(120), nullable=False)
    fecha_atencion: Mapped[date] = mapped_column(nullable=False, default=date.today)
    diagnostico: Mapped[str] = mapped_column(Text, nullable=False)
    tratamiento: Mapped[str] = mapped_column(Text, nullable=False)

    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'))
    usuario = relationship("User", back_populates="recetas")

    def serialize(self):
        return {
            "id": self.id,
            "nombre_mascota": self.nombre_mascota,
            "peso_mascota": self.peso_mascota,
            "color_mascota": self.color_mascota,
            "especie": self.especie,
            "sexo": self.sexo,
            "nombre_veterinario": self.nombre_veterinario,
            "fecha_atencion": self.fecha_atencion.strftime('%Y-%m-%d'),
            "diagnostico": self.diagnostico,
            "tratamiento": self.tratamiento,
            "user_id": self.user_id
        }