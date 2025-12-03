# 🚀 Guía de Deployment en Streamlit Cloud

## ✅ Tu app ya está configurada con:
- ✅ API Key de Anthropic incluida
- ✅ Base de datos Neon (PostgreSQL gratis en la nube)
- ✅ Cloudinary para almacenamiento de archivos
- ✅ Archivos listos para Git y Streamlit Cloud

---

## 📋 Pasos para Publicar

### 1️⃣ Crear repositorio en GitHub (2 minutos)

1. Ve a https://github.com/new
2. Nombre del repositorio: `soporte-administrativo`
3. Descripción: "Sistema de gestión de clientes con IA"
4. **IMPORTANTE**: Marca como **Privado** (para proteger tu API key)
5. NO añadas README, .gitignore ni licencia (ya los tienes)
6. Haz clic en "Create repository"

### 2️⃣ Subir tu código a GitHub (1 minuto)

Abre la terminal en la carpeta del proyecto y ejecuta:

```bash
cd "/Users/macintosh/Desktop/soporte administrativo"

# Inicializar Git
git init

# Añadir todos los archivos
git add .

# Hacer commit
git commit -m "Initial commit - Sistema de Soporte Administrativo"

# Conectar con tu repositorio (REEMPLAZA 'tu-usuario' con tu usuario de GitHub)
git remote add origin https://github.com/tu-usuario/soporte-administrativo.git

# Subir código
git branch -M main
git push -u origin main
```

### 3️⃣ Desplegar en Streamlit Cloud (3 minutos)

1. **Ve a** https://share.streamlit.io/

2. **Inicia sesión** con tu cuenta de GitHub

3. **Haz clic en** "New app"

4. **Configurar la app:**
   - Repository: `tu-usuario/soporte-administrativo`
   - Branch: `main`
   - Main file path: `app.py`

5. **⚠️ IMPORTANTE - Configurar Secrets:**
   - Haz clic en "Advanced settings"
   - En la pestaña "Secrets", pega esto:

   ```toml
   # IMPORTANTE: Reemplaza estos valores con tus credenciales reales
   # Las credenciales están en el archivo .streamlit/secrets.toml (NO subido a Git)

   ANTHROPIC_API_KEY = "tu-api-key-de-anthropic"
   DATABASE_URL = "tu-url-de-base-de-datos-neon"
   CLOUDINARY_CLOUD_NAME = "tu-cloud-name"
   CLOUDINARY_API_KEY = "tu-cloudinary-api-key"
   CLOUDINARY_API_SECRET = "tu-cloudinary-api-secret"
   ```

   **Nota:** Las credenciales reales están configuradas en el archivo local `.streamlit/secrets.toml` que no se sube a Git por seguridad.

6. **Haz clic en "Deploy"**

7. **Espera 2-3 minutos** mientras se instalan las dependencias

8. **¡Listo!** Tu app estará en: `https://tu-usuario-soporte-administrativo.streamlit.app`

---

## 🗄️ Base de Datos y Almacenamiento

### ✅ Base de Datos: Neon (PostgreSQL) - YA CONFIGURADA

Tu aplicación ya está configurada con Neon PostgreSQL:
- ✅ 0.5 GB gratis
- ✅ PostgreSQL serverless
- ✅ Los datos persisten entre redespliegues
- ✅ Escalado automático

**Accede a tu base de datos:**
1. Ve a https://console.neon.tech
2. Inicia sesión con tu cuenta
3. Visualiza tus datos, ejecuta queries SQL
4. Monitorea el uso

**Credenciales configuradas:**
```
Host: ep-floral-base-agevp7yk-pooler.c-2.eu-central-1.aws.neon.tech
Database: neondb
User: neondb_owner
```

### ✅ Almacenamiento: Cloudinary - YA CONFIGURADO

Tu aplicación ya está configurada con Cloudinary:
- ✅ 25 GB de almacenamiento gratis
- ✅ Los archivos se guardan en la nube
- ✅ URLs públicas para compartir documentos
- ✅ Respaldo automático

**Accede a tus archivos:**
1. Ve a https://cloudinary.com/console
2. Inicia sesión con tu cuenta
3. Navega a "Media Library"
4. Verás tus documentos en:
   - `soporte_admin/uploaded` - Documentos subidos por clientes
   - `soporte_admin/generated` - Formularios rellenados

**Cloud Name:** dvyo9iu61

### Alternativas (si quieres cambiar):

**Supabase (PostgreSQL):**
- 500 MB gratis
- Interfaz web amigable
- https://supabase.com

**Neon (ya usas este):**
- 0.5 GB gratis
- PostgreSQL serverless
- https://neon.tech

---

## 🔄 Actualizar la App

Cuando hagas cambios en el código:

```bash
cd "/Users/macintosh/Desktop/soporte administrativo"

git add .
git commit -m "Descripción de los cambios"
git push

# Streamlit Cloud detectará los cambios y redesplegará automáticamente
```

---

## 🔒 Seguridad - IMPORTANTE

### ⚠️ Tu API Key está expuesta en este documento

**POR SEGURIDAD, deberías:**

1. **Regenerar tu API key:**
   - Ve a https://console.anthropic.com/settings/keys
   - Elimina la key actual
   - Crea una nueva
   - Actualiza los secrets en Streamlit Cloud

2. **Mantener el repo privado en GitHub**

3. **No compartir el archivo .env o secrets.toml**

---

## 🐛 Solución de Problemas

### Error: "Module not found"
- Verifica que `requirements.txt` esté en la raíz
- Reboot la app desde Streamlit Cloud

### Error: "No se encontró ANTHROPIC_API_KEY"
- Verifica que configuraste los Secrets en Streamlit Cloud
- Settings > Secrets > Añadir ANTHROPIC_API_KEY

### La app es muy lenta
- Anthropic API puede ser lenta con PDFs grandes
- Considera actualizar el modelo en el código

### Los datos desaparecen
- Si usas SQLite, los datos se borran al redesplegar
- Migra a Supabase o Neon para persistencia

---

## 📊 Límites del Plan Gratuito

**Streamlit Cloud (Gratis):**
- 1 app privada
- 3 apps públicas
- Recursos limitados (1 GB RAM)

**Anthropic API:**
- Pago por uso
- ~$3 por cada millón de tokens de entrada
- Monitorea tu uso en: https://console.anthropic.com/settings/usage

**Supabase (Gratis):**
- 500 MB de base de datos
- 1 GB de transferencia/mes
- 2 proyectos activos

---

## 🎉 ¡Ya está!

Tu app debería estar funcionando en:
`https://tu-usuario-soporte-administrativo.streamlit.app`

Comparte el link con tu equipo (asegúrate de que el repo sea privado si tiene datos sensibles).

---

## 📞 Soporte

- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Anthropic Docs**: https://docs.anthropic.com
- **Supabase Docs**: https://supabase.com/docs
