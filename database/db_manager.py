"""
Gestor de base de datos (SQLite o PostgreSQL)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Cliente
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_url: str = None):
        """
        Inicializa el gestor de base de datos

        Args:
            db_url: URL de conexión
                   SQLite: sqlite:///database/clientes.db
                   PostgreSQL: postgresql://usuario:contraseña@host:5432/nombre_bd
                   Supabase: postgresql://user:pass@db.xxx.supabase.co:5432/postgres
        """
        if db_url is None:
            # Primero verificar si hay DATABASE_URL (común en servicios cloud)
            db_url = os.getenv('DATABASE_URL')

            if not db_url:
                # Verificar si hay configuración de PostgreSQL
                db_user = os.getenv('DB_USER')

                if db_user:
                    # Usar PostgreSQL
                    db_pass = os.getenv('DB_PASSWORD', 'postgres')
                    db_host = os.getenv('DB_HOST', 'localhost')
                    db_port = os.getenv('DB_PORT', '5432')
                    db_name = os.getenv('DB_NAME', 'soporte_admin')
                    db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
                else:
                    # Por defecto usar SQLite (gratis, sin configuración)
                    db_dir = Path('database')
                    db_dir.mkdir(exist_ok=True)
                    db_url = f"sqlite:///{db_dir}/clientes.db"
                    print(f"📁 Usando SQLite en: {db_dir}/clientes.db")

        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Crea todas las tablas en la base de datos"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Retorna una nueva sesión de base de datos"""
        return self.SessionLocal()

    def agregar_cliente(self, cliente_data: dict) -> Cliente:
        """
        Agrega un nuevo cliente a la base de datos

        Args:
            cliente_data: Diccionario con los datos del cliente

        Returns:
            Cliente creado
        """
        session = self.get_session()
        try:
            cliente = Cliente(**cliente_data)
            session.add(cliente)
            session.commit()
            session.refresh(cliente)
            return cliente
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def obtener_cliente(self, cliente_id: int) -> Cliente:
        """Obtiene un cliente por ID"""
        session = self.get_session()
        try:
            return session.query(Cliente).filter(Cliente.id == cliente_id).first()
        finally:
            session.close()

    def obtener_todos_clientes(self) -> list[Cliente]:
        """Obtiene todos los clientes"""
        session = self.get_session()
        try:
            return session.query(Cliente).all()
        finally:
            session.close()

    def actualizar_cliente(self, cliente_id: int, datos_nuevos: dict) -> Cliente:
        """Actualiza un cliente existente"""
        session = self.get_session()
        try:
            cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
            if cliente:
                for key, value in datos_nuevos.items():
                    if hasattr(cliente, key):
                        setattr(cliente, key, value)
                session.commit()
                session.refresh(cliente)
            return cliente
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def eliminar_cliente(self, cliente_id: int) -> bool:
        """Elimina un cliente"""
        session = self.get_session()
        try:
            cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
            if cliente:
                session.delete(cliente)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def buscar_por_cif(self, cif: str) -> Cliente:
        """Busca un cliente por CIF"""
        session = self.get_session()
        try:
            return session.query(Cliente).filter(Cliente.cif == cif).first()
        finally:
            session.close()
