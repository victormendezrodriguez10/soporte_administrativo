# 📄 Sistema de Soporte Administrativo

Sistema completo de gestión de clientes con extracción y rellenado automático de documentos usando Inteligencia Artificial.

## 🎯 Características

- **Extracción Automática de Datos**: Sube documentos PDF o Word y extrae automáticamente información del cliente usando IA
- **Base de Datos PostgreSQL**: Almacena toda la información de clientes de forma estructurada
- **Rellenado Automático**: Rellena formularios PDF y Word con datos guardados
- **Interfaz Intuitiva**: Aplicación web con Streamlit, fácil de usar

## 📋 Datos Gestionados

El sistema gestiona los siguientes campos por cliente:
- Nombre del representante legal y DNI
- Razón social y CIF de la empresa
- Dirección y correo electrónico
- Número de trabajadores
- Facturación anual
- Habilitaciones
- Certificaciones ISO
- Número ROLECE
- Plan de igualdad (Sí/No)
- Protocolo de acoso (Sí/No)

## 🚀 Instalación

### 1. Requisitos Previos

- Python 3.9 o superior
- PostgreSQL 12 o superior instalado y ejecutándose
- API Key de Anthropic Claude

### 2. Clonar/Descargar el proyecto

El proyecto ya está en la carpeta `soporte administrativo`

### 3. Crear entorno virtual

```bash
cd "soporte administrativo"
python3 -m venv venv
source venv/bin/activate  # En Mac/Linux
# o
venv\Scripts\activate  # En Windows
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar PostgreSQL

#### Crear base de datos:

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear la base de datos
CREATE DATABASE soporte_admin;

# Crear usuario (opcional)
CREATE USER soporte_user WITH PASSWORD 'tu_contraseña';
GRANT ALL PRIVILEGES ON DATABASE soporte_admin TO soporte_user;

# Salir
\q
```

### 6. Configurar variables de entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
DB_NAME=soporte_admin

ANTHROPIC_API_KEY=tu_api_key_de_anthropic
```

**Para obtener API Key de Anthropic:**
1. Ve a https://console.anthropic.com/
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys"
4. Crea una nueva API key
5. Cópiala en el archivo .env

### 7. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

## 📖 Uso

### 1. Extraer Datos de Documentos

1. Ve a "📥 Extraer Datos"
2. Sube un documento PDF o Word que contenga información de un cliente
3. Haz clic en "🤖 Extraer Datos con IA"
4. Revisa los datos extraídos
5. Haz clic en "💾 Guardar en Base de Datos"

### 2. Gestionar Clientes

1. Ve a "👥 Gestionar Clientes"
2. Visualiza todos los clientes guardados
3. Expande cada cliente para ver sus detalles
4. Elimina clientes si es necesario

### 3. Rellenar Documentos

1. Ve a "📝 Rellenar Documentos"
2. Selecciona un cliente de la lista
3. Sube un formulario vacío (PDF o Word)
4. Haz clic en "🎯 Rellenar Documento"
5. Descarga el documento completado

#### Tipos de formularios soportados:

**Para Word (.docx):**
- **Con marcadores**: Usa placeholders como `{{RAZON_SOCIAL}}`, `{{CIF}}`, etc.
- **Sin marcadores**: La IA identifica los campos automáticamente

**Para PDF:**
- **Formularios interactivos**: PDFs con campos de formulario nativos
- **Formularios estáticos**: La IA identifica dónde colocar los datos

## 📁 Estructura del Proyecto

```
soporte administrativo/
│
├── app.py                  # Aplicación principal Streamlit
├── requirements.txt        # Dependencias Python
├── .env.example           # Ejemplo de variables de entorno
├── README.md              # Este archivo
│
├── database/              # Módulo de base de datos
│   ├── __init__.py
│   ├── models.py         # Modelos SQLAlchemy
│   └── db_manager.py     # Gestor de base de datos
│
├── modules/               # Módulos de procesamiento
│   ├── __init__.py
│   ├── pdf_extractor.py  # Extracción de datos de PDF
│   ├── pdf_filler.py     # Rellenado de PDFs
│   └── word_handler.py   # Manejo de documentos Word
│
├── uploaded_pdfs/         # Documentos subidos
└── generated_pdfs/        # Documentos generados
```

## 🔧 Solución de Problemas

### Error: "No se encontró ANTHROPIC_API_KEY"

Asegúrate de:
1. Haber creado el archivo `.env`
2. Tener la API key correcta de Anthropic
3. Reiniciar la aplicación después de crear el archivo

### Error de conexión a PostgreSQL

Verifica que:
1. PostgreSQL esté ejecutándose: `pg_isready`
2. Las credenciales en `.env` sean correctas
3. La base de datos `soporte_admin` exista

### Los datos extraídos no son correctos

La calidad de extracción depende de:
- La claridad del documento original
- Que los campos estén claramente identificados
- Puedes editar manualmente los datos antes de guardar

## 📝 Crear Plantillas de Word con Marcadores

Para mejores resultados al rellenar documentos Word, usa estos marcadores en tus plantillas:

```
{{NOMBRE_REPRESENTANTE}}
{{DNI_REPRESENTANTE}}
{{RAZON_SOCIAL}}
{{CIF}}
{{DIRECCION}}
{{EMAIL}}
{{NUM_TRABAJADORES}}
{{FACTURACION}}
{{HABILITACIONES}}
{{ISOS}}
{{ROLECE}}
{{PLAN_IGUALDAD}}
{{PROTOCOLO_ACOSO}}
```

Ejemplo de plantilla:

```
DATOS DE LA EMPRESA

Razón Social: {{RAZON_SOCIAL}}
CIF: {{CIF}}
Dirección: {{DIRECCION}}
Email: {{EMAIL}}

Representante Legal: {{NOMBRE_REPRESENTANTE}}
DNI: {{DNI_REPRESENTANTE}}

Número de trabajadores: {{NUM_TRABAJADORES}}
Facturación anual: {{FACTURACION}} €

Certificaciones ISO: {{ISOS}}
Plan de Igualdad: {{PLAN_IGUALDAD}}
```

## 🔐 Seguridad

- Nunca compartas tu archivo `.env`
- Mantén tu API key de Anthropic segura
- Las credenciales de base de datos deben ser fuertes
- Los documentos subidos se guardan localmente

## 📊 Limitaciones Actuales

1. **PDFs no interactivos**: Para PDFs sin campos de formulario, la IA analiza dónde deberían ir los datos pero no genera el overlay automáticamente (requiere desarrollo adicional)
2. **Formatos específicos**: Algunos formatos de documentos muy complejos pueden requerir ajustes
3. **Idioma**: Optimizado para español

## 🚀 Mejoras Futuras

- [ ] Soporte para Excel
- [ ] Exportación masiva de datos
- [ ] API REST para integraciones
- [ ] Múltiples idiomas
- [ ] Editor visual de plantillas
- [ ] Historial de cambios
- [ ] Roles y permisos de usuario

## 📞 Soporte

Para problemas o sugerencias, consulta:
- Documentación de Streamlit: https://docs.streamlit.io
- Documentación de Claude API: https://docs.anthropic.com
- Documentación de SQLAlchemy: https://docs.sqlalchemy.org

## 📜 Licencia

Este proyecto es de uso interno para gestión administrativa.

---

Desarrollado con ❤️ usando Python, Streamlit y Claude AI
