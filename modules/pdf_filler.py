"""
Módulo para rellenar PDFs con datos de clientes usando IA
"""
import anthropic
import base64
import os
import json
from pathlib import Path
from typing import Dict
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

class PDFFiller:
    def __init__(self, api_key: str = None):
        """
        Inicializa el rellenador de PDFs con Claude API

        Args:
            api_key: API key de Anthropic
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Se requiere ANTHROPIC_API_KEY")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def analizar_formulario_pdf(self, pdf_path: str, datos_cliente: Dict) -> Dict:
        """
        Analiza un formulario PDF y determina dónde colocar los datos del cliente

        Args:
            pdf_path: Ruta al PDF formulario vacío
            datos_cliente: Diccionario con datos del cliente

        Returns:
            Información sobre cómo rellenar el formulario
        """
        # Leer el PDF y convertirlo a base64
        with open(pdf_path, 'rb') as f:
            pdf_data = base64.standard_b64encode(f.read()).decode('utf-8')

        # Crear descripción de los datos disponibles
        datos_disponibles = json.dumps(datos_cliente, indent=2, ensure_ascii=False)

        prompt = f"""Analiza este formulario PDF vacío y los datos del cliente proporcionados.

DATOS DEL CLIENTE DISPONIBLES:
{datos_disponibles}

INSTRUCCIONES:
1. Identifica todos los campos del formulario que se pueden rellenar
2. Para cada campo, determina:
   - El texto exacto del campo/etiqueta en el PDF
   - Qué dato del cliente corresponde a ese campo
   - La posición aproximada en el PDF (página, zona: superior/media/inferior, izquierda/centro/derecha)
   - Si es un campo de texto libre o una casilla de verificación (checkbox)

3. Responde con un JSON con este formato:
{{
  "campos": [
    {{
      "etiqueta_en_pdf": "Nombre del representante legal:",
      "campo_cliente": "nombre_representante_legal",
      "valor": "valor del campo del cliente",
      "pagina": 1,
      "zona": "superior izquierda",
      "tipo": "texto"
    }},
    {{
      "etiqueta_en_pdf": "☐ Tiene plan de igualdad",
      "campo_cliente": "tiene_plan_igualdad",
      "valor": true,
      "pagina": 2,
      "zona": "media derecha",
      "tipo": "checkbox"
    }}
  ],
  "instrucciones_especiales": "Cualquier nota sobre cómo rellenar el formulario"
}}

IMPORTANTE:
- Responde SOLO con JSON válido
- Incluye todos los campos que identifiques
- Si un dato del cliente no tiene campo correspondiente en el PDF, omítelo
- Para checkboxes, el valor será true o false"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            response_text = message.content[0].text

            # Limpiar respuesta
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            return json.loads(response_text.strip())

        except Exception as e:
            raise Exception(f"Error al analizar formulario PDF: {e}")

    def rellenar_pdf_interactivo(self, pdf_path: str, datos_cliente: Dict, output_path: str) -> bool:
        """
        Intenta rellenar un PDF interactivo (con campos de formulario)

        Args:
            pdf_path: Ruta al PDF original
            datos_cliente: Datos del cliente
            output_path: Ruta donde guardar el PDF rellenado

        Returns:
            True si se pudo rellenar, False si no es un PDF interactivo
        """
        try:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()

            # Verificar si tiene campos de formulario
            if reader.get_form_text_fields() is None:
                return False

            # Obtener campos del formulario
            form_fields = reader.get_form_text_fields()

            # Mapeo de nombres de campos comunes
            mapeo_campos = {
                'nombre_representante_legal': ['nombre', 'representante', 'nombre_representante', 'rep_legal'],
                'dni_representante': ['dni', 'nif', 'dni_representante', 'nif_representante'],
                'razon_social': ['razon_social', 'empresa', 'nombre_empresa', 'denominacion'],
                'cif': ['cif', 'nif_empresa', 'cif_empresa'],
                'direccion': ['direccion', 'domicilio', 'direccion_social'],
                'correo_electronico': ['email', 'correo', 'correo_electronico', 'e-mail'],
                'numero_trabajadores': ['trabajadores', 'num_trabajadores', 'plantilla'],
                'facturacion': ['facturacion', 'volumen_negocio', 'ingresos'],
                'habilitaciones': ['habilitaciones', 'autorizaciones'],
                'isos': ['iso', 'isos', 'certificaciones'],
                'rolece': ['rolece', 'rea'],
                'tiene_plan_igualdad': ['plan_igualdad', 'igualdad'],
                'tiene_protocolo_acoso': ['protocolo_acoso', 'acoso']
            }

            # Rellenar campos
            for page in reader.pages:
                writer.add_page(page)

            # Intentar rellenar cada campo del cliente
            for campo_cliente, valor in datos_cliente.items():
                if valor is None:
                    continue

                # Buscar campo correspondiente en el PDF
                for nombre_campo_pdf in form_fields.keys():
                    nombre_lower = nombre_campo_pdf.lower()

                    # Verificar si coincide con algún mapeo
                    if campo_cliente in mapeo_campos:
                        for variante in mapeo_campos[campo_cliente]:
                            if variante in nombre_lower:
                                # Convertir valor a string apropiado
                                if isinstance(valor, bool):
                                    valor_str = 'Sí' if valor else 'No'
                                else:
                                    valor_str = str(valor)

                                writer.update_page_form_field_values(
                                    writer.pages[0],
                                    {nombre_campo_pdf: valor_str}
                                )
                                break

            # Guardar PDF rellenado
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            return True

        except Exception as e:
            print(f"Error al rellenar PDF interactivo: {e}")
            return False

    def rellenar_pdf_con_ia(self, pdf_path: str, datos_cliente: Dict, output_path: str):
        """
        Rellena un PDF no interactivo usando IA para identificar campos

        Args:
            pdf_path: Ruta al PDF formulario
            datos_cliente: Datos del cliente
            output_path: Ruta de salida
        """
        # Primero analizar el formulario
        analisis = self.analizar_formulario_pdf(pdf_path, datos_cliente)

        # Leer el PDF original
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        # Este es un método simplificado
        # En producción, se necesitaría una biblioteca más avanzada como pdf-annotate
        # o generar overlays con las posiciones exactas

        print("ANÁLISIS DEL FORMULARIO:")
        print(json.dumps(analisis, indent=2, ensure_ascii=False))

        # Por ahora, copiar el PDF original
        # TODO: Implementar overlay de texto en las posiciones identificadas
        for page in reader.pages:
            writer.add_page(page)

        with open(output_path, 'wb') as f:
            writer.write(f)

        return analisis

    def rellenar_pdf(self, pdf_path: str, datos_cliente: Dict, output_path: str) -> Dict:
        """
        Método principal para rellenar un PDF (intenta interactivo primero, luego IA)

        Args:
            pdf_path: Ruta al PDF formulario
            datos_cliente: Datos del cliente
            output_path: Ruta de salida

        Returns:
            Diccionario con información del proceso
        """
        # Intentar rellenar como PDF interactivo
        if self.rellenar_pdf_interactivo(pdf_path, datos_cliente, output_path):
            return {
                'exito': True,
                'metodo': 'pdf_interactivo',
                'mensaje': 'PDF rellenado exitosamente (formulario interactivo)'
            }
        else:
            # Si no es interactivo, usar IA
            analisis = self.rellenar_pdf_con_ia(pdf_path, datos_cliente, output_path)
            return {
                'exito': True,
                'metodo': 'ia_analisis',
                'mensaje': 'PDF analizado con IA. Requiere implementación manual de overlay.',
                'analisis': analisis
            }
