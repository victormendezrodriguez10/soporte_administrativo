#!/bin/bash

# Script de configuración inicial para Sistema de Soporte Administrativo

echo "🚀 Configuración del Sistema de Soporte Administrativo"
echo "=================================================="
echo ""

# Verificar Python
echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instálalo primero."
    exit 1
fi
echo "✅ Python $(python3 --version) encontrado"
echo ""

# Verificar PostgreSQL
echo "Verificando PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL no encontrado. Por favor instálalo:"
    echo "   Mac: brew install postgresql"
    echo "   Ubuntu: sudo apt install postgresql"
    exit 1
fi
echo "✅ PostgreSQL encontrado"
echo ""

# Crear entorno virtual
echo "Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "ℹ️  Entorno virtual ya existe"
fi
echo ""

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencias instaladas"
echo ""

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "Creando archivo .env..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales:"
    echo "   - Configura DB_PASSWORD con tu contraseña de PostgreSQL"
    echo "   - Configura ANTHROPIC_API_KEY con tu API key de Claude"
    echo ""
else
    echo "ℹ️  Archivo .env ya existe"
    echo ""
fi

# Crear directorios necesarios
echo "Creando directorios..."
mkdir -p uploaded_pdfs
mkdir -p generated_pdfs
echo "✅ Directorios creados"
echo ""

# Verificar base de datos
echo "Verificando base de datos..."
echo "Intenta conectarte a PostgreSQL y crea la base de datos si no existe:"
echo ""
echo "  psql -U postgres -c \"CREATE DATABASE soporte_admin;\""
echo ""

echo "=================================================="
echo "✅ Configuración completada"
echo ""
echo "Próximos pasos:"
echo "1. Edita el archivo .env con tus credenciales"
echo "2. Crea la base de datos PostgreSQL si no existe"
echo "3. Ejecuta: streamlit run app.py"
echo ""
