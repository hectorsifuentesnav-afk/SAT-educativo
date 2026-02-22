import numpy as np
import scipy.signal as signal
from scipy.stats import kurtosis
import matplotlib.pyplot as plt

# ---------------- CONFIGURACIÓN POR DEFECTO ----------------
DEFAULT_CFG = {
    "G": 9.81,
    "SAMPLE_RATE": 100.0,
    "STA_WINDOW": 1.0,
    "LTA_WINDOW": 30.0,
    "STA_LTA_THRESHOLD": 3.0,
    "PGA_THRESHOLD_G": 0.05,
    "TSUNAMI_MAGNITUDE_THRESHOLD": 7.0,
    "TSUNAMI_PERIOD_THRESHOLD": 10.0,
    "FILTER_FC": 20.0
}


# ---------------- SEÑAL SINTÉTICA ----------------
def generar_sintetica(duration=120.0, fs=100.0, snr_db=10.0, cfg=None):
    if cfg is None:
        cfg = DEFAULT_CFG

    G = cfg["G"]
    t = np.arange(0.0, duration, 1.0 / fs)
    señal = np.zeros_like(t)

    # Componentes oscilatorios amortiguados
    for _ in range(np.random.randint(1, 4)):
        f = 10 ** np.random.uniform(np.log10(0.2), np.log10(8.0))
        amp = 10 ** np.random.uniform(np.log10(0.0005), np.log10(0.01)) * G
        damping = np.random.uniform(0.0002, 0.005)
        phase = np.random.uniform(0, 2 * np.pi)
        señal += amp * np.sin(2 * np.pi * f * t + phase) * np.exp(-damping * t)

    # Pulsos tipo P (claros y detectables)
    for _ in range(np.random.randint(1, 3)):
        p_time = np.random.uniform(5.0, duration - 5.0)
        p_idx = int(p_time * fs)
        pulse_len = int(np.random.uniform(0.2, 0.6) * fs)
        amp = np.random.uniform(0.02, 0.06) * G
        window = signal.windows.tukey(pulse_len, alpha=0.5)

        end = min(len(t), p_idx + pulse_len)
        señal[p_idx:end] += amp * window[: end - p_idx]

    # Ruido controlado por SNR
    rms_signal = np.sqrt(np.mean(señal ** 2)) + 1e-12
    snr_linear = 10 ** (snr_db / 20.0)
    ruido = np.random.normal(0.0, rms_signal / snr_linear, size=señal.shape)

    return t, señal + ruido, fs


# ---------------- MODO DOPPLER ----------------
def generar_doppler(duration=120.0, fs=100.0, f0=0.8, v_rel=30.0, c=300.0, amp=None, snr_db=8.0, cfg=None):
    if cfg is None:
        cfg = DEFAULT_CFG
    if amp is None:
        amp = 0.02 * cfg["G"]

    t = np.arange(0.0, duration, 1.0/fs)
    v_t = np.linspace(-v_rel, v_rel, len(t))
    v_t = np.clip(v_t, -0.9*c, 0.9*c)

    inst_freq = f0 * (c / (c - v_t))
    phase = 2*np.pi*np.cumsum(inst_freq)/fs
    señal = amp * np.sin(phase) * np.exp(-0.005*t)

    rms_signal = np.sqrt(np.mean(señal**2)) + 1e-12
    snr_linear = 10**(snr_db/20.0)
    ruido = np.random.normal(0.0, rms_signal/snr_linear, size=señal.shape)

    return t, señal + ruido, fs


# ---------------- FILTRO ----------------
def filtro_pasabajos(accel, fs, cfg):
    nyq = 0.5 * fs
    wn = min(cfg["FILTER_FC"] / nyq, 0.99)
    b, a = signal.butter(4, wn, btype='low')
    return signal.filtfilt(b, a, accel)

# ---------------- STA/LTA ----------------
def sta_lta(accel, fs, cfg):
    nsta = int(cfg["STA_WINDOW"] * fs)
    nlta = int(cfg["LTA_WINDOW"] * fs)
    sq = accel**2
    sta = np.convolve(sq, np.ones(nsta)/nsta, mode='same')
    lta = np.convolve(sq, np.ones(nlta)/nlta, mode='same')
    return sta / (lta + 1e-12)

def detectar_p(ratio, t, cfg):
    threshold = cfg["STA_LTA_THRESHOLD"]
    idx = np.argmax(ratio > threshold)
    if ratio[idx] > threshold:
        return t[idx], idx
    return None, None


# ---------------- PARÁMETROS SÍSMICOS ----------------
def calcular_pga(accel):
    return np.max(np.abs(accel))

def frecuencia_dominante(accel, fs):
    n = len(accel)
    fft = np.abs(np.fft.rfft(accel * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1/fs)
    idx = np.argmax(fft[1:]) + 1
    f = freqs[idx]
    return f, 1.0/f if f > 0 else np.inf

def estimar_magnitud(pga):
    pga_mm = pga * 1000
    return round(np.log10(pga_mm) + 0.5, 2) if pga_mm > 0 else 0.0

def clasificar_alerta(pga_g, mag, period, cfg):
    if pga_g < cfg["PGA_THRESHOLD_G"]:
        return "ruido"
    if mag >= cfg["TSUNAMI_MAGNITUDE_THRESHOLD"] and period >= cfg["TSUNAMI_PERIOD_THRESHOLD"]:
        return "tsunami"
    return "sismica"

def explicar_resultado(resultado, cfg):
    if resultado["alert_type"] == "no_detectado":
        return (
            "No se detectó un evento sísmico significativo. "
            "Esto puede deberse a una baja amplitud de la señal o a un nivel alto de ruido, "
            "lo que impide que el algoritmo STA/LTA supere el umbral configurado."
        )

    texto = []

    texto.append(
        f"Se detectó un evento con una aceleración pico (PGA) de "
        f"{resultado['pga_g']:.4f} g."
    )

    if resultado["pga_g"] < cfg["PGA_THRESHOLD_G"]:
        texto.append(
            "La aceleración es baja, por lo que el sistema clasifica el evento como ruido."
        )
    else:
        texto.append(
            "La aceleración supera el umbral configurado, indicando un evento sísmico real."
        )

    texto.append(
        f"El periodo dominante de la señal es de {resultado['dom_period']:.2f} s, "
        "lo cual está relacionado con la frecuencia principal del movimiento del suelo."
    )

    if resultado["alert_type"] == "tsunami":
        texto.append(
            "Debido a la combinación de alta magnitud y periodo largo, "
            "el sistema identifica un posible escenario de tsunami."
        )
    else:
        texto.append(
            "El periodo dominante no corresponde a un escenario típico de tsunami."
        )

    return " ".join(texto)

# ---------------- PROCESAMIENTO ----------------
def procesar_señal(source, t, accel, fs, cfg):
    accel_f = filtro_pasabajos(accel, fs, cfg)
    ratio = sta_lta(accel_f, fs, cfg)
    p_time, p_idx = detectar_p(ratio, t, cfg)

    if p_time is None:
        return {
            "alert_type": "no_detectado",
            "accel_filt": accel_f,
            "p_time": None,
            "dom_freq": None,
            "dom_period": None
        }

    segmento = accel_f[p_idx:p_idx + int(10*fs)]
    pga = calcular_pga(segmento)
    pga_g = pga / cfg["G"]
    dom_f, dom_p = frecuencia_dominante(segmento, fs)
    mag = estimar_magnitud(pga)
    alert = clasificar_alerta(pga_g, mag, dom_p, cfg)

    return {
        "alert_type": alert,
        "accel_filt": accel_f,
        "p_time": p_time,
        "dom_freq": dom_f,
        "dom_period": dom_p,
        "pga_g": pga_g,
        "magnitude": mag
    }


# ---------------- FIGURA ----------------
def crear_figura(t, accel_raw, accel_filt, fs, p_time, dom_freq, alert):
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))

    ax[0].plot(t, accel_raw, label="Raw", alpha=0.5)
    ax[0].plot(t, accel_filt, label="Filtrada")
    if p_time is not None:
        ax[0].axvline(p_time, color="r", linestyle="--", label="Llegada P")
    ax[0].legend()
    ax[0].grid()

    n = len(accel_filt)
    freqs = np.fft.rfftfreq(n, 1/fs)
    fft = np.abs(np.fft.rfft(accel_filt * np.hanning(n)))
    ax[1].semilogy(freqs, fft)
    if dom_freq is not None:
        ax[1].axvline(dom_freq, color="r", linestyle="--", label="Frecuencia dominante")
    ax[1].grid()
    ax[1].legend()

    fig.suptitle(f"Alerta: {alert}")
    return fig

