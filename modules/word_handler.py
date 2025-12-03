"""
Módulo para manejar documentos Word (.docx)
"""
import anthropic
import base64
import os
import json
from pathlib import Path
from typing import Dict
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

class WordHandler:
    def __init__(self, api_key: str = None):
        """
        Inicializa el manejador de Word con Claude API

        Args:
            api_key: API key de Anthropic
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Se requiere ANTHROPIC_API_KEY")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def extraer_texto_word(self, docx_path: str) -> str:
        """
        Extrae todo el texto de un documento Word

        Args:
            docx_path: Ruta al archivo .docx

        Returns:
            Texto completo del documento
        """
        doc = Document(docx_path)
        texto_completo = []

        for para in doc.paragraphs:
            texto_completo.append(para.text)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    texto_completo.append(cell.text)

        return '\n'.join(texto_completo)

    def extraer_datos_cliente_word(self, docx_path: str) -> Dict[str, any]:
        """
        Extrae datos del cliente desde un documento Word usando Claude API

        Args:
            docx_path: Ruta al archivo Word

        Returns:
            Diccionario con los datos extraídos
        """
        texto = self.extraer_texto_word(docx_path)

        prompt = f"""Analiza este texto extraído de un documento Word y extrae la siguiente información sobre el cliente/empresa:

TEXTO DEL DOCUMENTO:
{texto}

CAMPOS A EXTRAER:
1. nombre_representante_legal: Nombre completo del representante legal
2. dni_representante: DNI/NIF del representante legal
3. razon_social: Razón social de la empresa
4. cif: CIF de la empresa
5. direccion: Dirección completa de la empresa
6. correo_electronico: Correo electrónico de contacto
7. numero_trabajadores: Número de trabajadores (como número entero)
8. facturacion: Facturación anual (como número decimal, sin símbolos)
9. habilitaciones: Lista de habilitaciones (separadas por comas)
10. isos: Certificaciones ISO que posee (separadas por comas)
11. rolece: Número o código ROLECE si está presente
12. tiene_plan_igualdad: true si tiene plan de igualdad, false si no
13. tiene_protocolo_acoso: true si tiene protocolo de acoso, false si no

Responde ÚNICAMENTE con un objeto JSON válido. Si un campo no está presente, usa null.

Ejemplo:
{{
  "nombre_representante_legal": "María López",
  "dni_representante": "12345678A",
  "razon_social": "Empresa SA",
  "cif": "A12345678",
  "direccion": "Calle Principal 1",
  "correo_electronico": "info@empresa.com",
  "numero_trabajadores": 25,
  "facturacion": 500000.00,
  "habilitaciones": "Transporte, Logística",
  "isos": "ISO 9001",
  "rolece": null,
  "tiene_plan_igualdad": false,
  "tiene_protocolo_acoso": true
}}"""

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = message.content[0].text

            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            datos = json.loads(response_text.strip())
            datos['pdf_original_nombre'] = Path(docx_path).name
            datos['pdf_original_ruta'] = docx_path

            return datos

        except Exception as e:
            raise Exception(f"Error al extraer datos del Word: {e}")

    def rellenar_word_con_marcadores(self, docx_path: str, datos_cliente: Dict, output_path: str):
        """
        Rellena un documento Word que use marcadores/placeholders como {{campo}}

        Args:
            docx_path: Ruta al documento Word plantilla
            datos_cliente: Datos del cliente
            output_path: Ruta de salida
        """
        doc = Document(docx_path)

        # Mapeo de campos
        mapeo = {
            '{{NOMBRE_REPRESENTANTE}}': datos_cliente.get('nombre_representante_legal', ''),
            '{{DNI_REPRESENTANTE}}': datos_cliente.get('dni_representante', ''),
            '{{RAZON_SOCIAL}}': datos_cliente.get('razon_social', ''),
            '{{CIF}}': datos_cliente.get('cif', ''),
            '{{DIRECCION}}': datos_cliente.get('direccion', ''),
            '{{EMAIL}}': datos_cliente.get('correo_electronico', ''),
            '{{NUM_TRABAJADORES}}': str(datos_cliente.get('numero_trabajadores', '')),
            '{{FACTURACION}}': str(datos_cliente.get('facturacion', '')),
            '{{HABILITACIONES}}': datos_cliente.get('habilitaciones', ''),
            '{{ISOS}}': datos_cliente.get('isos', ''),
            '{{ROLECE}}': datos_cliente.get('rolece', ''),
            '{{PLAN_IGUALDAD}}': 'Sí' if datos_cliente.get('tiene_plan_igualdad') else 'No',
            '{{PROTOCOLO_ACOSO}}': 'Sí' if datos_cliente.get('tiene_protocolo_acoso') else 'No'
        }

        # Reemplazar en párrafos
        for para in doc.paragraphs:
            for marcador, valor in mapeo.items():
                if marcador in para.text:
                    para.text = para.text.replace(marcador, str(valor) if valor else '')

        # Reemplazar en tablas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        for marcador, valor in mapeo.items():
                            if marcador in para.text:
                                para.text = para.text.replace(marcador, str(valor) if valor else '')

        doc.save(output_path)

    def rellenar_word_con_ia(self, docx_path: str, datos_cliente: Dict, output_path: str) -> Dict:
        """
        Analiza un documento Word y lo rellena usando IA

        Args:
            docx_path: Ruta al documento Word
            datos_cliente: Datos del cliente
            output_path: Ruta de salida

        Returns:
            Información del proceso
        """
        # Extraer texto original
        texto_original = self.extraer_texto_word(docx_path)

        # Crear descripción de datos disponibles
        datos_json = json.dumps(datos_cliente, indent=2, ensure_ascii=False)

        prompt = f"""Tienes un documento Word con el siguiente contenido:

{texto_original}

Y estos datos del cliente:
{datos_json}

Identifica en el texto original dónde deben ir los datos del cliente y genera el texto COMPLETO del documento rellenado.

Instrucciones:
1. Mantén TODA la estructura y formato del documento original
2. Rellena los campos vacíos (____), huecos, o campos identificables con los datos correspondientes del cliente
3. Si hay checkboxes o casillas (☐), márcalas con [X] si el dato del cliente es true
4. Devuelve el documento COMPLETO con todos los campos rellenados

Responde SOLO con el texto del documento rellenado, sin explicaciones adicionales."""

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            texto_rellenado = message.content[0].text

            # Crear nuevo documento con el texto rellenado
            doc = Document()

            # Dividir por líneas y crear párrafos
            for linea in texto_rellenado.split('\n'):
                doc.add_paragraph(linea)

            doc.save(output_path)

            return {
                'exito': True,
                'mensaje': 'Documento Word rellenado con IA'
            }

        except Exception as e:
            raise Exception(f"Error al rellenar Word con IA: {e}")

    def rellenar_word(self, docx_path: str, datos_cliente: Dict, output_path: str, usar_marcadores: bool = True) -> Dict:
        """
        Método principal para rellenar documentos Word

        Args:
            docx_path: Ruta al documento Word
            datos_cliente: Datos del cliente
            output_path: Ruta de salida
            usar_marcadores: Si True, intenta con marcadores primero

        Returns:
            Información del proceso
        """
        try:
            if usar_marcadores:
                # Intentar con marcadores
                self.rellenar_word_con_marcadores(docx_path, datos_cliente, output_path)
                return {
                    'exito': True,
                    'metodo': 'marcadores',
                    'mensaje': 'Documento rellenado usando marcadores'
                }
            else:
                # Usar IA
                return self.rellenar_word_con_ia(docx_path, datos_cliente, output_path)

        except Exception as e:
            # Si falla con marcadores, intentar con IA
            if usar_marcadores:
                return self.rellenar_word_con_ia(docx_path, datos_cliente, output_path)
            else:
                raise e
