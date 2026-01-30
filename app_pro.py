"""
GUI Streamlit Professionale - Verifiche Strutturali DM 2229/1939
Interfaccia avanzata con materiali RELUIS, armature libere, sollecitazioni.
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import sys

sys.path.insert(0, 'src')

from verifiche_dm1939.materials import Calcestruzzo, Acciaio
from verifiche_dm1939.sections import (
    SezioneRettangolare, SezioneT, SezioneI, SezioneL, SezioneU,
    SezioneRettangolareCava, SezioneCircolare, SezioneCircolareCava, Barra
)

# ============================================================================
# CONFIGURAZIONE
# ============================================================================
st.set_page_config(
    page_title="Verifiche Strutturali DM 2229/1939",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS compatto e professionale
st.markdown("""
    <style>
    * { font-size: 12px !important; }
    h1, h2, h3 { margin-bottom: 5px !important; margin-top: 10px !important; }
    .main { padding: 15px !important; }
    [data-testid="stSidebar"] { width: 280px !important; padding: 10px !important; }
    .stMetric { background: #f8f9fa; padding: 8px; border-radius: 4px; border-left: 3px solid #1f77b4; }
    .section-box { background: #f0f2f6; padding: 10px; border-radius: 4px; margin-bottom: 10px; border-left: 3px solid #2ca02c; }
    .warning-box { background: #fff3cd; padding: 10px; border-radius: 4px; border-left: 3px solid #ffc107; }
    .success-box { background: #d4edda; padding: 10px; border-radius: 4px; border-left: 3px solid #28a745; }
    .error-box { background: #f8d7da; padding: 10px; border-radius: 4px; border-left: 3px solid #dc3545; }
    table { font-size: 11px !important; }
    </style>
""", unsafe_allow_html=True)

# Database Materiali RELUIS/Normativa
CALCESTRUZZI = {
    "C20 (Rck 20)": {"rck": 20.0, "ec": 21500.0, "descrizione": "Rck=20 MPa"},
    "C25 (Rck 25)": {"rck": 25.0, "ec": 22800.0, "descrizione": "Rck=25 MPa"},
    "C28 (Rck 28)": {"rck": 28.0, "ec": 23500.0, "descrizione": "Rck=28 MPa"},
    "C30 (Rck 30)": {"rck": 30.0, "ec": 24200.0, "descrizione": "Rck=30 MPa"},
    "C35 (Rck 35)": {"rck": 35.0, "ec": 25300.0, "descrizione": "Rck=35 MPa"},
    "C40 (Rck 40)": {"rck": 40.0, "ec": 26200.0, "descrizione": "Rck=40 MPa"},
}

ACCIAI = {
    "FeB32k": {"fyk": 320.0, "es": 206000.0, "descrizione": "FeB32k, fyk=320 MPa"},
    "FeB38k": {"fyk": 375.0, "es": 206000.0, "descrizione": "FeB38k, fyk=375 MPa"},
    "FeB44k": {"fyk": 430.0, "es": 206000.0, "descrizione": "FeB44k, fyk=430 MPa"},
    "FeB50k": {"fyk": 500.0, "es": 210000.0, "descrizione": "FeB50k, fyk=500 MPa"},
}

DIAMETRI_STD = [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]

# ============================================================================
# HEADER
# ============================================================================
col_header1, col_header2 = st.columns([4, 1])
with col_header1:
    st.markdown("# 🏗️ Verifiche Strutturali DM 2229/1939")
    st.markdown("*Analisi sezioni calcestruzzo armato - Santarella & Giangreco*")

# ============================================================================
# SIDEBAR - SEZIONE E MATERIALI
# ============================================================================
with st.sidebar:
    st.markdown("## 📐 Sezione")
    
    sezione_tipo = st.selectbox(
        "Tipo",
        ["Rettangolare", "T", "I", "L", "U", "Cava Rett.", "Circolare", "Tubo Circolare"],
        key="sec_type"
    )
    
    st.divider()
    st.markdown("## 📦 Materiali")
    
    # Calcestruzzo
    cal_label = st.selectbox("Calcestruzzo", list(CALCESTRUZZI.keys()), key="cal")
    cal_preset = CALCESTRUZZI[cal_label]
    
    with st.expander("⚙️ Modifica Calcestruzzo", expanded=False):
        rck_man = st.number_input("Rck [MPa]", value=float(cal_preset["rck"]), step=1.0)
        ec_man = st.number_input("Ec [MPa]", value=float(cal_preset["ec"]), step=100.0)
        cal_preset = {"rck": rck_man, "ec": ec_man}
    
    # Acciaio
    acc_label = st.selectbox("Acciaio", list(ACCIAI.keys()), key="acc")
    acc_preset = ACCIAI[acc_label]
    
    with st.expander("⚙️ Modifica Acciaio", expanded=False):
        fyk_man = st.number_input("fyk [MPa]", value=float(acc_preset["fyk"]), step=10.0)
        es_man = st.number_input("Es [MPa]", value=float(acc_preset["es"]), step=1000.0)
        acc_preset = {"fyk": fyk_man, "es": es_man}
    
    # Coefficiente omogeneizzazione
    st.divider()
    st.markdown("## 🔗 Omogeneizzazione")
    n_mode = st.radio("Modalità", ["Auto (Es/Ec)", "Manuale"], key="n_mode")
    if n_mode == "Manuale":
        n_val = st.number_input("n", value=15.0, min_value=5.0, max_value=25.0)
    else:
        n_val = acc_preset["es"] / cal_preset["ec"]
    
    st.info(f"**n = {n_val:.2f}**")
    
    # Copriferro
    copriferro = st.number_input("Copriferro [mm]", value=30.0, min_value=10.0, max_value=50.0, step=1.0)

# ============================================================================
# TAB: GEOMETRIA
# ============================================================================
tab_geom, tab_armature, tab_sollecitazioni, tab_calcoli = st.tabs(
    ["📐 Geometria", "🛠️ Armature", "⚙️ Sollecitazioni", "📊 Calcoli & Verifiche"]
)

with tab_geom:
    st.markdown("### Parametri Geometrici")
    
    # Input in colonne per ridurre spazio
    sezione = None
    
    if sezione_tipo == "Rettangolare":
        col1, col2 = st.columns(2)
        with col1:
            b = st.number_input("Base b [mm]", value=300.0, min_value=50.0, step=10.0)
        with col2:
            h = st.number_input("Altezza h [mm]", value=500.0, min_value=50.0, step=10.0)
        
        cls = Calcestruzzo(resistenza_caratteristica=cal_preset["rck"])
        acc = Acciaio(tipo="FeB32k", tensione_snervamento=acc_preset["fyk"])
        sezione = SezioneRettangolare(b, h, cls, acc, copriferro=copriferro)
    
    elif sezione_tipo == "T":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            bw = st.number_input("Nervatura bw [mm]", value=200.0, min_value=50.0, step=10.0)
        with col2:
            h = st.number_input("Altezza h [mm]", value=600.0, min_value=100.0, step=10.0)
        with col3:
            bf = st.number_input("Soletta bf [mm]", value=800.0, min_value=100.0, step=10.0)
        with col4:
            tf = st.number_input("Spessore tf [mm]", value=120.0, min_value=50.0, step=10.0)
        
        cls = Calcestruzzo(resistenza_caratteristica=cal_preset["rck"])
        acc = Acciaio(tipo="FeB32k", tensione_snervamento=acc_preset["fyk"])
        sezione = SezioneT(bw, h, bf, tf, cls, acc, copriferro=copriferro)
    
    elif sezione_tipo == "I":
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            bw = st.number_input("Anima bw [mm]", value=150.0, min_value=50.0, step=10.0)
        with col2:
            h = st.number_input("Altezza h [mm]", value=500.0, min_value=100.0, step=10.0)
        with col3:
            bf_sup = st.number_input("Sup bf [mm]", value=400.0, min_value=100.0, step=10.0)
        with col4:
            tf_sup = st.number_input("Sup tf [mm]", value=100.0, min_value=50.0, step=10.0)
        with col5:
            bf_inf = st.number_input("Inf bf [mm]", value=400.0, min_value=100.0, step=10.0)
        with col6:
            tf_inf = st.number_input("Inf tf [mm]", value=100.0, min_value=50.0, step=10.0)
        
        cls = Calcestruzzo(resistenza_caratteristica=cal_preset["rck"])
        acc = Acciaio(tipo="FeB32k", tensione_snervamento=acc_preset["fyk"])
        sezione = SezioneI(bw, h, bf_sup, tf_sup, bf_inf, tf_inf, cls, acc, copriferro=copriferro)
    
    elif sezione_tipo == "Circolare":
        col1 = st.columns(1)[0]
        with col1:
            D = st.number_input("Diametro D [mm]", value=400.0, min_value=100.0, step=10.0)
        
        cls = Calcestruzzo(resistenza_caratteristica=cal_preset["rck"])
        acc = Acciaio(tipo="FeB32k", tensione_snervamento=acc_preset["fyk"])
        sezione = SezioneCircolare(D, cls, acc, copriferro=copriferro)
    
    elif sezione_tipo == "Tubo Circolare":
        col1, col2 = st.columns(2)
        with col1:
            De = st.number_input("Diametro esterno De [mm]", value=400.0, min_value=100.0, step=10.0)
        with col2:
            Di = st.number_input("Diametro interno Di [mm]", value=300.0, min_value=50.0, step=10.0)
        
        if Di >= De - 50:
            st.error("❌ Di deve essere << De")
            Di = De - 100
        
        cls = Calcestruzzo(resistenza_caratteristica=cal_preset["rck"])
        acc = Acciaio(tipo="FeB32k", tensione_snervamento=acc_preset["fyk"])
        sezione = SezioneCircolareCava(De, Di, cls, acc, copriferro=copriferro)
    
    elif sezione_tipo == "Cava Rett.":
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            b = st.number_input("Larghezza b [mm]", value=400.0, min_value=100.0, step=10.0)
        with col2:
            h = st.number_input("Altezza h [mm]", value=500.0, min_value=100.0, step=10.0)
        with col3:
            tw = st.number_input("Sp. vert. tw [mm]", value=80.0, min_value=30.0, step=10.0)
        with col4:
            ts = st.number_input("Sp. sup. ts [mm]", value=80.0, min_value=30.0, step=10.0)
        with col5:
            ti = st.number_input("Sp. inf. ti [mm]", value=80.0, min_value=30.0, step=10.0)
        
        cls = Calcestruzzo(resistenza_caratteristica=cal_preset["rck"])
        acc = Acciaio(tipo="FeB32k", tensione_snervamento=acc_preset["fyk"])
        sezione = SezioneRettangolareCava(b, h, tw, ts, ti, cls, acc, copriferro=copriferro)
    
    elif sezione_tipo == "L":
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            b1 = st.number_input("Ala1 b1 [mm]", value=300.0, min_value=50.0, step=10.0)
        with col2:
            t1 = st.number_input("Sp. t1 [mm]", value=100.0, min_value=30.0, step=10.0)
        with col3:
            h = st.number_input("Altezza h [mm]", value=400.0, min_value=100.0, step=10.0)
        with col4:
            b2 = st.number_input("Ala2 b2 [mm]", value=300.0, min_value=50.0, step=10.0)
        with col5:
            t2 = st.number_input("Sp. t2 [mm]", value=100.0, min_value=30.0, step=10.0)
        
        cls = Calcestruzzo(resistenza_caratteristica=cal_preset["rck"])
        acc = Acciaio(tipo="FeB32k", tensione_snervamento=acc_preset["fyk"])
        sezione = SezioneL(b1, t1, h, b2, t2, cls, acc, copriferro=copriferro)
    
    elif sezione_tipo == "U":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            b = st.number_input("Larghezza b [mm]", value=400.0, min_value=100.0, step=10.0)
        with col2:
            h = st.number_input("Altezza h [mm]", value=500.0, min_value=100.0, step=10.0)
        with col3:
            tf = st.number_input("Sp. ali tf [mm]", value=80.0, min_value=30.0, step=10.0)
        with col4:
            tw = st.number_input("Sp. anima tw [mm]", value=100.0, min_value=40.0, step=10.0)
        
        cls = Calcestruzzo(resistenza_caratteristica=cal_preset["rck"])
        acc = Acciaio(tipo="FeB32k", tensione_snervamento=acc_preset["fyk"])
        sezione = SezioneU(b, h, tf, tw, cls, acc, copriferro=copriferro)
    
    # Proprietà geometriche
    if sezione:
        st.divider()
        prop = sezione.calcola_proprieta_geometriche()
        
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            st.metric("Area", f"{prop.area:.0f} mm²")
        with col_p2:
            st.metric("y_G", f"{prop.y_baricentro:.1f} mm")
        with col_p3:
            st.metric("Ix", f"{prop.momento_inerzia_x:.2e} mm⁴")
        with col_p4:
            st.metric("Iy", f"{prop.momento_inerzia_y:.2e} mm⁴")
        
        # Disegno
        fig, ax = plt.subplots(figsize=(6, 6))
        contorno = sezione.get_contorno()
        xs = [p[0] for p in contorno] + [contorno[0][0]]
        ys = [p[1] for p in contorno] + [contorno[0][1]]
        
        ax.fill(xs, ys, color='lightblue', alpha=0.3, edgecolor='blue', linewidth=1.5)
        ax.plot(xs, ys, 'b-', linewidth=1.5)
        ax.plot(0, prop.y_baricentro, 'ro', markersize=8)
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2)
        ax.set_xlabel('x [mm]', fontsize=10)
        ax.set_ylabel('y [mm]', fontsize=10)
        ax.set_title(f'{sezione_tipo}', fontsize=11, fontweight='bold')
        plt.tight_layout()
        
        st.pyplot(fig, use_container_width=True)

# ============================================================================
# TAB: ARMATURE
# ============================================================================
with tab_armature:
    if sezione:
        st.markdown("### Armature - Inserimento Libero")
        
        # Armature inferiori
        st.markdown("#### 📍 Inferiori (As - tese in trazione M+)")
        
        df_inf = st.data_editor(
            pd.DataFrame({
                "Diametro [mm]": [16, 20],
                "N° barre": [2, 1],
                "Attiva": [True, True]
            }),
            use_container_width=True,
            key="df_inf"
        )
        
        as_inf = 0
        for idx, row in df_inf.iterrows():
            if row["Attiva"]:
                d = row["Diametro [mm]"]
                n = int(row["N° barre"])
                a = n * np.pi * (d/2)**2
                as_inf += a
                sezione.aggiungi_armatura_inferiore(d, n)
        
        st.info(f"**As = {as_inf:.0f} mm²** ({as_inf/(prop.area)*100:.2f}%)")
        
        # Armature superiori
        st.markdown("#### 📍 Superiori (As' - tese in trazione M-)")
        
        df_sup = st.data_editor(
            pd.DataFrame({
                "Diametro [mm]": [12],
                "N° barre": [2],
                "Attiva": [True]
            }),
            use_container_width=True,
            key="df_sup"
        )
        
        as_sup = 0
        for idx, row in df_sup.iterrows():
            if row["Attiva"]:
                d = row["Diametro [mm]"]
                n = int(row["N° barre"])
                a = n * np.pi * (d/2)**2
                as_sup += a
                sezione.aggiungi_armatura_superiore(d, n)
        
        st.info(f"**As' = {as_sup:.0f} mm²** ({as_sup/(prop.area)*100:.2f}%)")
        
        # Staffe
        st.markdown("#### 🔗 Staffe (Taglio)")
        
        col_st1, col_st2, col_st3 = st.columns(3)
        with col_st1:
            d_st = st.number_input("Diametro [mm]", value=8.0, min_value=6.0, max_value=16.0, step=1.0)
        with col_st2:
            p_st = st.number_input("Passo [mm]", value=150.0, min_value=50.0, max_value=400.0, step=10.0)
        with col_st3:
            n_br = st.number_input("N° bracci", value=2, min_value=2, max_value=4, step=1)
        
        if d_st > 0 and p_st > 0:
            sezione.aggiungi_staffe(d_st, p_st, numero_bracci=int(n_br))

# ============================================================================
# TAB: SOLLECITAZIONI
# ============================================================================
with tab_sollecitazioni:
    if sezione:
        st.markdown("### Sollecitazioni")
        st.markdown("**Convenzioni DM 2229/1939:**")
        st.markdown("- M+ → compressione fibre superiori, trazione inferiori (As)")
        st.markdown("- M- → compressione fibre inferiori, trazione superiori (As')")
        st.markdown("- N- → compressione | N+ → trazione")
        
        st.divider()
        
        # Tabella sollecitazioni
        col_sol1, col_sol2, col_sol3 = st.columns(3)
        
        with col_sol1:
            st.markdown("##### Momento [kNm]")
            M_vals = st.text_area(
                "M (una per riga)",
                "50\n80\n100",
                height=80,
                label_visibility="collapsed"
            )
            M_list = [float(x.strip()) for x in M_vals.strip().split('\n') if x.strip()]
        
        with col_sol2:
            st.markdown("##### Sforzo Normale [kN]")
            N_vals = st.text_area(
                "N (una per riga)",
                "-100\n-200\n-300",
                height=80,
                label_visibility="collapsed"
            )
            N_list = [float(x.strip()) for x in N_vals.strip().split('\n') if x.strip()]
        
        with col_sol3:
            st.markdown("##### Opzioni")
            analizza = st.button("🔍 Analizza", use_container_width=True, type="primary")
        
        # Risultati
        if analizza:
            st.divider()
            st.markdown("### Risultati Analisi")
            
            risultati = []
            for M in M_list:
                for N in N_list:
                    try:
                        an = sezione.calcola_asse_neutro(M=M, N=N)
                        risultati.append({
                            "M [kNm]": M,
                            "N [kN]": N,
                            "x_n [mm]": f"{an.posizione:.1f}",
                            "Tipo": an.tipo_rottura,
                            "εc,sup": f"{an.epsilon_cls_sup:.5f}",
                            "εs,inf": f"{an.epsilon_acciaio_inf:.5f}"
                        })
                    except Exception as e:
                        st.error(f"Errore M={M}, N={N}: {str(e)}")
            
            if risultati:
                df_ris = pd.DataFrame(risultati)
                st.dataframe(df_ris, use_container_width=True, hide_index=True)

# ============================================================================
# TAB: CALCOLI
# ============================================================================
with tab_calcoli:
    if sezione:
        st.markdown("### Utilità Calcoli")
        
        # Area ferro necessaria
        st.markdown("#### 📊 Area Ferro Necessaria")
        
        col_afe1, col_afe2 = st.columns(2)
        
        with col_afe1:
            M_afe = st.number_input("Momento M [kNm]", value=80.0, min_value=0.0, step=10.0)
            pos_afe = st.radio("Posizione", ["Inferiore (As)", "Superiore (As')"], horizontal=True)
        
        with col_afe2:
            if st.button("Calcola As necessaria", use_container_width=True, type="primary"):
                try:
                    pos = 'inferiore' if 'Inferiore' in pos_afe else 'superiore'
                    as_nec = sezione.calcola_area_ferro_necessaria(M=M_afe, posizione=pos)
                    
                    st.success(f"**As necessaria = {as_nec:.0f} mm²**")
                    
                    # Tabella suggerimenti
                    sugg = []
                    for d in DIAMETRI_STD:
                        area_barra = np.pi * (d/2)**2
                        n_min = int(np.ceil(as_nec / area_barra))
                        area_eff = n_min * area_barra
                        perc = (as_nec / area_eff) * 100
                        
                        if 90 <= perc <= 110:
                            sugg.append({
                                "Barre": f"{n_min}φ{d}",
                                "Area [mm²]": f"{area_eff:.0f}",
                                "Utilizzo [%]": f"{perc:.0f}"
                            })
                    
                    if sugg:
                        st.dataframe(pd.DataFrame(sugg), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Errore: {str(e)}")

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.markdown("""
<div style="text-align: center; font-size: 10px; color: gray; margin-top: 30px;">
🏗️ <b>Verifiche DM 2229/1939</b> | Python 3.12 | Streamlit | 
Riferimenti: RELUIS, Santarella & Giangreco | 
Codice: Open Source
</div>
""", unsafe_allow_html=True)
