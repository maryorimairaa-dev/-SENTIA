
# ============================================================
# SENTIA - Sistema Inteligente para la Deteccion y Gestion
# de Necesidades Urbanas
# Proyecto: Chiclayo, Lambayeque - Peru
# ============================================================

import os
import sqlite3
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import folium
import plotly.express as px
from streamlit_folium import st_folium


# ------------------------------------------------------------
# 1. CONFIGURACIoN GENERAL
# ------------------------------------------------------------

st.set_page_config(
    page_title="SENTIA | Gestión Urbana",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

NOMBRE_APP = "SENTIA"
SUBTITULO = "Sistema Inteligente para la Detección y Gestión de Necesidades Urbanas"
CIUDAD = "Chiclayo, Lambayeque - Perú"

CARPETA_DATOS = "database"
ARCHIVO_BD = os.path.join(CARPETA_DATOS, "sentia.db")

CATEGORIAS = [
    "Residuos acumulados",
    "Falla de alumbrado público",
    "Calles deterioradas",
    "Inundaciones y aniegos",
    "Otros problemas urbanos"
]

ESTADOS = [
    "Recibido",
    "En revisión",
    "En proceso",
    "Atendido"
]


# ------------------------------------------------------------
# 2. ESTILOS DE LA INTERFAZ
# ------------------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FB;
    }

    section[data-testid="stSidebar"] {
        background-color: #102B46;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .sentia-header {
        background: linear-gradient(115deg, #102B46, #176B87);
        padding: 28px;
        border-radius: 16px;
        color: white;
        margin-bottom: 22px;
    }

    .sentia-header h1 {
        color: white;
        font-size: 38px;
        margin-bottom: 4px;
    }

    .sentia-header p {
        color: #E5F2F8;
        margin: 0;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E4EAF0;
        padding: 16px;
        border-radius: 12px;
    }

    h1, h2, h3 {
        color: #163A56;
    }

    .stButton > button {
        border-radius: 9px;
        font-weight: 600;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# 3. BASE DE DATOS
# ------------------------------------------------------------

def conectar_bd():
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    conexion = sqlite3.connect(ARCHIVO_BD)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_bd():
    conexion = conectar_bd()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_ciudadano TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            ubicacion TEXT NOT NULL,
            latitud REAL NOT NULL,
            longitud REAL NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Recibido',
            fecha TEXT NOT NULL,
            fotografia BLOB
        )
    """)

    conexion.commit()
    conexion.close()


# ------------------------------------------------------------
# 4. REGISTRO Y CONSULTA DE REPORTES
# ------------------------------------------------------------

def registrar_reporte(
    nombre,
    categoria,
    descripcion,
    ubicacion,
    latitud,
    longitud,
    fotografia
):
    conexion = conectar_bd()

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conexion.execute("""
        INSERT INTO reportes (
            nombre_ciudadano,
            categoria,
            descripcion,
            ubicacion,
            latitud,
            longitud,
            estado,
            fecha,
            fotografia
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nombre,
        categoria,
        descripcion,
        ubicacion,
        latitud,
        longitud,
        "Recibido",
        fecha_actual,
        fotografia
    ))

    conexion.commit()
    conexion.close()


def obtener_reportes():
    conexion = conectar_bd()

    datos = pd.read_sql_query(
        "SELECT * FROM reportes ORDER BY fecha DESC",
        conexion
    )

    conexion.close()
    return datos


def cambiar_estado(id_reporte, nuevo_estado):
    conexion = conectar_bd()

    conexion.execute("""
        UPDATE reportes
        SET estado = ?
        WHERE id = ?
    """, (nuevo_estado, id_reporte))

    conexion.commit()
    conexion.close()


def eliminar_reporte(id_reporte):
    conexion = conectar_bd()

    conexion.execute(
        "DELETE FROM reportes WHERE id = ?",
        (id_reporte,)
    )

    conexion.commit()
    conexion.close()


# ------------------------------------------------------------
# 5. FUNCIONES AUXILIARES
# ------------------------------------------------------------

def obtener_color(categoria):
    colores = {
        "Residuos acumulados": "green",
        "Falla de alumbrado público": "orange",
        "Calles deterioradas": "red",
        "Inundaciones y aniegos": "blue",
        "Otros problemas urbanos": "purple"
    }

    return colores.get(categoria, "gray")


def preparar_datos():
    datos = obtener_reportes()

    if not datos.empty:
        datos["fecha"] = pd.to_datetime(
            datos["fecha"],
            errors="coerce"
        )

    return datos


def mostrar_encabezado():
    st.markdown(f"""
        <div class="sentia-header">
            <h1>🏙️ {NOMBRE_APP}</h1>
            <p>{SUBTITULO}</p>
            <p>📍 {CIUDAD}</p>
        </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------
# 6. INICIO DE LA APLICACIÓN
# ------------------------------------------------------------

inicializar_bd()
datos = preparar_datos()

with st.sidebar:
    st.markdown("# 🌿 SENTIA")
    st.caption("Plataforma de gestión urbana")
    st.divider()

    pagina = st.radio(
        "MENÚ PRINCIPAL",
        [
            "Inicio",
            "Registrar incidencia",
            "Mapa de incidencias",
            "Gestión de reportes",
            "Análisis y estadísticas",
            "Acerca del proyecto"
        ]
    )

    st.divider()
    st.markdown("**Ubicación del proyecto**")
    st.write("📍 Chiclayo")
    st.write("📌 Lambayeque, Perú")
    st.divider()
    st.caption("SENTIA | Versión inicial")


# ------------------------------------------------------------
# 7. PÁGINA DE INICIO
# ------------------------------------------------------------

if pagina == "Inicio":

    mostrar_encabezado()

    st.subheader("Panel general de incidencias")
    st.write(
        "Consulta el estado de los problemas urbanos "
        "registrados en la ciudad de Chiclayo."
    )

    total = len(datos)

    recibidos = (
        len(datos[datos["estado"] == "Recibido"])
        if not datos.empty else 0
    )

    en_proceso = (
        len(datos[datos["estado"] == "En proceso"])
        if not datos.empty else 0
    )

    atendidos = (
        len(datos[datos["estado"] == "Atendido"])
        if not datos.empty else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total de reportes", total)
    col2.metric("Recibidos", recibidos)
    col3.metric("En proceso", en_proceso)
    col4.metric("Atendidos", atendidos)

    st.divider()

    izquierda, derecha = st.columns([1.5, 1])

    with izquierda:
        st.subheader("Últimas incidencias")

        if datos.empty:
            st.info(
                "Todavía no hay reportes registrados. "
                "Puedes comenzar desde Registrar incidencia."
            )
        else:
            recientes = datos.head(6).copy()

            recientes["fecha"] = recientes["fecha"].dt.strftime(
                "%d/%m/%Y %H:%M"
            )

            st.dataframe(
                recientes[
                    [
                        "id",
                        "categoria",
                        "ubicacion",
                        "estado",
                        "fecha"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

    with derecha:
        st.subheader("Estado de atención")

        if not datos.empty:
            resumen = (
                datos["estado"]
                .value_counts()
                .reset_index()
            )

            resumen.columns = ["Estado", "Cantidad"]

            figura = px.pie(
                resumen,
                names="Estado",
                values="Cantidad",
                hole=0.55,
                title="Distribución de reportes"
            )

            figura.update_layout(
                margin=dict(t=45, b=10, l=10, r=10)
            )

            st.plotly_chart(
                figura,
                use_container_width=True
            )
        else:
            st.info("El gráfico aparecerá cuando existan reportes.")


# ------------------------------------------------------------
# 8. REGISTRAR INCIDENCIA
# ------------------------------------------------------------

elif pagina == "Registrar incidencia":

    mostrar_encabezado()

    st.subheader("📝 Registrar un problema urbano")

    st.write(
        "Completa los datos para registrar una incidencia "
        "detectada en tu barrio o zona de Chiclayo."
    )

    with st.form("formulario_reporte", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input(
                "Nombre del ciudadano",
                placeholder="Escribe tu nombre"
            )

            categoria = st.selectbox(
                "Tipo de problema",
                CATEGORIAS
            )

            ubicacion = st.text_input(
                "Ubicación o referencia",
                placeholder="Ejemplo: avenida Balta, Chiclayo"
            )

        with col2:
            latitud = st.number_input(
                "Latitud",
                value=-6.7714,
                format="%.6f"
            )

            longitud = st.number_input(
                "Longitud",
                value=-79.8409,
                format="%.6f"
            )

        descripcion = st.text_area(
            "Descripción de la incidencia",
            placeholder=(
                "Explica qué problema observaste "
                "y proporciona detalles de su ubicación."
            ),
            height=120
        )

        fotografia = st.file_uploader(
            "Adjuntar fotografía (opcional)",
            type=["jpg", "jpeg", "png"]
        )

        enviar = st.form_submit_button(
            "Registrar incidencia",
            use_container_width=True
        )

        if enviar:

            if not nombre.strip():
                st.error("Debes ingresar el nombre del ciudadano.")

            elif not ubicacion.strip():
                st.error("Debes indicar la ubicación del problema.")

            elif not descripcion.strip():
                st.error("Debes escribir una descripción.")

            elif not (-90 <= latitud <= 90):
                st.error("La latitud ingresada no es válida.")

            elif not (-180 <= longitud <= 180):
                st.error("La longitud ingresada no es válida.")

            else:
                imagen_bytes = (
                    fotografia.getvalue()
                    if fotografia is not None
                    else None
                )

                registrar_reporte(
                    nombre.strip(),
                    categoria,
                    descripcion.strip(),
                    ubicacion.strip(),
                    latitud,
                    longitud,
                    imagen_bytes
                )

                st.success(
                    "¡La incidencia se registró correctamente!"
                )

                st.info(
                    "El reporte se encuentra en estado: Recibido."
                )


# ------------------------------------------------------------
# 9. MAPA INTERACTIVO
# ------------------------------------------------------------

elif pagina == "Mapa de incidencias":

    mostrar_encabezado()

    st.subheader("🗺️ Mapa de incidencias urbanas")

    st.write(
        "Visualiza los puntos donde se han registrado "
        "problemas urbanos."
    )

    if datos.empty:

        st.info(
            "No existen incidencias para mostrar en el mapa. "
            "Registra un reporte para visualizarlo."
        )

    else:

        mapa = folium.Map(
            location=[-6.7714, -79.8409],
            zoom_start=13,
            tiles="OpenStreetMap"
        )

        for _, reporte in datos.iterrows():

            color = obtener_color(reporte["categoria"])

            contenido = f"""
            <b>Reporte N.º:</b> {reporte['id']}<br>
            <b>Problema:</b> {reporte['categoria']}<br>
            <b>Ubicación:</b> {reporte['ubicacion']}<br>
            <b>Estado:</b> {reporte['estado']}<br>
            <b>Fecha:</b> {reporte['fecha']}
            """

            folium.Marker(
                location=[
                    float(reporte["latitud"]),
                    float(reporte["longitud"])
                ],
                popup=folium.Popup(
                    contenido,
                    max_width=300
                ),
                tooltip=reporte["categoria"],
                icon=folium.Icon(
                    color=color,
                    icon="info-sign"
                )
            ).add_to(mapa)

        st_folium(
            mapa,
            width=None,
            height=570,
            key="mapa_sentia"
        )

        st.caption(
            "Mapa basado en OpenStreetMap. Los marcadores "
            "corresponden a las coordenadas introducidas "
            "al registrar cada incidencia."
        )

        st.markdown("**Leyenda de categorías**")

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.markdown("🟢 Residuos")
        col2.markdown("🟠 Alumbrado")
        col3.markdown("🔴 Calles")
        col4.markdown("🔵 Inundaciones")
        col5.markdown("🟣 Otros")


# ------------------------------------------------------------
# 10. GESTIÓN DE REPORTES
# ------------------------------------------------------------

elif pagina == "Gestión de reportes":

    mostrar_encabezado()

    st.subheader("📋 Administración de incidencias")

    st.write(
        "Consulta los reportes y actualiza su estado "
        "de atención."
    )

    datos = preparar_datos()

    if datos.empty:

        st.info("No hay reportes registrados todavía.")

    else:

        filtro_estado = st.selectbox(
            "Filtrar por estado",
            ["Todos"] + ESTADOS
        )

        if filtro_estado == "Todos":
            filtrados = datos.copy()
        else:
            filtrados = datos[
                datos["estado"] == filtro_estado
            ].copy()

        tabla = filtrados.drop(
            columns=["fotografia"],
            errors="ignore"
        )

        st.dataframe(
            tabla,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Actualizar estado de un reporte")

        ids = filtrados["id"].tolist()

        if ids:

            id_seleccionado = st.selectbox(
                "Selecciona el número de reporte",
                ids
            )

            reporte = datos[
                datos["id"] == id_seleccionado
            ].iloc[0]

            st.write(f"**Problema:** {reporte['categoria']}")
            st.write(f"**Ubicación:** {reporte['ubicacion']}")
            st.write(f"**Estado actual:** {reporte['estado']}")

            nuevo_estado = st.selectbox(
                "Nuevo estado",
                ESTADOS,
                index=ESTADOS.index(reporte["estado"])
            )

            if st.button(
                "Guardar actualización",
                use_container_width=True
            ):

                cambiar_estado(
                    id_seleccionado,
                    nuevo_estado
                )

                st.success(
                    "El estado del reporte se actualizó correctamente."
                )

                st.rerun()

        st.divider()

        st.subheader("Consultar fotografía")

        reportes_con_foto = datos[
            datos["fotografia"].notna()
        ]

        if not reportes_con_foto.empty:

            id_foto = st.selectbox(
                "Selecciona un reporte con fotografía",
                reportes_con_foto["id"].tolist(),
                key="selector_fotografia"
            )

            conexion = conectar_bd()

            resultado = conexion.execute(
                "SELECT fotografia FROM reportes WHERE id = ?",
                (id_foto,)
            ).fetchone()

            conexion.close()

            if resultado and resultado["fotografia"]:
                st.image(
                    resultado["fotografia"],
                    caption=f"Fotografía del reporte N.º {id_foto}",
                    width=450
                )

        else:
            st.caption(
                "Todavía no se han adjuntado fotografías."
            )

        st.divider()

        st.subheader("Eliminar un reporte")

        with st.expander("Abrir opción de eliminación"):

            st.warning(
                "Esta acción elimina el reporte seleccionado "
                "de la base de datos."
            )

            id_eliminar = st.selectbox(
                "Número de reporte que deseas eliminar",
                datos["id"].tolist(),
                key="eliminar_reporte"
            )

            confirmar = st.checkbox(
                "Confirmo que deseo eliminar este reporte."
            )

            if st.button("Eliminar reporte"):

                if confirmar:
                    eliminar_reporte(id_eliminar)
                    st.success("Reporte eliminado.")
                    st.rerun()
                else:
                    st.error(
                        "Marca la casilla de confirmación primero."
                    )

        st.divider()

        csv = tabla.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ Descargar reportes en CSV",
            data=csv,
            file_name="reportes_sentia.csv",
            mime="text/csv"
        )


# ------------------------------------------------------------
# 11. ANÁLISIS Y ESTADÍSTICAS
# ------------------------------------------------------------

elif pagina == "Análisis y estadísticas":

    mostrar_encabezado()

    st.subheader("📊 Análisis de problemas urbanos")

    st.write(
        "Observa la frecuencia de las incidencias "
        "y su estado de atención."
    )

    datos = preparar_datos()

    if datos.empty:

        st.info(
            "Aún no hay información suficiente para generar "
            "estadísticas. Registra algunas incidencias primero."
        )

    else:

        col1, col2 = st.columns(2)

        with col1:

            conteo_categoria = (
                datos["categoria"]
                .value_counts()
                .reset_index()
            )

            conteo_categoria.columns = [
                "Categoría",
                "Cantidad"
            ]

            grafico_barras = px.bar(
                conteo_categoria,
                x="Categoría",
                y="Cantidad",
                color="Categoría",
                title="Incidencias por categoría",
                text="Cantidad"
            )

            grafico_barras.update_layout(
                showlegend=False,
                xaxis_title="Tipo de problema",
                yaxis_title="Número de reportes"
            )

            st.plotly_chart(
                grafico_barras,
                use_container_width=True
            )

        with col2:

            conteo_estado = (
                datos["estado"]
                .value_counts()
                .reset_index()
            )

            conteo_estado.columns = [
                "Estado",
                "Cantidad"
            ]

            grafico_estado = px.pie(
                conteo_estado,
                names="Estado",
                values="Cantidad",
                hole=0.45,
                title="Reportes según su estado"
            )

            st.plotly_chart(
                grafico_estado,
                use_container_width=True
            )

        st.divider()

        st.subheader("📅 Reportes de los últimos siete días")

        fecha_limite = datetime.now() - timedelta(days=7)

        ultimos_dias = datos[
            datos["fecha"] >= fecha_limite
        ]

        st.metric(
            "Incidencias registradas en los últimos 7 días",
            len(ultimos_dias)
        )

        if not ultimos_dias.empty:

            conteo_semanal = (
                ultimos_dias["categoria"]
                .value_counts()
                .reset_index()
            )

            conteo_semanal.columns = [
                "Categoría",
                "Cantidad"
            ]

            st.dataframe(
                conteo_semanal,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No se han registrado incidencias durante "
                "los últimos siete días."
            )

        st.divider()

        st.subheader("🚨 Alertas por repetición de incidencias")

        if not ultimos_dias.empty:

            repetidos = ultimos_dias["categoria"].value_counts()

            hay_alerta = False

            for categoria, cantidad in repetidos.items():

                if cantidad >= 3:

                    hay_alerta = True

                    st.warning(
                        f"Se registraron {cantidad} incidencias "
                        f"de tipo '{categoria}' en los últimos "
                        "siete días. Se recomienda revisar "
                        "la zona afectada."
                    )

            if not hay_alerta:

                st.success(
                    "No se detectaron categorías con tres "
                    "o más reportes en los últimos siete días."
                )

        else:

            st.info(
                "Se necesitan reportes recientes para evaluar "
                "la repetición de incidencias."
            )

        st.caption(
            "Las alertas de esta versión se generan mediante "
            "reglas de frecuencia. No representan predicciones "
            "realizadas por un modelo de inteligencia artificial."
        )


# ------------------------------------------------------------
# 12. ACERCA DEL PROYECTO
# ------------------------------------------------------------

elif pagina == "Acerca del proyecto":

    mostrar_encabezado()

    st.subheader("Acerca de SENTIA")

    st.write(
        "SENTIA es una propuesta de plataforma inteligente "
        "orientada a la detección y gestión de necesidades "
        "urbanas en la ciudad de Chiclayo."
    )

    st.markdown("### 🎯 Objetivo general")

    st.write(
        "Facilitar la identificación, el registro y el seguimiento "
        "de problemas urbanos mediante herramientas digitales "
        "que permitan organizar la información y apoyar "
        "la toma de decisiones."
    )

    st.markdown("### 🏙️ Problemática que aborda")

    st.write(
        "En diferentes sectores urbanos pueden presentarse "
        "situaciones que afectan la calidad de vida de los "
        "ciudadanos, como la acumulación de residuos, las fallas "
        "de alumbrado público, el deterioro de las calles "
        "y las inundaciones."
    )

    st.markdown("### ⚙️ Funcionalidades principales")

    funcionalidades = [
        "Registro de incidencias ciudadanas.",
        "Clasificación de problemas urbanos.",
        "Almacenamiento de reportes en una base de datos.",
        "Visualización de incidencias en un mapa interactivo.",
        "Seguimiento del estado de atención.",
        "Análisis estadístico de los reportes.",
        "Generación de alertas por repetición de incidencias."
    ]

    for elemento in funcionalidades:
        st.markdown(f"- {elemento}")

    
    st.dataframe(
        tecnologias,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### 🔭 Mejoras previstas")

    st.write(
        "En futuras versiones se plantea incorporar sensores "
        "IoT, mecanismos de análisis más avanzados, modelos "
        "predictivos, acceso para diferentes tipos de usuarios "
        "y una base de datos centralizada."
    )

    st.info(
        "La versión actual constituye una primera implementación "
        "funcional. Las funciones de sensores físicos e "
        "inteligencia artificial predictiva todavía no están "
        "integradas."
    )


# ------------------------------------------------------------
# 13. PIE DE PÁGINA
# ------------------------------------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#718096; padding:12px;">
        <strong>SENTIA</strong><br>
        Sistema Inteligente para la Detección y Gestión de
        Necesidades Urbanas<br>
        Chiclayo - Lambayeque, Perú
    </div>
    """,
    unsafe_allow_html=True
)
  