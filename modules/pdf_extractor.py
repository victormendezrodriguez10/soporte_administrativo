"""
Módulo para extraer datos de PDFs usando Claude API
"""
import anthropic
import base64
import os
import json
from pathlib import Path
from typing import Dict, Optional

class PDFExtractor:
    def __init__(self, api_key: str = None):
        """
        Inicializa el extractor de PDFs con Claude API

        Args:
            api_key: API key de Anthropic. Si no se proporciona, se busca en variables de entorno
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Se requiere ANTHROPIC_API_KEY. Configúrala como variable de entorno o pásala al constructor")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def extraer_datos_cliente(self, pdf_path: str) -> Dict[str, any]:
        """
        Extrae datos del cliente desde un PDF usando Claude API

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Diccionario con los datos extraídos del cliente
        """
        # Leer el PDF y convertirlo a base64
        with open(pdf_path, 'rb') as f:
            pdf_data = base64.standard_b64encode(f.read()).decode('utf-8')

        # Definir el prompt para extraer datos
        prompt = """Analiza este documento PDF y extrae la siguiente información sobre el cliente/empresa:

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

IMPORTANTE:
- Responde ÚNICAMENTE con un objeto JSON válido
- Si un campo no está presente en el documento, usa null
- Para campos booleanos, usa true o false (sin comillas)
- Para números, no uses comillas
- No incluyas explicaciones, solo el JSON

Ejemplo de formato de respuesta:
{
  "nombre_representante_legal": "Juan Pérez García",
  "dni_representante": "12345678A",
  "razon_social": "Empresa Ejemplo S.L.",
  "cif": "B12345678",
  "direccion": "Calle Mayor 123, 28013 Madrid",
  "correo_electronico": "info@ejemplo.com",
  "numero_trabajadores": 50,
  "facturacion": 1500000.00,
  "habilitaciones": "Construcción, Instalaciones eléctricas",
  "isos": "ISO 9001, ISO 14001",
  "rolece": "REA-123456",
  "tiene_plan_igualdad": true,
  "tiene_protocolo_acoso": true
}"""

        try:
            # Llamar a Claude API con el PDF
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
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

            # Extraer la respuesta
            response_text = message.content[0].text

            # Parsear el JSON
            # A veces Claude puede incluir markdown, así que limpiamos
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            datos_extraidos = json.loads(response_text.strip())

            # Guardar info del archivo original
            datos_extraidos['pdf_original_nombre'] = Path(pdf_path).name
            datos_extraidos['pdf_original_ruta'] = pdf_path

            return datos_extraidos

        except json.JSONDecodeError as e:
            raise ValueError(f"Error al parsear la respuesta JSON de Claude: {e}\nRespuesta: {response_text}")
        except Exception as e:
            raise Exception(f"Error al extraer datos del PDF: {e}")

    def validar_datos(self, datos: Dict) -> tuple[bool, list]:
        """
        Valida que los datos extraídos sean correctos

        Returns:
            Tupla (es_valido, lista_errores)
        """
        errores = []

        # Validaciones básicas
        if datos.get('cif') and len(str(datos['cif'])) < 9:
            errores.append("CIF parece incorrecto (muy corto)")

        if datos.get('dni_representante') and len(str(datos['dni_representante'])) not in [9, 10]:
            errores.append("DNI parece incorrecto")

        if datos.get('correo_electronico') and '@' not in str(datos['correo_electronico']):
            errores.append("Correo electrónico parece incorrecto")

        if datos.get('numero_trabajadores'):
            try:
                num = int(datos['numero_trabajadores'])
                if num < 0:
                    errores.append("Número de trabajadores no puede ser negativo")
            except (ValueError, TypeError):
                errores.append("Número de trabajadores debe ser un número")

        return len(errores) == 0, errores
