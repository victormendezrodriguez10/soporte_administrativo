# 📝 Comandos para Subir a GitHub

## Paso 1: Crear repositorio en GitHub

1. Ve a: https://github.com/new
2. Nombre: `soporte-administrativo`
3. ⚠️ **IMPORTANTE**: Marca como **PRIVADO** (para proteger la API key)
4. NO añadas README, .gitignore ni licencia
5. Click en "Create repository"

---

## Paso 2: Copiar tu usuario de GitHub

En GitHub, tu usuario aparece en la URL: `https://github.com/TU-USUARIO`

Por ejemplo, si tu perfil es `https://github.com/juanperez`, tu usuario es `juanperez`

---

## Paso 3: Ejecutar estos comandos

**Abre la terminal** y ejecuta (REEMPLAZA `TU-USUARIO` con tu usuario real):

```bash
cd "/Users/macintosh/Desktop/soporte administrativo"

# Conectar con GitHub (REEMPLAZA TU-USUARIO)
git remote add origin https://github.com/TU-USUARIO/soporte-administrativo.git

# Subir el código
git push -u origin main
```

**Ejemplo real:**
Si tu usuario es `juanperez`:
```bash
git remote add origin https://github.com/juanperez/soporte-administrativo.git
git push -u origin main
```

Te pedirá usuario y contraseña de GitHub (o token personal si tienes 2FA activado).

---

## Paso 4: Verificar

Ve a: `https://github.com/TU-USUARIO/soporte-administrativo`

Deberías ver todos tus archivos ahí.

---

## ✅ Siguiente: Publicar en Streamlit Cloud

Lee el archivo `DEPLOY_STREAMLIT.md` para las instrucciones completas.

**Resumen rápido:**

1. Ve a: https://share.streamlit.io/
2. Conecta con GitHub
3. New app > Selecciona tu repositorio
4. En Advanced Settings > Secrets:
   - Copia el contenido de `.streamlit/secrets.toml` local
   - Pégalo en el campo Secrets
5. Deploy!

Tu app estará en: `https://tu-usuario-soporte-administrativo.streamlit.app`

---

## 🔄 Para actualizar la app después

Cuando hagas cambios:

```bash
cd "/Users/macintosh/Desktop/soporte administrativo"

git add .
git commit -m "Descripción de los cambios"
git push
```

Streamlit Cloud detectará los cambios y redesplegará automáticamente.
