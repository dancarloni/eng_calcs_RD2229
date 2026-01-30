"""
GUI Streamlit - Verifiche Strutturali DM 2229/1939

Interfaccia interattiva per la creazione di sezioni,
inserimento materiali, calcolo proprietà e verifiche.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import sys

sys.path.insert(0, 'src')

from verifiche_dm1939.materials import Calcestruzzo, Acciaio
from verifiche_dm1939.sections import (
    SezioneRettangolare,
    SezioneT,
    SezioneI,
    SezioneL,
    SezioneU,
    SezioneRettangolareCava,
    SezioneCircolare,
    SezioneCircolareCava,
)

# Configurazione pagina
st.set_page_config(
    page_title="Verifiche DM 2229/1939",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato
st.markdown("""
    <style>
    .header-main {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .section-title {
        font-size: 1.8em;
        font-weight: bold;
        color: #2ca02c;
        margin-top: 20px;
        border-bottom: 2px solid #2ca02c;
        padding-bottom: 10px;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 10px;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="header-main">🏗️ Verifiche Strutturali - DM 2229/1939</div>', 
            unsafe_allow_html=True)
st.markdown("_Analisi di sezioni in calcestruzzo armato secondo il Regio Decreto n. 2229 del 1939_")
st.divider()

# Sidebar - Configurazione
with st.sidebar:
    st.markdown("### ⚙️ Configurazione")
    
    # Sezione tipo
    sezione_tipo = st.selectbox(
        "Tipo di sezione",
        [
            "Rettangolare",
            "A T",
            "A Doppia T (I)",
            "A L",
            "A U (Canale)",
            "Rettangolare Cava",
            "Circolare",
            "Circolare Cava"
        ],
        key="sezione_tipo"
    )
    
    st.divider()
    
    # Materiali
    st.markdown("### 📦 Materiali")
    
    rck = st.selectbox(
        "Calcestruzzo Rck [MPa]",
        [10, 15, 20, 25, 30],
        index=1,
        key="rck"
    )
    
    tipo_acciaio = st.selectbox(
        "Acciaio da armatura",
        ["FeB24k", "FeB32k", "FeB38k", "FeB44k"],
        index=1,
        key="tipo_acc"
    )
    
    # Mappa tipo -> fyk
    fyk_map = {
        "FeB24k": 235.0,
        "FeB32k": 320.0,
        "FeB38k": 375.0,
        "FeB44k": 430.0
    }
    fyk = fyk_map[tipo_acciaio]

# Colonne principale
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="section-title">📐 Geometria Sezione</div>', 
                unsafe_allow_html=True)
    
    # Parametri geometrici in base al tipo
    if sezione_tipo == "Rettangolare":
        b = st.number_input("Base [mm]", value=300, min_value=50, step=10)
        h = st.number_input("Altezza [mm]", value=500, min_value=50, step=10)
        copriferro = st.number_input("Copriferro [mm]", value=30, min_value=10, step=5)
        
        cls = Calcestruzzo(resistenza_caratteristica=float(rck))
        acc = Acciaio(tipo=tipo_acciaio, tensione_snervamento=fyk)
        sezione = SezioneRettangolare(b, h, cls, acc, copriferro=copriferro)
        
    elif sezione_tipo == "A T":
        bw = st.number_input("Larghezza nervatura [mm]", value=200, min_value=50, step=10)
        h = st.number_input("Altezza totale [mm]", value=600, min_value=100, step=10)
        bf = st.number_input("Larghezza soletta [mm]", value=800, min_value=100, step=10)
        tf = st.number_input("Spessore soletta [mm]", value=120, min_value=50, step=10)
        copriferro = st.number_input("Copriferro [mm]", value=30, min_value=10, step=5)
        
        cls = Calcestruzzo(resistenza_caratteristica=float(rck))
        acc = Acciaio(tipo=tipo_acciaio, tensione_snervamento=fyk)
        sezione = SezioneT(bw, h, bf, tf, cls, acc, copriferro=copriferro)
        
    elif sezione_tipo == "A Doppia T (I)":
        bw = st.number_input("Larghezza anima [mm]", value=150, min_value=50, step=10)
        h = st.number_input("Altezza totale [mm]", value=500, min_value=100, step=10)
        bf_sup = st.number_input("Larghezza soletta sup [mm]", value=400, min_value=100, step=10)
        tf_sup = st.number_input("Spessore soletta sup [mm]", value=100, min_value=50, step=10)
        bf_inf = st.number_input("Larghezza soletta inf [mm]", value=400, min_value=100, step=10)
        tf_inf = st.number_input("Spessore soletta inf [mm]", value=100, min_value=50, step=10)
        copriferro = st.number_input("Copriferro [mm]", value=30, min_value=10, step=5)
        
        cls = Calcestruzzo(resistenza_caratteristica=float(rck))
        acc = Acciaio(tipo=tipo_acciaio, tensione_snervamento=fyk)
        sezione = SezioneI(bw, h, bf_sup, tf_sup, bf_inf, tf_inf, cls, acc, copriferro=copriferro)
        
    elif sezione_tipo == "Circolare":
        D = st.number_input("Diametro [mm]", value=400, min_value=100, step=10)
        copriferro = st.number_input("Copriferro [mm]", value=30, min_value=10, step=5)
        
        cls = Calcestruzzo(resistenza_caratteristica=float(rck))
        acc = Acciaio(tipo=tipo_acciaio, tensione_snervamento=fyk)
        sezione = SezioneCircolare(D, cls, acc, copriferro=copriferro)
        
    elif sezione_tipo == "Circolare Cava":
        De = st.number_input("Diametro esterno [mm]", value=400, min_value=100, step=10)
        Di = st.number_input("Diametro interno [mm]", value=300, min_value=50, step=10)
        copriferro = st.number_input("Copriferro [mm]", value=30, min_value=10, step=5)
        
        if Di >= De:
            st.error("❌ Il diametro interno deve essere < diametro esterno")
            Di = De - 50
        
        cls = Calcestruzzo(resistenza_caratteristica=float(rck))
        acc = Acciaio(tipo=tipo_acciaio, tensione_snervamento=fyk)
        sezione = SezioneCircolareCava(De, Di, cls, acc, copriferro=copriferro)
        
    elif sezione_tipo == "Rettangolare Cava":
        b = st.number_input("Larghezza esterna [mm]", value=400, min_value=100, step=10)
        h = st.number_input("Altezza esterna [mm]", value=500, min_value=100, step=10)
        tw = st.number_input("Spessore pareti verticali [mm]", value=80, min_value=30, step=10)
        ts = st.number_input("Spessore parete superiore [mm]", value=80, min_value=30, step=10)
        ti = st.number_input("Spessore parete inferiore [mm]", value=80, min_value=30, step=10)
        copriferro = st.number_input("Copriferro [mm]", value=30, min_value=10, step=5)
        
        cls = Calcestruzzo(resistenza_caratteristica=float(rck))
        acc = Acciaio(tipo=tipo_acciaio, tensione_snervamento=fyk)
        sezione = SezioneRettangolareCava(b, h, tw, ts, ti, cls, acc, copriferro=copriferro)
        
    elif sezione_tipo == "A L":
        b1 = st.number_input("Larghezza ala sup [mm]", value=300, min_value=50, step=10)
        t1 = st.number_input("Spessore ala sup [mm]", value=100, min_value=30, step=10)
        h = st.number_input("Altezza totale [mm]", value=400, min_value=100, step=10)
        b2 = st.number_input("Larghezza ala inf [mm]", value=300, min_value=50, step=10)
        t2 = st.number_input("Spessore ala inf [mm]", value=100, min_value=30, step=10)
        copriferro = st.number_input("Copriferro [mm]", value=30, min_value=10, step=5)
        
        cls = Calcestruzzo(resistenza_caratteristica=float(rck))
        acc = Acciaio(tipo=tipo_acciaio, tensione_snervamento=fyk)
        sezione = SezioneL(b1, t1, h, b2, t2, cls, acc, copriferro=copriferro)
        
    elif sezione_tipo == "A U (Canale)":
        b = st.number_input("Larghezza totale [mm]", value=400, min_value=100, step=10)
        h = st.number_input("Altezza totale [mm]", value=500, min_value=100, step=10)
        tf = st.number_input("Spessore ali [mm]", value=80, min_value=30, step=10)
        tw = st.number_input("Spessore anima [mm]", value=100, min_value=40, step=10)
        copriferro = st.number_input("Copriferro [mm]", value=30, min_value=10, step=5)
        
        cls = Calcestruzzo(resistenza_caratteristica=float(rck))
        acc = Acciaio(tipo=tipo_acciaio, tensione_snervamento=fyk)
        sezione = SezioneU(b, h, tf, tw, cls, acc, copriferro=copriferro)
    
    # Armature
    st.markdown('<div class="section-title">🛠️ Armature</div>', unsafe_allow_html=True)
    
    col_arm1, col_arm2 = st.columns(2)
    with col_arm1:
        st.markdown("**Inferiori (As)**")
        d_inf = st.number_input("⌀ [mm]", value=20, min_value=8, step=2, key="d_inf")
        n_inf = st.number_input("N° barre", value=3, min_value=1, step=1, key="n_inf")
        if n_inf > 0 and d_inf > 0:
            sezione.aggiungi_armatura_inferiore(d_inf, n_inf)
    
    with col_arm2:
        st.markdown("**Superiori (As')**")
        d_sup = st.number_input("⌀ [mm]", value=16, min_value=8, step=2, key="d_sup")
        n_sup = st.number_input("N° barre", value=2, min_value=0, step=1, key="n_sup")
        if n_sup > 0 and d_sup > 0:
            sezione.aggiungi_armatura_superiore(d_sup, n_sup)
    
    # Staffe
    col_st1, col_st2 = st.columns(2)
    with col_st1:
        d_staffe = st.number_input("Staffe ⌀ [mm]", value=8, min_value=6, step=2, key="d_st")
    with col_st2:
        passo_staffe = st.number_input("Passo [mm]", value=150, min_value=50, step=10, key="p_st")
    
    if d_staffe > 0 and passo_staffe > 0:
        sezione.aggiungi_staffe(d_staffe, passo_staffe, numero_bracci=2)

with col2:
    st.markdown('<div class="section-title">📊 Proprietà Geometriche</div>', 
                unsafe_allow_html=True)
    
    # Calcola proprietà
    prop = sezione.calcola_proprieta_geometriche()
    
    # Metriche
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Area", f"{prop.area:.0f} mm²", delta=None)
        st.metric("Baricentro (y)", f"{prop.y_baricentro:.1f} mm", delta=None)
    with col_m2:
        st.metric("Ix", f"{prop.momento_inerzia_x:.2e} mm⁴", delta=None)
        st.metric("Iy", f"{prop.momento_inerzia_y:.2e} mm⁴", delta=None)
    
    col_m3, col_m4 = st.columns(2)
    with col_m3:
        st.metric("Wx,sup", f"{prop.modulo_resistenza_sup:.2e} mm³", delta=None)
        st.metric("Wx,inf", f"{prop.modulo_resistenza_inf:.2e} mm³", delta=None)
    with col_m4:
        st.metric("As", f"{sezione.As:.0f} mm²", delta=None)
        st.metric("As'", f"{sezione.As_prime:.0f} mm²", delta=None)
    
    if sezione.As > 0:
        st.metric("ρ [%]", f"{sezione.percentuale_armatura:.2f}%", delta=None)
    
    st.divider()
    
    # Disegno sezione
    st.markdown('<div class="section-title">📐 Disegno Sezione</div>', 
                unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Contorno
    contorno = sezione.get_contorno()
    xs = [p[0] for p in contorno] + [contorno[0][0]]
    ys = [p[1] for p in contorno] + [contorno[0][1]]
    
    ax.fill(xs, ys, color='lightblue', alpha=0.3, edgecolor='blue', linewidth=2)
    ax.plot(xs, ys, 'b-', linewidth=2)
    
    # Baricentro
    ax.plot(0, prop.y_baricentro, 'ro', markersize=10, label='Baricentro', zorder=5)
    
    # Armature inferiori
    for barra in sezione.barre_inferiori:
        for i in range(int(barra.n_barre)):
            x_offset = (i - (barra.n_barre-1)/2) * (barra.diametro + 5)
            circle = plt.Circle((x_offset + barra.x_pos, barra.y_pos), 
                               barra.diametro/2,
                               color='red', fill=True, alpha=0.7, zorder=4)
            ax.add_patch(circle)
    
    # Armature superiori
    for barra in sezione.barre_superiori:
        for i in range(int(barra.n_barre)):
            x_offset = (i - (barra.n_barre-1)/2) * (barra.diametro + 5)
            circle = plt.Circle((x_offset + barra.x_pos, barra.y_pos), 
                               barra.diametro/2,
                               color='green', fill=True, alpha=0.7, zorder=4)
            ax.add_patch(circle)
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_xlabel('x [mm]', fontsize=10)
    ax.set_ylabel('y [mm]', fontsize=10)
    ax.set_title(f'Sezione {sezione_tipo}', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

# Sezione Calcoli
st.divider()
st.markdown('<div class="section-title">🧮 Calcoli e Verifiche</div>', 
            unsafe_allow_html=True)

col_calc1, col_calc2, col_calc3 = st.columns(3)

with col_calc1:
    st.markdown("**Sollecitazioni**")
    M = st.number_input("Momento M [kNm]", value=50.0, step=5.0)
    N = st.number_input("Sforzo N [kN]", value=-100.0, step=10.0)

with col_calc2:
    st.markdown("**Coefficiente Omogeneizzazione**")
    n_mode = st.radio("Modalità", ["Automatico", "Manuale"], horizontal=True)
    if n_mode == "Manuale":
        n_val = st.number_input("n = Es/Ec", value=15.0, min_value=5.0, max_value=20.0)
        sezione.coeff_omogeneizzazione = n_val
    else:
        sezione.coeff_omogeneizzazione = None

with col_calc3:
    st.markdown("**Opzioni**")
    ruota = st.checkbox("Ruota 90°")
    if ruota:
        sezione.ruota_90_gradi()

# Calcoli
if st.button("🔍 Calcola Asse Neutro", use_container_width=True, type="primary"):
    try:
        asse_neutro = sezione.calcola_asse_neutro(M=M, N=N)
        
        col_an1, col_an2, col_an3 = st.columns(3)
        
        with col_an1:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("Asse Neutro", f"{asse_neutro.posizione:.1f} mm", 
                     delta=f"Tipo: {asse_neutro.tipo_rottura}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_an2:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("εc,sup", f"{asse_neutro.epsilon_cls_sup:.5f}", delta=None)
            st.metric("εs,inf", f"{asse_neutro.epsilon_acciaio_inf:.5f}", delta=None)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_an3:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("εc,inf", f"{asse_neutro.epsilon_cls_inf:.5f}", delta=None)
            st.metric("εs,sup", f"{asse_neutro.epsilon_acciaio_sup:.5f}", delta=None)
            st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Errore nel calcolo: {str(e)}")

# Utility ferro
st.divider()
st.markdown("### ⚙️ Utility - Calcolo Area Ferro Necessaria")

col_util1, col_util2, col_util3 = st.columns(3)

with col_util1:
    M_util = st.number_input("Momento M [kNm]", value=80.0, step=5.0, key="m_util")

with col_util2:
    pos_util = st.selectbox("Posizione", ["Inferiore (As)", "Superiore (As')"], key="pos_util")

with col_util3:
    if st.button("📊 Calcola As necessaria", use_container_width=True):
        pos = 'inferiore' if 'Inferiore' in pos_util else 'superiore'
        try:
            As_nec = sezione.calcola_area_ferro_necessaria(M=M_util, posizione=pos)
            st.success(f"✅ **As necessaria = {As_nec:.0f} mm²**")
            
            # Suggerimenti barre
            diametri_std = [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
            st.markdown("**Suggerimenti:**")
            for d in diametri_std:
                area_barra = np.pi * (d/2)**2
                n_barre = int(np.ceil(As_nec / area_barra))
                area_effettiva = n_barre * area_barra
                perc_sfruttamento = (As_nec / area_effettiva) * 100
                
                if 95 <= perc_sfruttamento <= 105:
                    st.info(f"→ {n_barre}φ{d} = {area_effettiva:.0f} mm² ({perc_sfruttamento:.0f}% sfruttamento)")
        
        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: gray; padding: 20px;">
    <small>
    🏗️ <b>Verifiche Strutturali DM 2229/1939</b> | 
    Basato su Santarella e Giangreco | 
    Python 3.12 | 
    Streamlit GUI
    </small>
    </div>
""", unsafe_allow_html=True)
