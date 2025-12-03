"""
Módulo de autenticación para el Sistema de Soporte Administrativo
"""
import streamlit as st
import hashlib
import os

class AuthManager:
    def __init__(self):
        """Inicializa el gestor de autenticación"""
        # Credenciales configuradas
        self.usuarios = {
            'favoritoconcurso@oclem.com': {
                'password': 'Favorito2025',
                'nombre': 'Usuario Favorito'
            }
        }

    def verificar_credenciales(self, email: str, password: str) -> bool:
        """
        Verifica si las credenciales son correctas

        Args:
            email: Email del usuario
            password: Contraseña

        Returns:
            True si las credenciales son correctas
        """
        if email in self.usuarios:
            return self.usuarios[email]['password'] == password
        return False

    def obtener_nombre_usuario(self, email: str) -> str:
        """Obtiene el nombre del usuario"""
        if email in self.usuarios:
            return self.usuarios[email]['nombre']
        return None

    def iniciar_sesion(self, email: str, password: str) -> bool:
        """
        Inicia sesión del usuario

        Args:
            email: Email del usuario
            password: Contraseña

        Returns:
            True si el login fue exitoso
        """
        if self.verificar_credenciales(email, password):
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.session_state.user_name = self.obtener_nombre_usuario(email)
            return True
        return False

    def cerrar_sesion(self):
        """Cierra la sesión del usuario"""
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_name = None

    def esta_autenticado(self) -> bool:
        """Verifica si el usuario está autenticado"""
        return st.session_state.get('authenticated', False)

    def obtener_usuario_actual(self) -> dict:
        """Obtiene información del usuario actual"""
        if self.esta_autenticado():
            return {
                'email': st.session_state.get('user_email'),
                'nombre': st.session_state.get('user_name')
            }
        return None


def mostrar_pagina_login():
    """
    Muestra la página de login
    """
    # Centrar el formulario
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("---")
        st.title("🔐 Inicio de Sesión")
        st.markdown("### Sistema de Soporte Administrativo")
        st.markdown("---")

        # Formulario de login
        with st.form("login_form"):
            email = st.text_input(
                "📧 Correo Electrónico",
                placeholder="usuario@ejemplo.com",
                key="login_email"
            )

            password = st.text_input(
                "🔑 Contraseña",
                type="password",
                placeholder="Ingresa tu contraseña",
                key="login_password"
            )

            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

            with col_btn2:
                submit_button = st.form_submit_button(
                    "🚀 Iniciar Sesión",
                    use_container_width=True,
                    type="primary"
                )

            if submit_button:
                if email and password:
                    auth = AuthManager()
                    if auth.iniciar_sesion(email, password):
                        st.success("✅ Inicio de sesión exitoso")
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas. Por favor, intenta de nuevo.")
                else:
                    st.warning("⚠️ Por favor, completa todos los campos.")

        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666; font-size: 0.9em;'>
                <p>🔒 Sistema seguro de gestión de clientes</p>
                <p>Desarrollado con IA y tecnología en la nube</p>
            </div>
            """,
            unsafe_allow_html=True
        )
