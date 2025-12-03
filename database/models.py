"""
Modelos de base de datos para la aplicación de Soporte Administrativo
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Datos del representante legal
    nombre_representante_legal = Column(String(200))
    dni_representante = Column(String(20))

    # Datos de la empresa
    razon_social = Column(String(300))
    cif = Column(String(20), unique=True)
    direccion = Column(Text)
    correo_electronico = Column(String(200))

    # Datos operacionales
    numero_trabajadores = Column(Integer)
    facturacion = Column(Float)

    # Certificaciones y habilitaciones
    habilitaciones = Column(Text)  # JSON o texto separado por comas
    isos = Column(Text)  # JSON o texto separado por comas
    rolece = Column(String(100))

    # Políticas y protocolos
    tiene_plan_igualdad = Column(Boolean, default=False)
    tiene_protocolo_acoso = Column(Boolean, default=False)

    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Archivos PDF originales (opcional, guardar en blob)
    pdf_original_nombre = Column(String(300))
    pdf_original_ruta = Column(String(500))

    def __repr__(self):
        return f"<Cliente {self.razon_social} - CIF: {self.cif}>"

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'nombre_representante_legal': self.nombre_representante_legal,
            'dni_representante': self.dni_representante,
            'razon_social': self.razon_social,
            'cif': self.cif,
            'direccion': self.direccion,
            'correo_electronico': self.correo_electronico,
            'numero_trabajadores': self.numero_trabajadores,
            'facturacion': self.facturacion,
            'habilitaciones': self.habilitaciones,
            'isos': self.isos,
            'rolece': self.rolece,
            'tiene_plan_igualdad': self.tiene_plan_igualdad,
            'tiene_protocolo_acoso': self.tiene_protocolo_acoso,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
