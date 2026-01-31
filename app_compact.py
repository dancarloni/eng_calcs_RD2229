"""
Compact Streamlit GUI - tabella compatta per elementi e materiali
- Mostra tutti i parametri in un'unica schermata
- Import/Export CSV con intestazioni
- Materiali preset + CRUD materiali utente (salva in config/materials.json)
- Ogni elemento può avere materiali e parametri propri
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import sys
from io import StringIO

sys.path.insert(0, 'src')
from verifiche_dm1939.materials import Calcestruzzo, Acciaio
from verifiche_dm1939.sections import (
    SezioneRettangolare, SezioneT, SezioneI, SezioneL, SezioneU,
    SezioneRettangolareCava, SezioneCircolare, SezioneCircolareCava
)
from verifiche_dm1939.core.materiali_storici_completi import (
    CALCESTRUZZI_STORICI, ACCIAI_STORICI,
    elenca_calcestruzzi_dict, elenca_acciai_dict,
    valida_calcestruzzo, valida_acciaio,
    crea_tabella_comparativa
)

CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
MATERIALS_FILE = os.path.join(CONFIG_DIR, 'materials.json')

DEFAULT_MATERIALS = {
    "C280 (Storico Standard)": {
        "tipo_mat": "calcestruzzo",
        "sigma_c_kgcm2": 280,
        "sigma_c_ammissibile_kgcm2": 28,
        "tau_ammissibile_kgcm2": 4.0,
        "modulo_elastico_kgcm2": 373000,
        "coefficiente_omogeneo": 5.4,
        "tipo_cemento": "normale"
    },
    "FeB32k (Dolce)": {
        "tipo_mat": "acciaio",
        "tipo": "FeB32k",
        "sigma_y_kgcm2": 1400,
        "sigma_ammissibile_kgcm2": 609,
        "modulo_elastico_kgcm2": 2000000,
        "aderenza_migliorata": False
    },
    "Aq70 (Qualificato 70)": {
        "tipo_mat": "acciaio",
        "tipo": "Aq70",
        "sigma_y_kgcm2": 700,
        "sigma_ammissibile_kgcm2": 308,
        "modulo_elastico_kgcm2": 2050000,
        "aderenza_migliorata": True
    }
}

CSV_HEADERS = [
    'id','type','p1','p2','p3','p4','p5','p6','material','As','As_prime','M_kNm','N_kN'
]

st.set_page_config(page_title='Compact Verifiche', layout='wide')
st.title('Compact GUI - Verifiche DM 2229/1939 - Materiali Storici Santarella')

# Utility materiali
if not os.path.isdir(CONFIG_DIR):
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_materials():
    # Carica da file se esiste
    if os.path.isfile(MATERIALS_FILE):
        try:
            with open(MATERIALS_FILE, 'r', encoding='utf-8') as f:
                user_materials = json.load(f)
        except:
            user_materials = {}
    else:
        user_materials = {}
    
    # Combina default + storici + utente
    combined = DEFAULT_MATERIALS.copy()
    
    # Aggiungi materiali storici
    for c in elenca_calcestruzzi_dict():
        combined[c['nome']] = c
    
    for a in elenca_acciai_dict():
        combined[a['nome']] = a
    
    # Aggiungi materiali utente (sovrascritti se nome duplicato)
    combined.update(user_materials)
    
    return combined

def save_materials(user_mats):
    """Salva solo i materiali utente (non i storici)."""
    with open(MATERIALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_mats, f, indent=2, ensure_ascii=False)

materials = load_materials()

# Session state storage
if 'elements' not in st.session_state:
    st.session_state['elements'] = []

# Top controls: import / export / new element
col_im1, col_im2, col_im3, col_im4 = st.columns([1,1,1,2])
with col_im1:
    uploaded = st.file_uploader('Importa CSV elementi', type=['csv'], key='u1')
with col_im2:
    if st.button('Esporta CSV elementi'):
        df = pd.DataFrame(st.session_state['elements'])
        if df.empty:
            st.warning('Nessun elemento da esportare')
        else:
            csv = df.to_csv(index=False)
            st.download_button('Download CSV', data=csv, file_name='elementi_export.csv', mime='text/csv')
with col_im3:
    if st.button('Aggiungi elemento vuoto'):
        # aggiunge riga vuota
        new_id = len(st.session_state['elements']) + 1
        st.session_state['elements'].append({h: '' for h in CSV_HEADERS})
        st.session_state['elements'][-1]['id'] = str(new_id)
with col_im4:
    st.markdown(f'**Materiali disponibili:** {len(materials)}')
    
    # Bottone per mostrare tabella materiali
    if st.checkbox("Mostra tabella completa materiali", value=False):
        st.markdown("### TABELLA MATERIALI STORICI E UTENTE")
        
        # Crea lista materiali per tabella
        mats_for_table = list(materials.values())
        st.code(crea_tabella_comparativa(mats_for_table), language=None)

# Gestione import
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        # normalize headers
        df_columns = [c.strip() for c in df.columns]
        df.columns = df_columns
        # ensure required headers
        for h in CSV_HEADERS:
            if h not in df.columns:
                df[h] = ''
        df = df[CSV_HEADERS]
        st.session_state['elements'] = df.to_dict('records')
        st.success(f'Importati {len(st.session_state["elements"])} elementi')
    except Exception as e:
        st.error('Errore import CSV: ' + str(e))

# Data editor compatto
st.markdown('### Tabella elementi (modifica diretta)')
if st.session_state['elements']:
    df_elements = pd.DataFrame(st.session_state['elements'])
else:
    df_elements = pd.DataFrame(columns=CSV_HEADERS)

edited = st.data_editor(df_elements, num_rows='dynamic', use_container_width=True, key='editor_compact')
# save back
st.session_state['elements'] = edited.to_dict('records')

# Seleziona elemento per dettaglio
sel_idx = st.number_input('Seleziona indice elemento (1-based)', min_value=1, max_value=max(1, len(st.session_state['elements'])), value=1)
idx = sel_idx - 1

if len(st.session_state['elements'])>0:
    elem = st.session_state['elements'][idx]
    st.markdown('### Dettaglio elemento')
    cols = st.columns([1,1,1,1,1,1])
    # Mostra tutti i parametri in linea
    elem_type = st.selectbox('Tipo', ['rettangolare','T','I','L','U','rett_cava','circolare','circolare_cava'], index=0 if not elem.get('type') else ['rettangolare','T','I','L','U','rett_cava','circolare','circolare_cava'].index(elem.get('type')) if elem.get('type') in ['rettangolare','T','I','L','U','rett_cava','circolare','circolare_cava'] else 0)
    p1 = st.text_input('p1', value=str(elem.get('p1','')))
    p2 = st.text_input('p2', value=str(elem.get('p2','')))
    p3 = st.text_input('p3', value=str(elem.get('p3','')))
    p4 = st.text_input('p4', value=str(elem.get('p4','')))
    p5 = st.text_input('p5', value=str(elem.get('p5','')))
    p6 = st.text_input('p6', value=str(elem.get('p6','')))
    material_choice = st.selectbox('Materiale', list(materials.keys()), index=0 if not elem.get('material') else list(materials.keys()).index(elem.get('material')) if elem.get('material') in materials else 0)
    As = st.text_input('As [mm2]', value=str(elem.get('As','')))
    As_p = st.text_input("As' [mm2]", value=str(elem.get('As_prime','')))
    M = st.text_input('M [kNm]', value=str(elem.get('M_kNm','')))
    N = st.text_input('N [kN]', value=str(elem.get('N_kN','')))

    # Aggiorna elemento
    if st.button('Aggiorna elemento'):
        st.session_state['elements'][idx].update({
            'type': elem_type, 'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4, 'p5': p5, 'p6': p6,
            'material': material_choice, 'As': As, 'As_prime': As_p, 'M_kNm': M, 'N_kN': N
        })
        st.success('Elemento aggiornato')

    # Calcola proprietà per elemento selezionato
    if st.button('Calcola proprietà sezione'):
        try:
            mat = materials.get(material_choice, {})
            # costruisce oggetti materiali (se presenti chiavi)
            if 'rck' in mat:
                cls = Calcestruzzo(resistenza_caratteristica=float(mat['rck']))
            else:
                cls = Calcestruzzo(resistenza_caratteristica=30.0)
            if 'fyk' in mat:
                acc = Acciaio(tipo='user', tensione_snervamento=float(mat['fyk']))
            else:
                acc = Acciaio(tipo='user', tensione_snervamento=320.0)

            # mappa parametri base
            def tof(s):
                try:
                    return float(s)
                except Exception:
                    return 0.0
            p = [tof(p1), tof(p2), tof(p3), tof(p4), tof(p5), tof(p6)]
            s = None
            t = elem_type
            if t == 'rettangolare':
                s = SezioneRettangolare(p[0], p[1], cls, acc, copriferro=30.0)
            elif t == 'T':
                s = SezioneT(p[0], p[1], p[2], p[3], cls, acc, copriferro=30.0)
            elif t == 'I':
                s = SezioneI(p[0], p[1], p[2], p[3], p[4], p[5], cls, acc, copriferro=30.0)
            elif t == 'circolare':
                s = SezioneCircolare(p[0], cls, acc, copriferro=30.0)
            elif t == 'circolare_cava':
                s = SezioneCircolareCava(p[0], p[1], cls, acc, copriferro=30.0)
            elif t == 'rett_cava':
                s = SezioneRettangolareCava(p[0], p[1], p[2], p[3], p[4], cls, acc, copriferro=30.0)
            elif t == 'L':
                s = SezioneL(p[0], p[1], p[2], p[3], p[4], cls, acc, copriferro=30.0)
            elif t == 'U':
                s = SezioneU(p[0], p[1], p[2], p[3], cls, acc, copriferro=30.0)

            if s is None:
                st.error('Tipo sezione non supportato o parametri insufficienti')
            else:
                # set armature se fornite
                if As and float(As) > 0:
                    # aggiunge come 1 barra equivalente
                    s.aggiungi_armatura_inferiore(diametro=10.0, numero_barre=max(1,int(round(float(As)/(np.pi*(10/2)**2)))))
                if As_p and float(As_p) > 0:
                    s.aggiungi_armatura_superiore(diametro=10.0, numero_barre=max(1,int(round(float(As_p)/(np.pi*(10/2)**2)))))

                prop = s.calcola_proprieta_geometriche()
                st.write('Area [mm2]:', prop.area)
                st.write('y_G [mm]:', prop.y_baricentro)
                st.write('Ix [mm4]:', prop.momento_inerzia_x)

                # asse neutro se M provided
                if M:
                    an = s.calcola_asse_neutro(M=float(M), N=float(N) if N else 0.0)
                    st.write('Asse neutro [mm]:', an.posizione)
                    st.write('Tipo rottura:', an.tipo_rottura)
        except Exception as e:
            st.error('Errore calcolo: ' + str(e))

# Materiali: aggiungi/modifica
st.markdown('---')
st.markdown('## Inserisci Nuovo Materiale (Calcestruzzo o Acciaio)')

tab_cls_new, tab_acc_new = st.tabs(["Calcestruzzo", "Acciaio"])

with tab_cls_new:
    st.subheader("Aggiungi Calcestruzzo")
    col1, col2, col3 = st.columns(3)
    with col1:
        new_name_cls = st.text_input('Nome calcestruzzo', key='name_cls')
        new_sigma_c = st.number_input('Sigma_c tabulare [Kg/cm²]', value=280.0, step=10.0, key='sigma_c')
        new_sigma_amm = st.number_input('Sigma ammissibile [Kg/cm²]', value=28.0, step=1.0, key='sigma_amm')
    with col2:
        new_tau_amm = st.number_input('Tau ammissibile [Kg/cm²]', value=4.0, step=0.1, key='tau_amm')
        new_ec = st.number_input('Modulo Ec [Kg/cm²]', value=373000.0, step=1000.0, key='ec')
        new_n = st.number_input('Coefficiente n (Es/Ec)', value=5.4, step=0.1, key='n')
    with col3:
        new_tipo_cemento = st.selectbox('Tipo cemento', ['normale', 'alta_resistenza', 'alluminoso'], key='tipo_cem')
        new_rapporto_ac = st.number_input('Rapporto A/C (opzionale)', value=0.70, step=0.05, key='ac_ratio')
        new_note_cls = st.text_area('Note', key='note_cls', height=60)
    
    if st.button('Aggiungi Calcestruzzo', key='btn_add_cls'):
        # Validazione
        è_valido, avvisi = valida_calcestruzzo(new_sigma_c, new_sigma_amm, new_tau_amm, new_ec, new_n)
        
        if not è_valido:
            st.error("❌ Calcestruzzo NON VALIDO - Verificare i parametri:")
            for avv in avvisi:
                st.error(avv)
        else:
            # Mostra avvisi ma consente inserimento
            if avvisi:
                st.warning("⚠️ Avvisi di conformità:")
                for avv in avvisi:
                    st.warning(avv)
            
            if new_name_cls:
                # Carica materiali utente attuali
                if os.path.isfile(MATERIALS_FILE):
                    with open(MATERIALS_FILE, 'r', encoding='utf-8') as f:
                        user_mats = json.load(f)
                else:
                    user_mats = {}
                
                # Aggiungi nuovo materiale
                user_mats[new_name_cls] = {
                    'tipo_mat': 'calcestruzzo',
                    'sigma_c_kgcm2': float(new_sigma_c),
                    'sigma_c_ammissibile_kgcm2': float(new_sigma_amm),
                    'tau_ammissibile_kgcm2': float(new_tau_amm),
                    'modulo_elastico_kgcm2': float(new_ec),
                    'coefficiente_omogeneo': float(new_n),
                    'tipo_cemento': new_tipo_cemento,
                    'rapporto_ac': float(new_rapporto_ac),
                    'note': new_note_cls
                }
                save_materials(user_mats)
                materials = load_materials()  # Ricarica
                st.success(f"✓ Calcestruzzo '{new_name_cls}' aggiunto correttamente")
            else:
                st.error("Inserire un nome per il calcestruzzo")

with tab_acc_new:
    st.subheader("Aggiungi Acciaio")
    col1, col2, col3 = st.columns(3)
    with col1:
        new_name_acc = st.text_input('Nome acciaio', key='name_acc')
        new_tipo_acc = st.text_input('Tipo (es. FeB32k, Aq70)', value='FeB32k', key='tipo_acc')
        new_sigma_y = st.number_input('Sigma_y snervamento [Kg/cm²]', value=1400.0, step=50.0, key='sigma_y')
    with col2:
        new_sigma_amm_acc = st.number_input('Sigma ammissibile [Kg/cm²]', value=609.0, step=10.0, key='sigma_amm_acc')
        new_es = st.number_input('Modulo Es [Kg/cm²]', value=2000000.0, step=10000.0, key='es')
        new_aderenza = st.checkbox('Aderenza migliorata', value=False, key='aderenza')
    with col3:
        new_note_acc = st.text_area('Note', key='note_acc', height=60)
        new_norma = st.selectbox('Norma/Standard', ['FeB (Ferro-Beton)', 'Aq (Qualificato)', 'Altro'], key='norma')
    
    if st.button('Aggiungi Acciaio', key='btn_add_acc'):
        # Validazione
        è_valido, avvisi = valida_acciaio(new_sigma_y, new_sigma_amm_acc, new_es)
        
        if not è_valido:
            st.error("❌ Acciaio NON VALIDO - Verificare i parametri:")
            for avv in avvisi:
                st.error(avv)
        else:
            # Mostra avvisi ma consente inserimento
            if avvisi:
                st.warning("⚠️ Avvisi di conformità:")
                for avv in avvisi:
                    st.warning(avv)
            
            if new_name_acc:
                # Carica materiali utente attuali
                if os.path.isfile(MATERIALS_FILE):
                    with open(MATERIALS_FILE, 'r', encoding='utf-8') as f:
                        user_mats = json.load(f)
                else:
                    user_mats = {}
                
                # Aggiungi nuovo materiale
                user_mats[new_name_acc] = {
                    'tipo_mat': 'acciaio',
                    'tipo': new_tipo_acc,
                    'sigma_y_kgcm2': float(new_sigma_y),
                    'sigma_ammissibile_kgcm2': float(new_sigma_amm_acc),
                    'modulo_elastico_kgcm2': float(new_es),
                    'aderenza_migliorata': new_aderenza,
                    'note': new_note_acc,
                    'norma': new_norma
                }
                save_materials(user_mats)
                materials = load_materials()  # Ricarica
                st.success(f"✓ Acciaio '{new_name_acc}' aggiunto correttamente")
            else:
                st.error("Inserire un nome per l'acciaio")

st.write('File materiali usato:', MATERIALS_FILE)

# Quick help
st.markdown('---')
st.markdown('## ℹ️ INFORMAZIONI')
st.markdown("""
**Sistema di materiali storici RD 2229/1939 - Prontuario Santarella**

✓ **Calcestruzzi storici** - 7 tipi pre-caricati da 150 a 750 Kg/cm²
✓ **Acciai storici** - 8 tipi (FeB32k, FeB38k, FeB44k, Aq50, Aq60, Aq70, Aq80)
✓ **Validazione formule** - Controllo automatico su sigma_amm, tau_amm, Ec, n
✓ **Avvisi anomalie** - Segnala valori fuori range ma NON blocca l'inserimento
✓ **Persistenza** - Materiali utente salvati in config/materials.json

**Formula Santarella per Modulo Elastico:**
```
Ec = 550000 * σc / (σc + 200)  [Kg/cm²]
```

**Coefficiente omogeneizzazione:**
```
n = Es / Ec  (Es = 2,000,000 Kg/cm²)
```

**Headers CSV attesi:**
""")
st.code(','.join(CSV_HEADERS))




