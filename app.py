"""
Aplicación principal de Soporte Administrativo
Sistema de gestión de clientes con extracción y rellenado automático de documentos
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from database import DatabaseManager, Cliente
from modules import PDFExtractor, PDFFiller, WordHandler, CloudinaryStorage, AuthManager, mostrar_pagina_login

# Función para obtener configuración (de secrets o .env)
def get_config(key, default=None):
    """Obtiene configuración de Streamlit secrets o variables de entorno"""
    # Primero intentar desde Streamlit secrets (para cloud)
    if hasattr(st, 'secrets') and key in st.secrets:
        return st.secrets[key]
    # Luego desde variables de entorno (para local)
    return os.getenv(key, default)

# Configuración de la página
st.set_page_config(
    page_title="Soporte Administrativo",
    page_icon="📄",
    layout="wide"
)

# Inicializar session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = None
if 'pdf_extractor' not in st.session_state:
    st.session_state.pdf_extractor = None
if 'pdf_filler' not in st.session_state:
    st.session_state.pdf_filler = None
if 'word_handler' not in st.session_state:
    st.session_state.word_handler = None
if 'cloudinary_storage' not in st.session_state:
    st.session_state.cloudinary_storage = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = AuthManager()

def inicializar_servicios():
    """Inicializa los servicios de base de datos y API"""
    try:
        # Verificar que exista la API key (desde secrets o .env)
        api_key = get_config('ANTHROPIC_API_KEY')
        if not api_key:
            st.error("⚠️ No se encontró ANTHROPIC_API_KEY. Configúrala en Settings > Secrets (Streamlit Cloud) o en .env (local)")
            st.info("En Streamlit Cloud: Settings > Secrets > Añadir ANTHROPIC_API_KEY")
            return False

        # Inicializar base de datos
        if st.session_state.db_manager is None:
            # DATABASE_URL puede venir de secrets o .env
            db_url = get_config('DATABASE_URL')
            st.session_state.db_manager = DatabaseManager(db_url=db_url)
            st.session_state.db_manager.create_tables()

        # Inicializar Cloudinary
        if st.session_state.cloudinary_storage is None:
            cloud_name = get_config('CLOUDINARY_CLOUD_NAME')
            api_key_cloud = get_config('CLOUDINARY_API_KEY')
            api_secret = get_config('CLOUDINARY_API_SECRET')

            if all([cloud_name, api_key_cloud, api_secret]):
                st.session_state.cloudinary_storage = CloudinaryStorage(cloud_name, api_key_cloud, api_secret)
            else:
                st.warning("⚠️ Cloudinary no configurado. Los archivos se guardarán localmente.")

        # Inicializar módulos de procesamiento
        if st.session_state.pdf_extractor is None:
            st.session_state.pdf_extractor = PDFExtractor(api_key)

        if st.session_state.pdf_filler is None:
            st.session_state.pdf_filler = PDFFiller(api_key)

        if st.session_state.word_handler is None:
            st.session_state.word_handler = WordHandler(api_key)

        return True

    except Exception as e:
        st.error(f"Error al inicializar servicios: {e}")
        st.exception(e)
        return False

def pagina_inicio():
    """Página de inicio con información del sistema"""
    st.title("📄 Sistema de Soporte Administrativo")
    st.markdown("---")

    st.markdown("""
    ### Bienvenido al Sistema de Gestión de Clientes

    Este sistema permite:
    - 📥 **Extraer datos** de documentos PDF y Word usando IA
    - 💾 **Guardar información** de clientes en base de datos
    - 📝 **Rellenar formularios** automáticamente con datos guardados
    - 📤 **Descargar documentos** completados

    #### Campos gestionados:
    - Nombre del representante legal y DNI
    - Razón social y CIF
    - Dirección y correo electrónico
    - Número de trabajadores y facturación
    - Habilitaciones, ISOs, ROLECE
    - Plan de igualdad y protocolo de acoso

    ### 🚀 Comienza seleccionando una opción del menú lateral
    """)

    # Estadísticas
    if st.session_state.db_manager:
        clientes = st.session_state.db_manager.obtener_todos_clientes()
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Clientes", len(clientes))

        with col2:
            clientes_con_plan = sum(1 for c in clientes if c.tiene_plan_igualdad)
            st.metric("Con Plan de Igualdad", clientes_con_plan)

        with col3:
            clientes_con_protocolo = sum(1 for c in clientes if c.tiene_protocolo_acoso)
            st.metric("Con Protocolo de Acoso", clientes_con_protocolo)

def pagina_extraer_datos():
    """Página para extraer datos de documentos"""
    st.title("📥 Extraer Datos de Documentos")
    st.markdown("Sube un documento PDF o Word para extraer automáticamente los datos del cliente")

    archivo = st.file_uploader(
        "Selecciona un documento",
        type=['pdf', 'docx'],
        help="Formatos soportados: PDF, DOCX"
    )

    if archivo:
        # Guardar archivo temporalmente para procesamiento
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(archivo.name).suffix) as tmp:
            tmp.write(archivo.getbuffer())
            archivo_path = tmp.name

        # Subir a Cloudinary si está configurado
        cloudinary_url = None
        if st.session_state.cloudinary_storage:
            try:
                resultado = st.session_state.cloudinary_storage.subir_desde_bytes(
                    archivo.getbuffer(),
                    archivo.name,
                    folder="soporte_admin/uploaded"
                )
                cloudinary_url = resultado['url']
                st.success(f"✅ Archivo subido a Cloudinary: {archivo.name}")
            except Exception as e:
                st.warning(f"No se pudo subir a Cloudinary: {e}")
        else:
            st.success(f"Archivo cargado: {archivo.name}")

        if st.button("🤖 Extraer Datos con IA", type="primary"):
            with st.spinner("Analizando documento con IA..."):
                try:
                    # Determinar tipo de archivo
                    extension = archivo.name.split('.')[-1].lower()

                    if extension == 'pdf':
                        datos = st.session_state.pdf_extractor.extraer_datos_cliente(str(archivo_path))
                    elif extension == 'docx':
                        datos = st.session_state.word_handler.extraer_datos_cliente_word(str(archivo_path))
                    else:
                        st.error("Formato no soportado")
                        return

                    st.success("✅ Datos extraídos correctamente")

                    # Mostrar datos extraídos
                    st.subheader("Datos Extraídos:")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Representante Legal**")
                        st.write(f"Nombre: {datos.get('nombre_representante_legal', 'N/A')}")
                        st.write(f"DNI: {datos.get('dni_representante', 'N/A')}")

                        st.markdown("**Empresa**")
                        st.write(f"Razón Social: {datos.get('razon_social', 'N/A')}")
                        st.write(f"CIF: {datos.get('cif', 'N/A')}")
                        st.write(f"Dirección: {datos.get('direccion', 'N/A')}")
                        st.write(f"Email: {datos.get('correo_electronico', 'N/A')}")

                    with col2:
                        st.markdown("**Datos Operacionales**")
                        st.write(f"Trabajadores: {datos.get('numero_trabajadores', 'N/A')}")
                        st.write(f"Facturación: {datos.get('facturacion', 'N/A')}")

                        st.markdown("**Certificaciones**")
                        st.write(f"Habilitaciones: {datos.get('habilitaciones', 'N/A')}")
                        st.write(f"ISOs: {datos.get('isos', 'N/A')}")
                        st.write(f"ROLECE: {datos.get('rolece', 'N/A')}")

                        st.markdown("**Políticas**")
                        st.write(f"Plan Igualdad: {'✅ Sí' if datos.get('tiene_plan_igualdad') else '❌ No'}")
                        st.write(f"Protocolo Acoso: {'✅ Sí' if datos.get('tiene_protocolo_acoso') else '❌ No'}")

                    # Guardar en session state para poder guardarlo
                    st.session_state.datos_extraidos = datos

                    if st.button("💾 Guardar en Base de Datos"):
                        try:
                            # Limpiar datos antes de guardar
                            datos_limpios = {k: v for k, v in datos.items() if k not in ['pdf_original_nombre', 'pdf_original_ruta']}
                            datos_limpios['pdf_original_nombre'] = archivo.name
                            # Guardar URL de Cloudinary si está disponible, sino ruta local
                            datos_limpios['pdf_original_ruta'] = cloudinary_url if cloudinary_url else str(archivo_path)

                            cliente = st.session_state.db_manager.agregar_cliente(datos_limpios)
                            st.success(f"✅ Cliente guardado con ID: {cliente.id}")

                            # Limpiar archivo temporal
                            try:
                                os.unlink(archivo_path)
                            except:
                                pass

                        except Exception as e:
                            st.error(f"Error al guardar: {e}")

                except Exception as e:
                    st.error(f"Error al extraer datos: {e}")

def pagina_gestionar_clientes():
    """Página para ver y gestionar clientes"""
    st.title("👥 Gestionar Clientes")

    # Obtener todos los clientes
    clientes = st.session_state.db_manager.obtener_todos_clientes()

    if not clientes:
        st.info("No hay clientes registrados. Ve a 'Extraer Datos' para añadir el primero.")
        return

    # Mostrar tabla de clientes
    st.subheader(f"Total de Clientes: {len(clientes)}")

    for cliente in clientes:
        with st.expander(f"🏢 {cliente.razon_social} - CIF: {cliente.cif}"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Representante Legal**")
                st.write(f"Nombre: {cliente.nombre_representante_legal}")
                st.write(f"DNI: {cliente.dni_representante}")

                st.markdown("**Contacto**")
                st.write(f"Email: {cliente.correo_electronico}")
                st.write(f"Dirección: {cliente.direccion}")

            with col2:
                st.markdown("**Datos Operacionales**")
                st.write(f"Trabajadores: {cliente.numero_trabajadores}")
                st.write(f"Facturación: {cliente.facturacion}")

                st.markdown("**Certificaciones**")
                st.write(f"ISOs: {cliente.isos}")
                st.write(f"ROLECE: {cliente.rolece}")

            # Botón para eliminar
            if st.button(f"🗑️ Eliminar Cliente {cliente.id}", key=f"del_{cliente.id}"):
                if st.session_state.db_manager.eliminar_cliente(cliente.id):
                    st.success("Cliente eliminado")
                    st.rerun()

def pagina_rellenar_documentos():
    """Página para rellenar documentos con datos de clientes"""
    st.title("📝 Rellenar Documentos")
    st.markdown("Selecciona un cliente y sube un formulario para rellenarlo automáticamente")

    # Obtener clientes
    clientes = st.session_state.db_manager.obtener_todos_clientes()

    if not clientes:
        st.warning("No hay clientes registrados. Primero debes extraer datos de un documento.")
        return

    # Seleccionar cliente
    opciones_clientes = {f"{c.razon_social} (CIF: {c.cif})": c for c in clientes}
    cliente_seleccionado_str = st.selectbox("Selecciona un cliente", list(opciones_clientes.keys()))
    cliente_seleccionado = opciones_clientes[cliente_seleccionado_str]

    # Mostrar datos del cliente
    with st.expander("Ver datos del cliente"):
        st.json(cliente_seleccionado.to_dict())

    # Subir formulario
    formulario = st.file_uploader(
        "Sube el formulario a rellenar",
        type=['pdf', 'docx'],
        help="Sube un formulario vacío o plantilla"
    )

    if formulario:
        st.success(f"Formulario cargado: {formulario.name}")

        # Opciones de rellenado
        extension = formulario.name.split('.')[-1].lower()

        if extension == 'docx':
            usar_marcadores = st.checkbox(
                "Usar marcadores ({{CAMPO}})",
                value=True,
                help="Si el documento usa marcadores como {{RAZON_SOCIAL}}, déjalo marcado"
            )

        if st.button("🎯 Rellenar Documento", type="primary"):
            with st.spinner("Rellenando documento..."):
                try:
                    import tempfile

                    # Guardar formulario en archivo temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(formulario.name).suffix) as tmp_input:
                        tmp_input.write(formulario.getbuffer())
                        formulario_path = tmp_input.name

                    # Generar nombre de salida
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    razon_social_limpia = cliente_seleccionado.razon_social.replace(" ", "_").replace("/", "_")
                    output_nombre = f"{razon_social_limpia}_{timestamp}.{extension}"

                    # Crear archivo temporal para output
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmp_output:
                        output_path = tmp_output.name

                    # Convertir cliente a dict
                    datos_cliente = cliente_seleccionado.to_dict()

                    # Rellenar según tipo
                    if extension == 'pdf':
                        resultado = st.session_state.pdf_filler.rellenar_pdf(
                            formulario_path,
                            datos_cliente,
                            output_path
                        )
                    elif extension == 'docx':
                        resultado = st.session_state.word_handler.rellenar_word(
                            formulario_path,
                            datos_cliente,
                            output_path,
                            usar_marcadores=usar_marcadores
                        )

                    st.success(f"✅ {resultado['mensaje']}")

                    # Subir a Cloudinary si está configurado
                    cloudinary_url = None
                    if st.session_state.cloudinary_storage:
                        try:
                            with open(output_path, 'rb') as f:
                                resultado_upload = st.session_state.cloudinary_storage.subir_desde_bytes(
                                    f.read(),
                                    output_nombre,
                                    folder="soporte_admin/generated"
                                )
                                cloudinary_url = resultado_upload['url']
                                st.info(f"📤 Documento guardado en la nube")
                        except Exception as e:
                            st.warning(f"No se pudo subir a Cloudinary: {e}")

                    # Mostrar análisis si existe
                    if 'analisis' in resultado:
                        with st.expander("Ver análisis del documento"):
                            st.json(resultado['analisis'])

                    # Botón de descarga
                    with open(output_path, 'rb') as f:
                        contenido = f.read()
                        st.download_button(
                            label="📥 Descargar Documento Rellenado",
                            data=contenido,
                            file_name=output_nombre,
                            mime='application/pdf' if extension == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        )

                    # Si está en Cloudinary, mostrar también el link
                    if cloudinary_url:
                        st.markdown(f"🔗 [Ver documento en la nube]({cloudinary_url})")

                    # Limpiar archivos temporales
                    try:
                        os.unlink(formulario_path)
                        os.unlink(output_path)
                    except:
                        pass

                except Exception as e:
                    st.error(f"Error al rellenar documento: {e}")
                    st.exception(e)

def main():
    """Función principal de la aplicación"""

    # Verificar autenticación
    if not st.session_state.auth_manager.esta_autenticado():
        # Mostrar página de login
        mostrar_pagina_login()
        return

    # Usuario autenticado - mostrar aplicación
    # Sidebar
    st.sidebar.title("📁 Menú")

    # Mostrar información del usuario
    usuario = st.session_state.auth_manager.obtener_usuario_actual()
    if usuario:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **{usuario['nombre']}**")
        st.sidebar.markdown(f"📧 {usuario['email']}")

        if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.auth_manager.cerrar_sesion()
            st.rerun()

        st.sidebar.markdown("---")

    # Inicializar servicios
    if not inicializar_servicios():
        st.stop()

    # Menú de navegación
    pagina = st.sidebar.radio(
        "Selecciona una opción:",
        ["🏠 Inicio", "📥 Extraer Datos", "👥 Gestionar Clientes", "📝 Rellenar Documentos"]
    )

    # Información de configuración
    with st.sidebar.expander("⚙️ Configuración"):
        st.write("**Base de Datos:** Neon (PostgreSQL)")
        st.write("**IA:** Claude API (Anthropic)")
        st.write("**Almacenamiento:** Cloudinary")

        if st.button("🔄 Reconectar Servicios"):
            # Mantener la sesión autenticada
            authenticated = st.session_state.authenticated
            user_email = st.session_state.get('user_email')
            user_name = st.session_state.get('user_name')

            st.session_state.clear()

            # Restaurar autenticación
            st.session_state.authenticated = authenticated
            st.session_state.user_email = user_email
            st.session_state.user_name = user_name
            st.session_state.auth_manager = AuthManager()

            st.rerun()

    # Renderizar página seleccionada
    if pagina == "🏠 Inicio":
        pagina_inicio()
    elif pagina == "📥 Extraer Datos":
        pagina_extraer_datos()
    elif pagina == "👥 Gestionar Clientes":
        pagina_gestionar_clientes()
    elif pagina == "📝 Rellenar Documentos":
        pagina_rellenar_documentos()

if __name__ == "__main__":
    main()
