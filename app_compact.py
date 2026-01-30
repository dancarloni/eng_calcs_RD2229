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

CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
MATERIALS_FILE = os.path.join(CONFIG_DIR, 'materials.json')

DEFAULT_MATERIALS = {
    "C30 (Rck30)": {"rck": 30.0, "ec": 24200.0, "sigma_cls_amm": 3.0},
    "C25 (Rck25)": {"rck": 25.0, "ec": 22800.0, "sigma_cls_amm": 2.6},
    "FeB32k": {"fyk": 320.0, "es": 206000.0, "sigma_s_amm": 200.0}
}

CSV_HEADERS = [
    'id','type','p1','p2','p3','p4','p5','p6','material','As','As_prime','M_kNm','N_kN'
]

st.set_page_config(page_title='Compact Verifiche', layout='wide')
st.title('Compact GUI - Verifiche DM 2229/1939')

# Utility materiali
if not os.path.isdir(CONFIG_DIR):
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_materials():
    if os.path.isfile(MATERIALS_FILE):
        try:
            with open(MATERIALS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return DEFAULT_MATERIALS.copy()
    else:
        return DEFAULT_MATERIALS.copy()

def save_materials(mat_dict):
    with open(MATERIALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(mat_dict, f, indent=2, ensure_ascii=False)

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
    st.markdown('Materiali salvati: ' + ', '.join(list(materials.keys())))

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
st.markdown('## Materiali - aggiungi/modifica (visibili per import/export)')
colm1, colm2, colm3, colm4 = st.columns(4)
with colm1:
    new_name = st.text_input('Nome materiale', '')
with colm2:
    new_rck = st.number_input('Rck [MPa]', value=30.0, step=1.0)
with colm3:
    new_ec = st.number_input('Ec [MPa]', value=24200.0, step=100.0)
with colm4:
    new_sigma_cls = st.number_input('σ_cls_amm [MPa]', value=3.0, step=0.1)

colm5, colm6 = st.columns(2)
with colm5:
    new_fyk = st.number_input('fyk [MPa] (acciaio)', value=320.0, step=10.0)
with colm6:
    new_es = st.number_input('Es [MPa] (acciaio)', value=206000.0, step=1000.0)

if st.button('Salva materiale'):
    if not new_name:
        st.error('Inserire nome materiale')
    else:
        materials[new_name] = {
            'rck': float(new_rck), 'ec': float(new_ec), 'sigma_cls_amm': float(new_sigma_cls),
            'fyk': float(new_fyk), 'es': float(new_es)
        }
        save_materials(materials)
        st.success(f'Materiale {new_name} salvato')

# Export materiali
if st.button('Esporta materiali (JSON)'):
    st.download_button('Download materials.json', data=json.dumps(materials, indent=2, ensure_ascii=False), file_name='materials.json')

st.write('File materiali usato:', MATERIALS_FILE)

# Quick help
st.markdown('---')
st.markdown('CSV headers attesi:')
st.code(','.join(CSV_HEADERS))




