import streamlit as st
from sat_core import (
    generar_sintetica,
    generar_doppler,
    procesar_señal,
    crear_figura
)

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

# ---------------- BOTÓN PRINCIPAL ----------------
if st.button("Generar y analizar señal", type="primary"):

    with st.spinner("Procesando señal..."):
        if modo == "Señal sintética sísmica":
            t, accel, fs = generar_sintetica(
                duration=duracion,
                fs=100.0,
                snr_db=snr
            )
            source = "sintetica"

        else:
            t, accel, fs = generar_doppler(
                duration=duracion,
                fs=100.0,
                f0=0.8,
                v_rel=v_rel,
                c=300.0,
                amp=0.02 * 9.81,
                snr_db=snr
            )
            source = "doppler"

        resultado = procesar_señal(source, t, accel, fs)

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

# ---------------- PIE DE PÁGINA ----------------
st.divider()
st.caption("""
Este sistema tiene fines **educativos** y **no sustituye** a los sistemas oficiales de monitoreo sísmico.
Desarrollado como modelo didáctico para la enseñanza del movimiento ondulatorio,
la modelación matemática y el pensamiento computacional.
""")
