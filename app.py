import streamlit as st
from sat_core import (
    generar_sintetica,
    generar_doppler,
    procesar_señal,
    crear_figura
)
from sat_core import (
    generar_sintetica,
    generar_doppler,
    procesar_señal,
    crear_figura,
    explicar_resultado,
    DEFAULT_CFG
)

from sat_core import DEFAULT_CFG

if "cfg" not in st.session_state:
    st.session_state.cfg = DEFAULT_CFG.copy()


# ---------------- CONFIGURACIÓN DE LA PÁGINA ----------------
st.set_page_config(
    page_title="SAT Educativo – UNIR",
    layout="wide"
)

# ---------------- ENCABEZADO ----------------
st.title("Sistema de Alerta Temprana (SAT) – Modelo Educativo")
st.markdown("""
**Modelo computacional educativo para el estudio de sismos y el efecto Doppler**  
Carrera: Física–Matemática | Didáctica STEM
""")

st.divider()

# ---------------- SELECCIÓN DE MODO ----------------
modo = st.radio(
    "Seleccione el tipo de señal a analizar:",
    ["Señal sintética sísmica", "Modo Doppler"]
)

st.divider()

st.subheader("Parámetros del modelo")

colA, colB = st.columns(2)

with colA:
    snr = st.slider("Relación señal/ruido (SNR)", 2, 20, 8)
    duracion = st.slider("Duración de la señal (s)", 60, 180, 120)

with colB:
    if modo == "Modo Doppler":
        v_rel = st.slider("Velocidad relativa de la fuente (m/s)", 0, 60, 30)
    else:
        v_rel = None

st.sidebar.header("Parámetros del modelo")

cfg = st.session_state.cfg

cfg["STA_WINDOW"] = st.sidebar.number_input(
    "Ventana STA (s)", value=cfg["STA_WINDOW"], min_value=0.1
)

cfg["LTA_WINDOW"] = st.sidebar.number_input(
    "Ventana LTA (s)", value=cfg["LTA_WINDOW"], min_value=1.0
)

cfg["STA_LTA_THRESHOLD"] = st.sidebar.number_input(
    "Umbral STA/LTA", value=cfg["STA_LTA_THRESHOLD"]
)

cfg["PGA_THRESHOLD_G"] = st.sidebar.number_input(
    "Umbral PGA (g)", value=cfg["PGA_THRESHOLD_G"]
)

cfg["FILTER_FC"] = st.sidebar.number_input(
    "Frecuencia de corte del filtro (Hz)", value=cfg["FILTER_FC"]
)

if st.sidebar.button("Restaurar valores por defecto"):
    st.session_state.cfg = DEFAULT_CFG.copy()
    st.rerun()

# ---------------- BOTÓN PRINCIPAL ----------------
if st.button("Generar y analizar señal", type="primary"):
    st.session_state.resultado = procesar_señal(
        source,
        t,
        accel,
        fs,
        st.session_state.cfg
    )
            source = "sintetica"

        else:
            t, accel, fs = generar_doppler(
                duration=duracion,
                fs=100.0,
                f0=0.8,
                v_rel=v_rel,
                c=300.0,
                snr_db=snr,
                cfg=st.session_state.cfg
            )

            source = "doppler"

        st.session_state.resultado = procesar_señal(
            source,
            t,
            accel,
            fs,
            cfg=st.session_state.cfg
        )

# ---------------- RESULTADOS ----------------

    if resultado["alert_type"] == "no_detectado":
        st.warning("No se detectó un evento sísmico significativo.")
    else:
        st.success(f"Tipo de alerta detectada: **{resultado['alert_type'].upper()}**")

        col1, col2, col3 = st.columns(3)

        col1.metric("PGA (g)", f"{resultado['pga_g']:.4f}")
        col2.metric("Magnitud estimada", resultado["magnitude"])
        col3.metric("Periodo dominante (s)", f"{resultado['dom_period']:.2f}")

        st.divider()

        fig = crear_figura(
            t,
            accel,
            resultado["accel_filt"],
            fs,
            resultado["p_time"],
            resultado["dom_freq"],
            resultado["alert_type"]
        )

        st.pyplot(fig)

if "resultado" in st.session_state:
    resultado = st.session_state.resultado

    st.subheader("Resultados")

    if resultado["alert_type"] == "no_detectado":
        st.warning("No se detectó un evento sísmico significativo.")
    else:
        st.success(f"Tipo de alerta detectada: **{resultado['alert_type']}**")

    # Mostrar gráfica
    fig = crear_figura(t, resultado["accel_filt"])
    st.pyplot(fig)

    # Interpretación pedagógica
    st.subheader("Interpretación del resultado")
    explicacion = explicar_resultado(resultado, st.session_state.cfg)
    st.info(explicacion)


# ---------------- PIE DE PÁGINA ----------------
st.divider()
st.caption("""
Este sistema tiene fines **educativos** y **no sustituye** a los sistemas oficiales de monitoreo sísmico.
Desarrollado como modelo didáctico para la enseñanza del movimiento ondulatorio,
la modelación matemática y el pensamiento computacional.
""")
