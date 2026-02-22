import numpy as np
import scipy.signal as signal
from scipy.stats import kurtosis
import matplotlib.pyplot as plt

# ---------------- CONSTANTES ----------------
G = 9.81
SAMPLE_RATE = 100.0
STA_WINDOW = 1.0
LTA_WINDOW = 30.0
STA_LTA_THRESHOLD = 3.0
PGA_THRESHOLD_G = 0.05
TSUNAMI_MAGNITUDE_THRESHOLD = 7.0
TSUNAMI_PERIOD_THRESHOLD = 10.0


# ---------------- SINTÉTICA ----------------
def generar_sintetica(duration=120.0, fs=None, snr_db=10.0,
                      n_modos_range=(1,4), n_pulsos_range=(1,3),
                      pulse_max_amp_g=0.08):
    """
    Genera una señal sintética aleatoria.
    Devuelve: t (s), accel (m/s^2), fs
    """
    if fs is None:
        fs = float(cfg.get("SAMPLE_RATE", default_config["SAMPLE_RATE"]))
    G_local = float(cfg.get("G", default_config["G"]))

    t = np.arange(0.0, duration, 1.0/fs)
    señal = np.zeros_like(t)

    # modos aleatorios
    for _ in range(random.randint(*n_modos_range)):
        f = 10**random.uniform(np.log10(0.2), np.log10(8.0))
        amp = 10**random.uniform(np.log10(0.0005), np.log10(0.01)) * G_local
        damping = random.uniform(0.0002, 0.005)
        phase = random.uniform(0, 2*np.pi)
        señal += amp * np.sin(2*np.pi*f*t + phase) * np.exp(-damping * t)

    # pulsos tipo P
    for _ in range(random.randint(*n_pulsos_range)):
        p_time = random.uniform(5.0, max(5.0, duration - 5.0))
        p_idx = int(p_time * fs)
        pulse_len = max(1, int(random.uniform(0.2, 1.0) * fs))
        amp = random.uniform(0.01, pulse_max_amp_g) * G_local
        window = signal.windows.tukey(pulse_len, alpha=random.uniform(0.2,0.8))
        end = min(len(t), p_idx + pulse_len)
        if end > p_idx:
            señal[p_idx:end] += amp * window[:end-p_idx]

    # picos transitorios aleatorios
    if random.random() < 0.5:
        for _ in range(random.randint(0,3)):
            idx = random.randint(0, len(t)-1)
            l = min(len(t)-idx, int(random.uniform(1, 0.2*fs)))
            if l > 0:
                señal[idx:idx+l] += (random.uniform(0.002, 0.02) * G_local) * signal.windows.hann(l)

    # ruido según SNR
    rms_signal = np.sqrt(np.mean(señal**2)) + 1e-12
    snr_linear = 10**(snr_db/20.0) if snr_db is not None else 10**(10/20.0)
    noise_rms = rms_signal / snr_linear
    ruido = np.random.normal(0.0, noise_rms, size=señal.shape)

    accel = señal + ruido
    return t, accel, fs

# ---------------- MODO DOPPLER ----------------
def generar_doppler(duration=120.0, fs=100.0, f0=0.8, v_rel=30.0, c=300.0, amp=0.02*G, snr_db=8.0):
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
def filtro_pasabajos(accel, fs, fc=20.0):
    nyq = 0.5 * fs
    wn = min(fc/nyq, 0.99)
    b, a = signal.butter(4, wn, btype='low')
    return signal.filtfilt(b, a, accel)

# ---------------- STA/LTA ----------------
def sta_lta(accel, fs):
    nsta = int(STA_WINDOW * fs)
    nlta = int(LTA_WINDOW * fs)
    sq = accel**2
    sta = np.convolve(sq, np.ones(nsta)/nsta, mode='same')
    lta = np.convolve(sq, np.ones(nlta)/nlta, mode='same')
    return sta / (lta + 1e-12)

def detectar_p(ratio, t):
    idx = np.argmax(ratio > STA_LTA_THRESHOLD)
    if ratio[idx] > STA_LTA_THRESHOLD:
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

def clasificar_alerta(pga_g, mag, period):
    if pga_g < PGA_THRESHOLD_G:
        return "ruido"
    if mag >= TSUNAMI_MAGNITUDE_THRESHOLD and period >= TSUNAMI_PERIOD_THRESHOLD:
        return "tsunami"
    return "sismica"

# ---------------- PROCESAMIENTO ----------------
def procesar_señal(source, t, accel, fs):
    accel_f = filtro_pasabajos(accel, fs)
    ratio = sta_lta(accel_f, fs)
    p_time, p_idx = detectar_p(ratio, t)

    if p_time is None:
        return {"alert_type": "no_detectado"}

    segmento = accel_f[p_idx:p_idx + int(10*fs)]
    pga = calcular_pga(segmento)
    pga_g = pga / G
    dom_f, dom_p = frecuencia_dominante(segmento, fs)
    mag = estimar_magnitud(pga)
    alert = clasificar_alerta(pga_g, mag, dom_p)

    return {
        "p_time": p_time,
        "pga_g": pga_g,
        "dom_freq": dom_f,
        "dom_period": dom_p,
        "magnitude": mag,
        "alert_type": alert,
        "accel_filt": accel_f
    }

# ---------------- FIGURA ----------------
def crear_figura(t, accel_raw, accel_filt, fs, p_time, dom_freq, alert):
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))

    ax[0].plot(t, accel_raw, label="Raw", alpha=0.5)
    ax[0].plot(t, accel_filt, label="Filtrada")
    ax[0].axvline(p_time, color="r", linestyle="--")
    ax[0].legend()
    ax[0].grid()

    n = len(accel_filt)
    freqs = np.fft.rfftfreq(n, 1/fs)
    fft = np.abs(np.fft.rfft(accel_filt * np.hanning(n)))
    ax[1].semilogy(freqs, fft)
    ax[1].axvline(dom_freq, color="r", linestyle="--")
    ax[1].grid()

    fig.suptitle(f"Alerta: {alert}")
    return fig

