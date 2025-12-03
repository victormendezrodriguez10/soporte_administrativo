# 🚀 Guía de Inicio Rápido

## Configuración en 5 minutos

### 1️⃣ Instalar dependencias (2 minutos)

```bash
cd "soporte administrativo"

# Opción A: Usar script automático (Mac/Linux)
./setup.sh

# Opción B: Manual
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2️⃣ Configurar PostgreSQL (1 minuto)

```bash
# Instalar PostgreSQL si no lo tienes
# Mac:
brew install postgresql
brew services start postgresql

# Ubuntu:
sudo apt install postgresql
sudo systemctl start postgresql

# Crear la base de datos
psql -U postgres -c "CREATE DATABASE soporte_admin;"
```

### 3️⃣ Configurar API Key (1 minuto)

1. Ve a https://console.anthropic.com/
2. Crea una cuenta (o inicia sesión)
3. Ve a "API Keys" y crea una nueva
4. Copia la API key

### 4️⃣ Crear archivo .env (30 segundos)

Crea un archivo llamado `.env` en la carpeta del proyecto:

```bash
# Copiar ejemplo
cp .env.example .env

# Editar con tus datos
nano .env  # o usa tu editor favorito
```

Contenido del `.env`:

```
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=soporte_admin

ANTHROPIC_API_KEY=sk-ant-XXXXX...
```

### 5️⃣ Ejecutar la aplicación (10 segundos)

```bash
streamlit run app.py
```

Se abrirá en tu navegador en `http://localhost:8501`

---

## 📝 Primer Uso

### Opción A: Extraer datos de un documento existente

1. Ve a "📥 Extraer Datos"
2. Sube un PDF o Word con información de un cliente
3. La IA extraerá los datos automáticamente
4. Guarda en la base de datos

### Opción B: Crear plantillas de ejemplo

```bash
python crear_plantilla_ejemplo.py
```

Esto creará dos plantillas Word de ejemplo que puedes usar.

---

## 🎯 Flujo de Trabajo Típico

```
1. EXTRAER → Subir documento del cliente
            ↓
2. GUARDAR → Guardar datos en base de datos
            ↓
3. RELLENAR → Seleccionar cliente + subir formulario
            ↓
4. DESCARGAR → Descargar documento completado
```

---

## ⚠️ Solución Rápida de Problemas

### Error: "No se encontró ANTHROPIC_API_KEY"
**Solución:** Verifica que el archivo `.env` existe y contiene tu API key

### Error: "Could not connect to database"
**Solución:**
```bash
# Verificar que PostgreSQL está ejecutándose
pg_isready

# Si no está activo, iniciarlo:
brew services start postgresql  # Mac
sudo systemctl start postgresql  # Linux
```

### Error: "ModuleNotFoundError"
**Solución:**
```bash
# Asegúrate de que el entorno virtual está activado
source venv/bin/activate
# Reinstalar dependencias
pip install -r requirements.txt
```

---

## 📚 Documentación Completa

Lee `README.md` para información detallada sobre:
- Estructura del proyecto
- Todas las características
- Configuración avanzada
- Creación de plantillas personalizadas

---

## ✅ Checklist de Instalación

- [ ] Python 3.9+ instalado
- [ ] PostgreSQL instalado y ejecutándose
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos creada (`soporte_admin`)
- [ ] Archivo `.env` creado con credenciales
- [ ] API Key de Anthropic configurada
- [ ] Aplicación ejecutada (`streamlit run app.py`)

---

¡Listo! Ya puedes empezar a usar el sistema 🎉
