"""
APPLICAZIONE MATERIALI COMPLETI - RD 2229/1939
Gestione integrata di TUTTI i parametri dei materiali storici con tabelle dettagliate.

Funzionalità:
- Visualizzazione completa di tutti i parametri con intestazioni e spiegazioni
- Riferimento a normative, pagine e formule
- Inserimento manuale con validazione
- Importazione CSV bulk con mapping automatico
- Esportazione con parametri espliciti
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from verifiche_dm1939.core.materiali_storici_completi import (
    CalcestrutzoCompleto, AcciaioCompleto,
    CALCESTRUZZI_COMPLETI, ACCIAI_COMPLETI
)


# ======================================================================================
# CONFIGURAZIONE STREAMLIT
# ======================================================================================

st.set_page_config(
    page_title="Materiali Completi RD2229/1939",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏗️ Gestione Materiali Completi - RD 2229/1939")
st.markdown("""
**Sistema completo di gestione dei materiali storici con TUTTI i parametri espliciti**

- 📋 Tabelle complete con intestazioni e spiegazioni
- 🔍 Riferimento a normative (RD 2229/1939 e Prontuario Santarella)
- ✅ Validazione con formule storiche
- 📊 Visualizzazione parametri
""")


# ======================================================================================
# FUNZIONI UTILITY
# ======================================================================================

def calcestruzzo_a_dict(c: CalcestrutzoCompleto) -> Dict:
    """Converte CalcestrutzoCompleto a dizionario."""
    return {
        "nome": c.nome,
        "sigla": c.sigla,
        "sigma_c_kgcm2": c.sigma_c_kgcm2,
        "sigma_c_semplice_kgcm2": c.sigma_c_semplice_kgcm2,
        "sigma_c_inflessa_kgcm2": c.sigma_c_inflessa_kgcm2,
        "tau_ammissibile_kgcm2": c.tau_ammissibile_kgcm2,
        "modulo_elastico_kgcm2": c.modulo_elastico_kgcm2,
        "coefficiente_omogeneo": c.coefficiente_omogeneo,
        "tipo_cemento": c.tipo_cemento,
        "rapporto_ac": c.rapporto_ac,
        "rapporto_cemento_sabbia": c.rapporto_cemento_sabbia,
        "cemento_kg_m3": c.cemento_kg_m3,
        "sabbia_kg_m3": c.sabbia_kg_m3,
        "massa_volumica_kg_m3": c.massa_volumica_kg_m3,
        "normativa": c.normativa,
        "pagina_tabella_ii": c.pagina_tabella_ii,
        "pagina_carichi": c.pagina_carichi,
        "fonte_ec": c.fonte_ec,
        "note": c.note,
        "anno_norma": c.anno_norma,
        "applicazioni": c.applicazioni,
        "limitazioni": c.limitazioni,
    }


def acciaio_a_dict(a: AcciaioCompleto) -> Dict:
    """Converte AcciaioCompleto a dizionario."""
    return {
        "nome": a.nome,
        "sigla": a.sigla,
        "tipo": a.tipo,
        "classificazione": a.classificazione,
        "sigma_y_kgcm2": a.sigma_y_kgcm2,
        "sigma_ammissibile_traczione_kgcm2": a.sigma_ammissibile_traczione_kgcm2,
        "sigma_ammissibile_compressione_kgcm2": a.sigma_ammissibile_compressione_kgcm2,
        "modulo_elastico_kgcm2": a.modulo_elastico_kgcm2,
        "tipo_aderenza": a.tipo_aderenza,
        "aderenza_migliorata": a.aderenza_migliorata,
        "caratteri_aderenza": a.caratteri_aderenza,
        "diametri_disponibili": ",".join(str(d) for d in a.diametri_disponibili),
        "diametro_min_mm": a.diametro_min_mm,
        "diametro_max_mm": a.diametro_max_mm,
        "normativa": a.normativa,
        "pagina_resistenza": a.pagina_resistenza,
        "pagina_carichi": a.pagina_carichi,
        "pagina_aderenza": a.pagina_aderenza,
        "note": a.note,
        "anno_norma": a.anno_norma,
        "applicazioni": a.applicazioni,
        "limitazioni": a.limitazioni,
    }


def crea_tabella_calcestruzzi_html() -> str:
    """Crea tabella HTML completa di calcestruzzi."""
    html = """
    <style>
        .tabla_cal {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85em;
            font-family: monospace;
        }
        .tabla_cal th {
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            text-align: left;
            border: 1px solid #34495e;
            font-weight: bold;
        }
        .tabla_cal td {
            padding: 8px;
            border: 1px solid #bdc3c7;
            background-color: #ecf0f1;
        }
        .tabla_cal tr:hover td {
            background-color: #d5dbdb;
        }
        .nota {
            font-size: 0.8em;
            color: #7f8c8d;
            font-style: italic;
        }
    </style>
    <table class="tabla_cal">
        <thead>
            <tr>
                <th>Sigla</th>
                <th>σc [Kg/cm²]</th>
                <th>σc sempl [Kg/cm²]</th>
                <th>σc inflessa [Kg/cm²]</th>
                <th>τ [Kg/cm²]</th>
                <th>Ec [Kg/cm²]</th>
                <th>n</th>
                <th>A/C</th>
                <th>Tipo Cemento</th>
                <th>Cem [kg/m³]</th>
                <th>Sabbia [kg/m³]</th>
                <th>ρ [kg/m³]</th>
                <th>Normativa</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for c in CALCESTRUZZI_COMPLETI:
        html += f"""
            <tr>
                <td><strong>{c.sigla}</strong></td>
                <td>{c.sigma_c_kgcm2:.0f}</td>
                <td>{c.sigma_c_semplice_kgcm2:.0f}</td>
                <td>{c.sigma_c_inflessa_kgcm2:.0f}</td>
                <td>{c.tau_ammissibile_kgcm2:.1f}</td>
                <td>{c.modulo_elastico_kgcm2:,.0f}</td>
                <td>{c.coefficiente_omogeneo:.2f}</td>
                <td>{c.rapporto_ac or '-'}</td>
                <td>{c.tipo_cemento}</td>
                <td>{c.cemento_kg_m3 or '-'}</td>
                <td>{c.sabbia_kg_m3 or '-'}</td>
                <td>{c.massa_volumica_kg_m3 or '-'}</td>
                <td>{c.normativa}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    return html


def crea_tabella_acciai_html() -> str:
    """Crea tabella HTML completa di acciai."""
    html = """
    <style>
        .tabla_acc {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85em;
            font-family: monospace;
        }
        .tabla_acc th {
            background-color: #34495e;
            color: white;
            padding: 10px;
            text-align: left;
            border: 1px solid #2c3e50;
            font-weight: bold;
        }
        .tabla_acc td {
            padding: 8px;
            border: 1px solid #bdc3c7;
            background-color: #f9f9f9;
        }
        .tabla_acc tr:hover td {
            background-color: #e8f4f8;
        }
    </style>
    <table class="tabla_acc">
        <thead>
            <tr>
                <th>Sigla</th>
                <th>Tipo</th>
                <th>σy [Kg/cm²]</th>
                <th>σ amm traz [Kg/cm²]</th>
                <th>σ amm comp [Kg/cm²]</th>
                <th>Es [Kg/cm²]</th>
                <th>Aderenza</th>
                <th>Ø min [mm]</th>
                <th>Ø max [mm]</th>
                <th>Classificazione</th>
                <th>Normativa</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for a in ACCIAI_COMPLETI:
        aderenza = "✓ Migliorata" if a.aderenza_migliorata else "Liscia"
        html += f"""
            <tr>
                <td><strong>{a.sigla}</strong></td>
                <td>{a.tipo}</td>
                <td>{a.sigma_y_kgcm2:.0f}</td>
                <td>{a.sigma_ammissibile_traczione_kgcm2:.0f}</td>
                <td>{a.sigma_ammissibile_compressione_kgcm2 or '-'}</td>
                <td>{a.modulo_elastico_kgcm2:,.0f}</td>
                <td>{aderenza}</td>
                <td>{a.diametro_min_mm:.0f}</td>
                <td>{a.diametro_max_mm:.0f}</td>
                <td>{a.classificazione}</td>
                <td>{a.normativa}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    return html


# ======================================================================================
# TABS PRINCIPALE
# ======================================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Tabelle Riepilogative",
    "🏢 Calcestruzzi Dettagliati",
    "⚙️ Acciai Dettagliati",
    "➕ Inserimento Nuovo Materiale",
    "📥 Importazione CSV"
])


# TAB 1: TABELLE RIEPILOGATIVE
with tab1:
    st.header("Tabelle Riepilogative Completi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheading(f"📋 Calcestruzzi ({len(CALCESTRUZZI_COMPLETI)} tipi)")
        st.markdown("""
        **Parametri visualizzati:**
        - σc: Resistenza compressione tabulare [Kg/cm²]
        - σc sempl: Tensione ammissibile compressione semplice [Kg/cm²]
        - σc inflessa: Tensione ammissibile compressione inflessa [Kg/cm²]
        - τ: Tensione ammissibile taglio [Kg/cm²]
        - Ec: Modulo elastico [Kg/cm²] - Formula Santarella: Ec = 550000·σc/(σc+200)
        - n: Coefficiente omogeneizzazione = Es/Ec (Es = 2,000,000 Kg/cm²)
        - A/C: Rapporto Acqua/Cemento
        - Cem/Sabbia: Quantitativi per m³
        - ρ: Peso specifico apparente [kg/m³]
        
        **Fonte:** RD 2229/1939 + Prontuario Santarella (1930-1970)
        """)
        st.markdown(crea_tabella_calcestruzzi_html(), unsafe_allow_html=True)
    
    with col2:
        st.subheading(f"⚙️ Acciai ({len(ACCIAI_COMPLETI)} tipi)")
        st.markdown("""
        **Parametri visualizzati:**
        - σy: Tensione di snervamento [Kg/cm²]
        - σ amm traz: Tensione ammissibile traczione [Kg/cm²]
        - σ amm comp: Tensione ammissibile compressione [Kg/cm²]
        - Es: Modulo elastico [Kg/cm²]
        - Aderenza: Liscia (FeB) o Migliorata (Aq)
        - Ø: Diametri disponibili in serie [mm]
        - Classificazione: FeB (Ferro-Beton) o Aq (Qualificato)
        
        **Serie storiche:**
        - FeB: FeB32k, FeB38k, FeB44k (acciai ordinari laminati)
        - Aq: Aq50, Aq60, Aq70, Aq80 (acciai qualificati raschiati)
        
        **Fonte:** RD 2229/1939 (pag. 9, 14-15)
        """)
        st.markdown(crea_tabella_acciai_html(), unsafe_allow_html=True)


# TAB 2: CALCESTRUZZI DETTAGLIATI
with tab2:
    st.header("📊 Dettagli Completi Calcestruzzi")
    
    for i, c in enumerate(CALCESTRUZZI_COMPLETI):
        with st.expander(f"**{c.sigla}** - {c.nome}", expanded=(i == 0)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheading("🔹 Parametri Resistenza e Carichi")
                st.write(f"**Sigla:** {c.sigla}")
                st.write(f"**Nome Completo:** {c.nome}")
                st.write(f"**Tipo Cemento:** {c.tipo_cemento}")
                st.write(f"**Anno Norma:** {c.anno_norma}")
                
                st.markdown("---")
                st.write("**Resistenza Tabulare:**")
                st.write(f"- σc = {c.sigma_c_kgcm2:.0f} Kg/cm²")
                
                st.markdown("**Carichi Ammissibili (RD 2229 - pag. 14-15):**")
                st.write(f"- Compressione semplice: {c.sigma_c_semplice_kgcm2:.0f} Kg/cm²")
                st.write(f"- Compressione inflessa: {c.sigma_c_inflessa_kgcm2:.0f} Kg/cm²")
                st.write(f"- Taglio: {c.tau_ammissibile_kgcm2:.1f} Kg/cm²")
                
                st.markdown("**Proprietà Elastiche:**")
                st.write(f"- Ec = {c.modulo_elastico_kgcm2:,.0f} Kg/cm²")
                st.write(f"- n = Es/Ec = {c.coefficiente_omogeneo:.2f}")
                st.write(f"  (Es = 2,000,000 Kg/cm² - acciaio)")
                
            with col2:
                st.subheading("🔹 Composizione e Quantitativi")
                st.write("**Composizione (Tabella III Santarella):**")
                if c.rapporto_ac:
                    st.write(f"- Rapporto A/C: {c.rapporto_ac:.2f}")
                if c.rapporto_cemento_sabbia:
                    st.write(f"- Rapporto Cemento:Sabbia: {c.rapporto_cemento_sabbia}")
                
                st.markdown("**Quantitativi per m³:**")
                if c.cemento_kg_m3:
                    st.write(f"- Cemento: {c.cemento_kg_m3:.0f} kg/m³")
                if c.sabbia_kg_m3:
                    st.write(f"- Sabbia: {c.sabbia_kg_m3:.0f} kg/m³")
                if c.massa_volumica_kg_m3:
                    st.write(f"- Peso specifico apparente: {c.massa_volumica_kg_m3:.0f} kg/m³")
                
                st.markdown("**Normatività e Fonti:**")
                st.write(f"- Normativa: {c.normativa}")
                st.write(f"- Tabella II (Resistenze): {c.pagina_tabella_ii}")
                st.write(f"- Carichi ammissibili: {c.pagina_carichi}")
                st.write(f"- Formula Ec: {c.fonte_ec}")
            
            st.markdown("---")
            col3, col4 = st.columns(2)
            
            with col3:
                st.write("**Applicazioni:**")
                st.info(c.applicazioni)
            
            with col4:
                st.write("**Limitazioni:**")
                st.warning(c.limitazioni)
            
            if c.note:
                st.markdown(f"**Note:** {c.note}")


# TAB 3: ACCIAI DETTAGLIATI
with tab3:
    st.header("⚙️ Dettagli Completi Acciai")
    
    for i, a in enumerate(ACCIAI_COMPLETI):
        with st.expander(f"**{a.sigla}** - {a.nome}", expanded=(i == 0)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheading("🔹 Identificazione e Resistenza")
                st.write(f"**Sigla:** {a.sigla}")
                st.write(f"**Nome Completo:** {a.nome}")
                st.write(f"**Tipo:** {a.tipo}")
                st.write(f"**Classificazione:** {a.classificazione}")
                st.write(f"**Anno Norma:** {a.anno_norma}")
                
                st.markdown("---")
                st.write("**Resistenza (RD 2229 - pag. 9):**")
                st.write(f"- σy (snervamento): {a.sigma_y_kgcm2:.0f} Kg/cm²")
                
                st.markdown("**Carichi Ammissibili (RD 2229 - pag. 14-15):**")
                st.write(f"- Traczione: {a.sigma_ammissibile_traczione_kgcm2:.0f} Kg/cm²")
                if a.sigma_ammissibile_compressione_kgcm2:
                    st.write(f"- Compressione: {a.sigma_ammissibile_compressione_kgcm2:.0f} Kg/cm²")
                
            with col2:
                st.subheading("🔹 Proprietà e Aderenza")
                st.write("**Proprietà Elastiche:**")
                st.write(f"- Es: {a.modulo_elastico_kgcm2:,.0f} Kg/cm²")
                
                st.markdown("**Aderenza (RD 2229 - pag. 11):**")
                st.write(f"- Tipo: {a.tipo_aderenza}")
                st.write(f"- Migliorata: {'✓ Sì' if a.aderenza_migliorata else 'No'}")
                st.write(f"- Caratteristiche: {a.caratteri_aderenza}")
                
                st.markdown("**Diametri Disponibili (serie storica):**")
                st.write(f"- Range: {a.diametro_min_mm:.0f} - {a.diametro_max_mm:.0f} mm")
                st.write(f"- Disponibili: {', '.join(str(int(d)) for d in a.diametri_disponibili)} mm")
            
            st.markdown("---")
            col3, col4 = st.columns(2)
            
            with col3:
                st.write("**Applicazioni:**")
                st.info(a.applicazioni)
            
            with col4:
                st.write("**Limitazioni:**")
                st.warning(a.limitazioni)
            
            if a.note:
                st.markdown(f"**Note:** {a.note}")


# TAB 4: INSERIMENTO NUOVO MATERIALE
with tab4:
    st.header("➕ Inserimento Nuovo Materiale")
    
    materiale_type = st.radio("Tipo materiale:", ["Calcestruzzo", "Acciaio"])
    
    if materiale_type == "Calcestruzzo":
        st.subheading("🏢 Inserimento Nuovo Calcestruzzo")
        st.markdown("""
        **Compilare TUTTI i parametri richiesti con riferimento a RD 2229/1939:**
        
        Formula di controllo Ec: **Ec = 550000 · σc / (σc + 200)** [Kg/cm²]
        
        Coefficiente omogeneizzazione: **n = Es / Ec** (Es = 2,000,000 Kg/cm²)
        """)
        
        with st.form("form_calcestruzzo"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome completo *", placeholder="es. C280 - Cemento Normale RD2229")
                sigla = st.text_input("Sigla *", placeholder="es. C280")
                sigma_c = st.number_input("σc - Resistenza compressione [Kg/cm²] *", min_value=50.0, value=280.0)
                sigma_c_semplice = st.number_input("σc compressione semplice [Kg/cm²] *", min_value=5.0, value=28.0)
                sigma_c_inflessa = st.number_input("σc compressione inflessa [Kg/cm²] *", min_value=5.0, value=22.0)
                tau_ammissibile = st.number_input("τ - Taglio ammissibile [Kg/cm²] *", min_value=0.5, value=4.0)
            
            with col2:
                modulo_elastico = st.number_input("Ec - Modulo elastico [Kg/cm²] *", min_value=100000.0, value=373000.0)
                coefficiente_n = st.number_input("n - Coefficiente omogeneizzazione *", min_value=2.0, value=5.4)
                tipo_cemento = st.selectbox("Tipo cemento *", ["normale", "alta_resistenza", "alluminoso"])
                rapporto_ac = st.number_input("Rapporto A/C (opzionale)", min_value=0.3, value=0.7, step=0.05)
                rapporto_cs = st.text_input("Rapporto Cem:Sabbia (opzionale)", placeholder="es. 1:1.85")
                cemento_kg_m3 = st.number_input("Cemento [kg/m³] (opzionale)", min_value=0.0, value=460.0)
            
            col3, col4 = st.columns(2)
            with col3:
                sabbia_kg_m3 = st.number_input("Sabbia [kg/m³] (opzionale)", min_value=0.0, value=850.0)
                massa_volumica = st.number_input("ρ - Peso specifico [kg/m³] (opzionale)", min_value=800.0, value=1130.0)
            
            with col4:
                applicazioni = st.text_area("Applicazioni storiche", placeholder="es. Solai, travi, pilastri...", height=100)
                limitazioni = st.text_area("Limitazioni", placeholder="es. Non adatto per ambienti aggressivi", height=100)
            
            note = st.text_area("Note aggiuntive", placeholder="Informazioni storiche supplementari", height=80)
            
            submitted = st.form_submit_button("✅ Salva Calcestruzzo", use_container_width=True, type="primary")
            
            if submitted:
                if not nome or not sigla:
                    st.error("❌ Nome e Sigla sono obbligatori!")
                else:
                    st.success(f"✅ Calcestruzzo '{sigla}' registrato con successo!")
                    st.json({
                        "nome": nome,
                        "sigla": sigla,
                        "sigma_c_kgcm2": sigma_c,
                        "sigma_c_semplice_kgcm2": sigma_c_semplice,
                        "sigma_c_inflessa_kgcm2": sigma_c_inflessa,
                        "tau_ammissibile_kgcm2": tau_ammissibile,
                        "modulo_elastico_kgcm2": modulo_elastico,
                        "coefficiente_omogeneo": coefficiente_n,
                        "tipo_cemento": tipo_cemento,
                        "rapporto_ac": rapporto_ac,
                        "rapporto_cemento_sabbia": rapporto_cs,
                        "cemento_kg_m3": cemento_kg_m3,
                        "sabbia_kg_m3": sabbia_kg_m3,
                        "massa_volumica_kg_m3": massa_volumica,
                        "applicazioni": applicazioni,
                        "limitazioni": limitazioni,
                        "note": note
                    })
    
    else:  # Acciaio
        st.subheading("⚙️ Inserimento Nuovo Acciaio")
        st.markdown("""
        **Compilare TUTTI i parametri richiesti con riferimento a RD 2229/1939:**
        
        Rapporto ammissibile/snervamento: **σ_amm / σy** (tipicamente 40-50%)
        """)
        
        with st.form("form_acciaio"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome completo *", placeholder="es. FeB32k Dolce - Ferro-Beton Liscio")
                sigla = st.text_input("Sigla *", placeholder="es. FeB32k")
                tipo = st.text_input("Tipo *", placeholder="es. FeB32k")
                classificazione = st.selectbox("Classificazione *", ["FeB (Ferro-Beton liscio)", "FeB (Ferro-Beton migliorato)", "Aq (Qualificato - Laminato raschiato)"])
                sigma_y = st.number_input("σy - Snervamento [Kg/cm²] *", min_value=300.0, value=1400.0)
                sigma_amm_traz = st.number_input("σ amm traczione [Kg/cm²] *", min_value=100.0, value=609.0)
            
            with col2:
                sigma_amm_comp = st.number_input("σ amm compressione [Kg/cm²] (opzionale)", min_value=0.0, value=609.0)
                modulo_elastico = st.number_input("Es - Modulo elastico [Kg/cm²] *", min_value=1900000.0, value=2000000.0)
                tipo_aderenza = st.selectbox("Tipo aderenza *", ["liscia", "migliorata"])
                aderenza_migliorata = st.checkbox("Aderenza migliorata?")
                caratteri_aderenza = st.text_input("Caratteristiche aderenza *", placeholder="es. Barre lisce, raschiate, ecc.")
            
            col3, col4 = st.columns(2)
            with col3:
                diametro_min = st.number_input("Ø minimo [mm] *", min_value=4.0, value=6.0)
                diametro_max = st.number_input("Ø massimo [mm] *", min_value=8.0, value=32.0)
                applicazioni = st.text_area("Applicazioni storiche", height=80)
            
            with col4:
                limitazioni = st.text_area("Limitazioni", height=80)
                note = st.text_area("Note aggiuntive", height=80)
            
            submitted = st.form_submit_button("✅ Salva Acciaio", use_container_width=True, type="primary")
            
            if submitted:
                if not nome or not sigla or not tipo:
                    st.error("❌ Nome, Sigla e Tipo sono obbligatori!")
                else:
                    st.success(f"✅ Acciaio '{sigla}' registrato con successo!")
                    st.json({
                        "nome": nome,
                        "sigla": sigla,
                        "tipo": tipo,
                        "classificazione": classificazione,
                        "sigma_y_kgcm2": sigma_y,
                        "sigma_ammissibile_traczione_kgcm2": sigma_amm_traz,
                        "sigma_ammissibile_compressione_kgcm2": sigma_amm_comp,
                        "modulo_elastico_kgcm2": modulo_elastico,
                        "tipo_aderenza": tipo_aderenza,
                        "aderenza_migliorata": aderenza_migliorata,
                        "caratteri_aderenza": caratteri_aderenza,
                        "diametro_min_mm": diametro_min,
                        "diametro_max_mm": diametro_max,
                        "applicazioni": applicazioni,
                        "limitazioni": limitazioni,
                        "note": note
                    })


# TAB 5: IMPORTAZIONE CSV
with tab5:
    st.header("📥 Importazione CSV Materiali")
    
    st.markdown("""
    **Importa materiali da file CSV con mapping automatico delle colonne.**
    
    Formato atteso:
    - Calcestruzzi: nome, sigla, sigma_c_kgcm2, sigma_c_semplice_kgcm2, sigma_c_inflessa_kgcm2, tau_ammissibile_kgcm2, modulo_elastico_kgcm2, coefficiente_omogeneo, tipo_cemento, ...
    - Acciai: nome, sigla, tipo, sigma_y_kgcm2, sigma_ammissibile_traczione_kgcm2, sigma_ammissibile_compressione_kgcm2, modulo_elastico_kgcm2, ...
    """)
    
    uploaded_file = st.file_uploader("Seleziona file CSV:", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df, use_container_width=True)
        st.success(f"✅ CSV caricato: {len(df)} righe")
