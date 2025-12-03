# 🚀 EMPIEZA AQUÍ - Sistema de Soporte Administrativo

## ✅ Tu aplicación está LISTA para publicar

**Credenciales configuradas:**
- Las credenciales reales están en `.streamlit/secrets.toml` (archivo local, no se sube a Git)
- Para Streamlit Cloud: configúralas en Settings > Secrets

⚠️ **IMPORTANTE DE SEGURIDAD:**
Mantén tu repositorio de GitHub como PRIVADO para proteger las credenciales configuradas localmente.

---

## 🎯 ¿Qué hace esta aplicación?

1. **Extrae datos** de PDFs o Word con IA
2. **Guarda clientes** en base de datos
3. **Rellena formularios** automáticamente
4. **Descarga documentos** completados

**Campos gestionados:**
- Representante legal, DNI, CIF
- Razón social, dirección, email
- Trabajadores, facturación
- ISOs, habilitaciones, ROLECE
- Plan de igualdad, protocolo de acoso

---

## 📋 SIGUIENTE: Publicar en 3 pasos

### PASO 1: Crear repositorio GitHub (2 min)

1. Ve a: https://github.com/new
2. Nombre: `soporte-administrativo`
3. **Marca como PRIVADO** ✅
4. NO añadas README ni .gitignore
5. Click "Create repository"

### PASO 2: Subir el código (1 min)

Abre la terminal y ejecuta (**REEMPLAZA `TU-USUARIO`**):

```bash
cd "/Users/macintosh/Desktop/soporte administrativo"

git remote add origin https://github.com/TU-USUARIO/soporte-administrativo.git

git push -u origin main
```

### PASO 3: Publicar en Streamlit Cloud (3 min)

1. Ve a: https://share.streamlit.io/
2. Inicia sesión con GitHub
3. Click "New app"
4. Selecciona:
   - Repository: `soporte-administrativo`
   - Branch: `main`
   - Main file: `app.py`
5. Click "Advanced settings" → Pestaña "Secrets"
6. Copia el contenido del archivo `.streamlit/secrets.toml` local
   - Este archivo contiene tus credenciales reales
   - NO se sube a Git por seguridad
   - Pégalo en el campo "Secrets" de Streamlit Cloud
7. Click "Deploy"
8. **Espera 2-3 minutos**

🎉 **Tu app estará en:** `https://tu-usuario-soporte-administrativo.streamlit.app`

---

## 📚 Documentación Disponible

| Archivo | Descripción |
|---------|-------------|
| `COMANDOS_GIT.md` | Comandos paso a paso para GitHub |
| `DEPLOY_STREAMLIT.md` | Guía completa de deployment |
| `README.md` | Documentación técnica completa |
| `INICIO_RAPIDO.md` | Instalación local en 5 minutos |

---

## 💾 Base de Datos y Almacenamiento

**Base de Datos:** Neon PostgreSQL (YA CONFIGURADA) ✅
- ✅ 0.5 GB gratis
- ✅ Los datos persisten entre redespliegues
- ✅ Accede en: https://console.neon.tech

**Almacenamiento:** Cloudinary (YA CONFIGURADO) ✅
- ✅ 25 GB de almacenamiento gratis
- ✅ Archivos guardados en la nube
- ✅ Accede en: https://cloudinary.com/console
- 📁 Cloud Name: dvyo9iu61

---

## 🧪 Probar localmente (opcional)

Si quieres probar antes de publicar:

```bash
cd "/Users/macintosh/Desktop/soporte administrativo"

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

Se abre en: http://localhost:8501

---

## 📱 Estructura del Proyecto

```
soporte administrativo/
├── app.py                    # ⭐ Aplicación principal
├── requirements.txt          # Dependencias
├── database/                 # Gestión de BD
│   ├── models.py            # Modelo de Cliente
│   └── db_manager.py        # Operaciones BD
├── modules/                  # Procesamiento IA
│   ├── pdf_extractor.py     # Extraer de PDF
│   ├── pdf_filler.py        # Rellenar PDF
│   └── word_handler.py      # Procesar Word
└── .streamlit/
    └── secrets.toml         # ⚠️ NO se sube a Git

Documentación:
├── EMPIEZA_AQUI.md          # ⭐ Esta guía
├── COMANDOS_GIT.md          # Comandos Git
├── DEPLOY_STREAMLIT.md      # Deployment completo
└── README.md                # Documentación técnica
```

---

## 💰 Costos

**Streamlit Cloud:** GRATIS ✅
- 1 app privada gratis
- Hosting incluido

**Neon PostgreSQL:** GRATIS ✅
- 0.5 GB de base de datos gratis
- https://console.neon.tech

**Cloudinary:** GRATIS ✅
- 25 GB de almacenamiento gratis
- https://cloudinary.com/console

**Anthropic API:** De pago 💰
- ~$3 por cada millón de tokens de entrada
- ~$15 por millón de tokens de salida
- Monitorea uso: https://console.anthropic.com/settings/usage
- Estima: ~$0.50-2 por 100 documentos procesados

---

## 🆘 ¿Necesitas ayuda?

1. **Comandos Git:** Lee `COMANDOS_GIT.md`
2. **Deployment:** Lee `DEPLOY_STREAMLIT.md`
3. **Instalación local:** Lee `INICIO_RAPIDO.md`
4. **Documentación técnica:** Lee `README.md`

---

## 🔐 Recordatorios de Seguridad

✅ Mantén el repositorio GitHub como PRIVADO
✅ No compartas el archivo `.env` o `secrets.toml`
⚠️ Considera regenerar tu API key después de publicar

---

## 🎉 ¡Ya está todo listo!

Solo sigue los 3 pasos arriba y en menos de 10 minutos tendrás tu aplicación funcionando en la nube.

**¿Listo para empezar?** Abre `COMANDOS_GIT.md` y sigue las instrucciones paso a paso.
