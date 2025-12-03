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

    #### 📝 ¿Cómo funciona?

    1. **👥 Gestionar Clientes**
       - Añade clientes manualmente con todos sus datos
       - Busca clientes por razón social o CIF
       - Visualiza y administra tu base de datos

    2. **📝 Rellenar Documentos**
       - Busca y selecciona un cliente
       - Sube un formulario vacío (PDF o Word)
       - Descarga el documento completado automáticamente
       - Los archivos se borran automáticamente del servidor

    #### 💼 Campos gestionados:
    - Datos del representante legal (nombre, DNI)
    - Información de la empresa (razón social, CIF, dirección)
    - Datos operacionales (trabajadores, facturación)
    - Certificaciones (habilitaciones, ISOs, ROLECE)
    - Políticas (plan de igualdad, protocolo de acoso)

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

    # Tabs para Añadir y Ver clientes
    tab1, tab2 = st.tabs(["➕ Añadir Cliente", "📋 Ver Clientes"])

    # TAB 1: Añadir Cliente
    with tab1:
        st.subheader("Añadir Nuevo Cliente")

        with st.form("form_nuevo_cliente"):
            st.markdown("### Datos del Representante Legal")
            col1, col2 = st.columns(2)
            with col1:
                nombre_representante = st.text_input("Nombre completo*", key="nombre_rep")
            with col2:
                dni_representante = st.text_input("DNI/NIF*", key="dni_rep")

            st.markdown("### Datos de la Empresa")
            col1, col2 = st.columns(2)
            with col1:
                razon_social = st.text_input("Razón Social*", key="razon")
                cif = st.text_input("CIF*", key="cif")
                direccion = st.text_area("Dirección completa*", key="dir")
            with col2:
                correo = st.text_input("Correo electrónico*", key="email")
                num_trabajadores = st.number_input("Número de trabajadores", min_value=0, key="trabajadores")
                facturacion = st.number_input("Facturación anual (€)", min_value=0.0, step=1000.0, key="factura")

            st.markdown("### Certificaciones y Habilitaciones")
            col1, col2 = st.columns(2)
            with col1:
                habilitaciones = st.text_area("Habilitaciones (separadas por comas)", key="habil")
                isos = st.text_input("Certificaciones ISO (separadas por comas)", key="isos")
            with col2:
                rolece = st.text_input("Número ROLECE", key="rolece")

            st.markdown("### Políticas y Protocolos")
            col1, col2 = st.columns(2)
            with col1:
                plan_igualdad = st.checkbox("Plan de Igualdad", key="plan")
            with col2:
                protocolo_acoso = st.checkbox("Protocolo de Acoso", key="protocolo")

            submit = st.form_submit_button("💾 Guardar Cliente", type="primary", use_container_width=True)

            if submit:
                if not all([nombre_representante, dni_representante, razon_social, cif, direccion, correo]):
                    st.error("⚠️ Por favor, completa todos los campos obligatorios (*)")
                else:
                    try:
                        datos_cliente = {
                            'nombre_representante_legal': nombre_representante,
                            'dni_representante': dni_representante,
                            'razon_social': razon_social,
                            'cif': cif,
                            'direccion': direccion,
                            'correo_electronico': correo,
                            'numero_trabajadores': num_trabajadores,
                            'facturacion': facturacion,
                            'habilitaciones': habilitaciones if habilitaciones else None,
                            'isos': isos if isos else None,
                            'rolece': rolece if rolece else None,
                            'tiene_plan_igualdad': plan_igualdad,
                            'tiene_protocolo_acoso': protocolo_acoso
                        }
                        cliente = st.session_state.db_manager.agregar_cliente(datos_cliente)
                        st.success(f"✅ Cliente '{razon_social}' guardado correctamente (ID: {cliente.id})")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al guardar cliente: {e}")

    # TAB 2: Ver Clientes
    with tab2:
        # Obtener todos los clientes
        clientes = st.session_state.db_manager.obtener_todos_clientes()

        if not clientes:
            st.info("📭 No hay clientes registrados. Añade el primero en la pestaña 'Añadir Cliente'.")
            return

        # Buscador
        st.subheader(f"📊 Total de Clientes: {len(clientes)}")

        col1, col2 = st.columns([3, 1])
        with col1:
            buscar = st.text_input("🔍 Buscar por razón social o CIF", key="buscar_cliente", placeholder="Escribe para buscar...")
        with col2:
            st.write("")  # Espaciado
            st.write("")

        # Filtrar clientes según búsqueda
        if buscar:
            clientes_filtrados = [c for c in clientes if
                                  buscar.lower() in c.razon_social.lower() or
                                  (c.cif and buscar.lower() in c.cif.lower())]
            if clientes_filtrados:
                st.info(f"🔍 {len(clientes_filtrados)} cliente(s) encontrado(s)")
            else:
                st.warning("No se encontraron clientes con ese criterio")
        else:
            clientes_filtrados = clientes

        # Mostrar clientes
        for cliente in clientes_filtrados:
            with st.expander(f"🏢 {cliente.razon_social} - CIF: {cliente.cif}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Representante Legal**")
                    st.write(f"Nombre: {cliente.nombre_representante_legal or 'N/A'}")
                    st.write(f"DNI: {cliente.dni_representante or 'N/A'}")

                    st.markdown("**Contacto**")
                    st.write(f"Email: {cliente.correo_electronico or 'N/A'}")
                    st.write(f"Dirección: {cliente.direccion or 'N/A'}")

                with col2:
                    st.markdown("**Datos Operacionales**")
                    st.write(f"Trabajadores: {cliente.numero_trabajadores or 0}")
                    st.write(f"Facturación: {cliente.facturacion or 0} €")

                    st.markdown("**Certificaciones**")
                    st.write(f"Habilitaciones: {cliente.habilitaciones or 'N/A'}")
                    st.write(f"ISOs: {cliente.isos or 'N/A'}")
                    st.write(f"ROLECE: {cliente.rolece or 'N/A'}")

                    st.markdown("**Políticas**")
                    st.write(f"Plan Igualdad: {'✅ Sí' if cliente.tiene_plan_igualdad else '❌ No'}")
                    st.write(f"Protocolo Acoso: {'✅ Sí' if cliente.tiene_protocolo_acoso else '❌ No'}")

                # Botón para eliminar
                if st.button(f"🗑️ Eliminar Cliente", key=f"del_{cliente.id}"):
                    if st.session_state.db_manager.eliminar_cliente(cliente.id):
                        st.success("Cliente eliminado")
                        st.rerun()

def pagina_rellenar_documentos():
    """Página para rellenar documentos con datos de clientes"""
    st.title("📝 Rellenar Documentos")
    st.markdown("Sube un formulario vacío y selecciona el cliente para rellenarlo automáticamente")

    # Obtener clientes
    clientes = st.session_state.db_manager.obtener_todos_clientes()

    if not clientes:
        st.warning("⚠️ No hay clientes registrados. Ve a 'Gestionar Clientes' para añadir el primero.")
        return

    # PASO 1: Buscar y seleccionar cliente
    st.subheader("1️⃣ Selecciona el Cliente")

    col1, col2 = st.columns([3, 1])
    with col1:
        buscar_cliente = st.text_input("🔍 Buscar por razón social o CIF", key="buscar_rellenar", placeholder="Escribe para buscar...")

    # Filtrar clientes
    if buscar_cliente:
        clientes_filtrados = [c for c in clientes if
                              buscar_cliente.lower() in c.razon_social.lower() or
                              (c.cif and buscar_cliente.lower() in c.cif.lower())]
    else:
        clientes_filtrados = clientes

    if not clientes_filtrados:
        st.warning("No se encontraron clientes con ese criterio")
        return

    # Crear opciones para selectbox
    opciones_clientes = {f"🏢 {c.razon_social} - CIF: {c.cif}": c for c in clientes_filtrados}
    cliente_seleccionado_str = st.selectbox(
        "Selecciona el cliente",
        list(opciones_clientes.keys()),
        key="select_cliente"
    )
    cliente_seleccionado = opciones_clientes[cliente_seleccionado_str]

    # Mostrar datos del cliente
    with st.expander("👁️ Ver datos del cliente seleccionado"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Datos Básicos**")
            st.write(f"• Razón Social: {cliente_seleccionado.razon_social}")
            st.write(f"• CIF: {cliente_seleccionado.cif}")
            st.write(f"• Representante: {cliente_seleccionado.nombre_representante_legal}")
            st.write(f"• DNI: {cliente_seleccionado.dni_representante}")
        with col2:
            st.markdown("**Contacto**")
            st.write(f"• Email: {cliente_seleccionado.correo_electronico}")
            st.write(f"• Dirección: {cliente_seleccionado.direccion}")
            st.write(f"• Trabajadores: {cliente_seleccionado.numero_trabajadores}")
            st.write(f"• Facturación: {cliente_seleccionado.facturacion} €")

    st.markdown("---")

    # PASO 2: Subir formulario
    st.subheader("2️⃣ Sube el Formulario Vacío")

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
                            output_path
                        )

                    st.success(f"✅ {resultado['mensaje']}")

                    st.markdown("---")
                    st.subheader("3️⃣ Descarga tu Documento")

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
                        except Exception as e:
                            st.warning(f"No se pudo subir a Cloudinary: {e}")

                    # Mostrar análisis si existe
                    if 'analisis' in resultado:
                        with st.expander("📊 Ver análisis del documento"):
                            st.json(resultado['analisis'])

                    # Botón de descarga
                    with open(output_path, 'rb') as f:
                        contenido = f.read()

                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.download_button(
                                label="📥 Descargar Documento Rellenado",
                                data=contenido,
                                file_name=output_nombre,
                                mime='application/pdf' if extension == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                type="primary",
                                use_container_width=True
                            )

                    # Si está en Cloudinary, mostrar también el link
                    if cloudinary_url:
                        st.success("📤 Documento guardado en Cloudinary")
                        st.markdown(f"🔗 **Link permanente:** [Abrir en la nube]({cloudinary_url})")
                        st.caption("Este link estará disponible permanentemente en Cloudinary")

                    st.info("ℹ️ Los archivos temporales se eliminan automáticamente del servidor después de la descarga")

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
        ["🏠 Inicio", "👥 Gestionar Clientes", "📝 Rellenar Documentos"]
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
    elif pagina == "👥 Gestionar Clientes":
        pagina_gestionar_clientes()
    elif pagina == "📝 Rellenar Documentos":
        pagina_rellenar_documentos()

if __name__ == "__main__":
    main()
