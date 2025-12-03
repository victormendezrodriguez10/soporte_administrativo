"""
Módulo para gestionar archivos en Cloudinary
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from pathlib import Path
from typing import Optional, Dict
import tempfile
import requests

class CloudinaryStorage:
    def __init__(self, cloud_name: str = None, api_key: str = None, api_secret: str = None):
        """
        Inicializa el gestor de Cloudinary

        Args:
            cloud_name: Nombre del cloud de Cloudinary
            api_key: API key de Cloudinary
            api_secret: API secret de Cloudinary
        """
        self.cloud_name = cloud_name or os.getenv('CLOUDINARY_CLOUD_NAME')
        self.api_key = api_key or os.getenv('CLOUDINARY_API_KEY')
        self.api_secret = api_secret or os.getenv('CLOUDINARY_API_SECRET')

        if not all([self.cloud_name, self.api_key, self.api_secret]):
            raise ValueError("Se requieren las credenciales de Cloudinary: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET")

        # Configurar Cloudinary
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True
        )

    def subir_archivo(self, archivo_path: str, folder: str = "soporte_admin", resource_type: str = "auto") -> Dict:
        """
        Sube un archivo a Cloudinary

        Args:
            archivo_path: Ruta local del archivo
            folder: Carpeta en Cloudinary donde guardar
            resource_type: Tipo de recurso (auto, image, video, raw)

        Returns:
            Diccionario con información del archivo subido
        """
        try:
            # Subir archivo
            resultado = cloudinary.uploader.upload(
                archivo_path,
                folder=folder,
                resource_type=resource_type,
                use_filename=True,
                unique_filename=True
            )

            return {
                'public_id': resultado['public_id'],
                'url': resultado['secure_url'],
                'format': resultado.get('format'),
                'size': resultado.get('bytes'),
                'created_at': resultado.get('created_at')
            }

        except Exception as e:
            raise Exception(f"Error al subir archivo a Cloudinary: {e}")

    def subir_desde_bytes(self, archivo_bytes: bytes, nombre_archivo: str, folder: str = "soporte_admin") -> Dict:
        """
        Sube un archivo desde bytes a Cloudinary

        Args:
            archivo_bytes: Contenido del archivo en bytes
            nombre_archivo: Nombre del archivo
            folder: Carpeta en Cloudinary

        Returns:
            Diccionario con información del archivo subido
        """
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(nombre_archivo).suffix) as tmp:
                tmp.write(archivo_bytes)
                tmp_path = tmp.name

            # Subir archivo temporal
            resultado = self.subir_archivo(tmp_path, folder=folder)

            # Eliminar archivo temporal
            os.unlink(tmp_path)

            return resultado

        except Exception as e:
            raise Exception(f"Error al subir archivo desde bytes: {e}")

    def descargar_archivo(self, public_id: str, destino_path: Optional[str] = None) -> str:
        """
        Descarga un archivo de Cloudinary

        Args:
            public_id: ID público del archivo en Cloudinary
            destino_path: Ruta donde guardar (opcional, si no se usa archivo temporal)

        Returns:
            Ruta del archivo descargado
        """
        try:
            # Obtener URL del archivo
            url = cloudinary.CloudinaryImage(public_id).build_url()

            # Descargar archivo
            response = requests.get(url)
            response.raise_for_status()

            # Si no se especifica destino, usar archivo temporal
            if destino_path is None:
                extension = Path(public_id).suffix or '.bin'
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
                    tmp.write(response.content)
                    destino_path = tmp.name
            else:
                with open(destino_path, 'wb') as f:
                    f.write(response.content)

            return destino_path

        except Exception as e:
            raise Exception(f"Error al descargar archivo de Cloudinary: {e}")

    def eliminar_archivo(self, public_id: str, resource_type: str = "raw") -> bool:
        """
        Elimina un archivo de Cloudinary

        Args:
            public_id: ID público del archivo
            resource_type: Tipo de recurso

        Returns:
            True si se eliminó correctamente
        """
        try:
            resultado = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            return resultado.get('result') == 'ok'
        except Exception as e:
            print(f"Error al eliminar archivo: {e}")
            return False

    def listar_archivos(self, folder: str = "soporte_admin", max_results: int = 100) -> list:
        """
        Lista archivos en una carpeta de Cloudinary

        Args:
            folder: Carpeta a listar
            max_results: Número máximo de resultados

        Returns:
            Lista de archivos
        """
        try:
            resultado = cloudinary.api.resources(
                type="upload",
                prefix=folder,
                max_results=max_results
            )
            return resultado.get('resources', [])
        except Exception as e:
            print(f"Error al listar archivos: {e}")
            return []

    def obtener_url(self, public_id: str) -> str:
        """
        Obtiene la URL segura de un archivo

        Args:
            public_id: ID público del archivo

        Returns:
            URL del archivo
        """
        return cloudinary.CloudinaryImage(public_id).build_url(secure=True)

    def crear_carpetas(self):
        """
        Crea las carpetas necesarias en Cloudinary (uploaded_pdfs, generated_pdfs)
        Nota: Cloudinary crea carpetas automáticamente al subir archivos
        """
        # Las carpetas se crean automáticamente en Cloudinary
        # Esta función existe por compatibilidad
        pass
