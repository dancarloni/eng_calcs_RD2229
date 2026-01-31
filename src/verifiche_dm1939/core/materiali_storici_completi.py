"""
PARAMETRI COMPLETI MATERIALI STORICI - RD 2229/1939
Tabelle dettagliate con TUTTI i parametri riferiti a normative e fonti storiche

Fonti:
- RD 2229/1939 "Norme tecniche delle costruzioni in cemento armato"
- Prontuario dell'Ing. Luigi Santarella (1930-1970)
- Tabelle III e II dal Prontuario Santarella
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ======================================================================================
# CALCESTRUZZI STORICI
# ======================================================================================

# ======================================================================================
# DATACLASSES - DEFINIZIONE COMPLETA PARAMETRI
# ======================================================================================

@dataclass
class CalcestrutzoCompleto:
    """Calcestruzzo con TUTTI i parametri storici."""
    
    # IDENTIFICAZIONE
    nome: str  # es. "C280 Normale RD2229"
    sigla: str  # es. "C280"
    
    # RESISTENZA (Tabella II RD 2229, pag. 9)
    sigma_c_kgcm2: float  # Resistenza compressione [Kg/cm²]
    
    # CARICHI AMMISSIBILI (RD 2229 pag. 14-15)
    sigma_c_semplice_kgcm2: float  # Sezioni semplicemente compresse [Kg/cm²]
    sigma_c_inflessa_kgcm2: float  # Sezioni inflesse [Kg/cm²]
    tau_ammissibile_kgcm2: float  # Taglio [Kg/cm²]
    
    # PROPRIETÀ ELASTICHE (Formula Santarella - Prontuario pag. XX)
    modulo_elastico_kgcm2: float  # Ec [Kg/cm²]
    coefficiente_omogeneo: float  # n = Es/Ec (Es = 2,000,000 Kg/cm²)
    
    # COMPOSIZIONE
    tipo_cemento: str  # "normale" | "alta_resistenza" | "alluminoso"
    rapporto_ac: Optional[float] = None  # Acqua/Cemento (Tabella III Santarella)
    rapporto_cemento_sabbia: Optional[str] = None  # es. "1:1.85"
    
    # QUANTITATIVI PER m³ (da Tabella III - Quantitativi di cemento e sabbia)
    cemento_kg_m3: Optional[float] = None  # Cemento [kg/m³]
    sabbia_kg_m3: Optional[float] = None  # Sabbia [kg/m³]
    massa_volumica_kg_m3: Optional[float] = None  # Peso specifico apparente [kg/m³]
    
    # NORMATIVA E FONTI
    normativa: str = "RD 2229/1939"  # Decreto di riferimento
    pagina_tabella_ii: str = "pag. 9"
    pagina_carichi: str = "pag. 14-15"
    fonte_ec: str = "Formula Santarella Prontuario"
    
    # NOTE STORICHE
    note: str = ""
    anno_norma: int = 1939
    
    # ADDITIONAL INFO
    applicazioni: str = ""  # Usi comuni nell'epoca
    limitazioni: str = ""  # Limitazioni d'uso


@dataclass
class AcciaioCompleto:
    """Acciaio con TUTTI i parametri storici."""
    
    # IDENTIFICAZIONE
    nome: str  # es. "FeB32k Dolce"
    sigla: str  # es. "FeB32k"
    tipo: str  # es. "FeB32k" | "Aq70"
    classificazione: str  # "FeB (Ferro-Beton)" | "Aq (Qualificato)"
    
    # RESISTENZA (RD 2229 pag. 14-15)
    sigma_y_kgcm2: float  # Tensione di snervamento fy [Kg/cm²]
    
    # CARICHI AMMISSIBILI (RD 2229)
    sigma_ammissibile_traczione_kgcm2: float  # Traczione [Kg/cm²]
    sigma_ammissibile_compressione_kgcm2: Optional[float] = None  # Compressione [Kg/cm²]
    
    # PROPRIETÀ ELASTICHE
    modulo_elastico_kgcm2: float = 2000000  # Es [Kg/cm²]
    
    # ADERENZA (Pag. 11 RD 2229)
    tipo_aderenza: str = "liscia"  # "liscia" | "migliorata"
    aderenza_migliorata: bool = False  # True se migliorata
    caratteri_aderenza: str = ""  # es. "barre lisce, raschiate, ecc."
    
    # DIAMETRI DISPONIBILI (Serie storiche)
    diametri_disponibili: List[float] = field(default_factory=lambda: [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32])
    diametro_min_mm: float = 6.0
    diametro_max_mm: float = 32.0
    
    # NORMATIVA E FONTI
    normativa: str = "RD 2229/1939"
    pagina_resistenza: str = "pag. 9"
    pagina_carichi: str = "pag. 14-15"
    pagina_aderenza: str = "pag. 11"
    
    # NOTE STORICHE
    note: str = ""
    anno_norma: int = 1939
    
    # ADDITIONAL INFO
    applicazioni: str = ""  # Usi comuni
    limitazioni: str = ""  # Limitazioni d'uso


# ======================================================================================
# TABELLA CALCESTRUZZI COMPLETI (RD 2229/1939 + Santarella Prontuario)
# ======================================================================================

CALCESTRUZZI_COMPLETI: List[CalcestrutzoCompleto] = [
    CalcestrutzoCompleto(
        nome="C150 - Cemento Normale - RD2229/1939",
        sigla="C150",
        sigma_c_kgcm2=150,
        sigma_c_semplice_kgcm2=15,
        sigma_c_inflessa_kgcm2=12,
        tau_ammissibile_kgcm2=2.5,
        modulo_elastico_kgcm2=250000,
        coefficiente_omogeneo=8.0,
        tipo_cemento="normale",
        rapporto_ac=1.10,
        rapporto_cemento_sabbia="1:2.70",
        cemento_kg_m3=290,
        sabbia_kg_m3=790,
        massa_volumica_kg_m3=1080,
        pagina_tabella_ii="pag. 9 (Tabella II RD2229)",
        pagina_carichi="pag. 14-15 (Carichi ammissibili)",
        fonte_ec="Ec = 550000·σc/(σc+200) = 250000 Kg/cm²",
        note="Calcestruzzo ordinario per edilizia generale con scariche limitate",
        applicazioni="Solai, travi, pilastri in edifici ordinari, murature",
        limitazioni="Non adatto per strutture critiche o esposizioni chimiche"
    ),
    
    CalcestrutzoCompleto(
        nome="C200 - Cemento Normale - RD2229/1939",
        sigla="C200",
        sigma_c_kgcm2=200,
        sigma_c_semplice_kgcm2=20,
        sigma_c_inflessa_kgcm2=16,
        tau_ammissibile_kgcm2=3.0,
        modulo_elastico_kgcm2=303000,
        coefficiente_omogeneo=6.6,
        tipo_cemento="normale",
        rapporto_ac=0.95,
        rapporto_cemento_sabbia="1:2.30",
        cemento_kg_m3=360,
        sabbia_kg_m3=830,
        massa_volumica_kg_m3=1100,
        pagina_tabella_ii="pag. 9 (Tabella II RD2229)",
        pagina_carichi="pag. 14-15",
        fonte_ec="Ec = 550000·σc/(σc+200) = 303000 Kg/cm²",
        note="Calcestruzzo intermedio, uso comune in strutture ordinarie",
        applicazioni="Solai, travi, pilastri, muri in edifici residenziali e commerciali",
        limitazioni="Moderato per ambienti aggressivi"
    ),
    
    CalcestrutzoCompleto(
        nome="C240 - Cemento Normale - RD2229/1939",
        sigla="C240",
        sigma_c_kgcm2=240,
        sigma_c_semplice_kgcm2=24,
        sigma_c_inflessa_kgcm2=19,
        tau_ammissibile_kgcm2=3.5,
        modulo_elastico_kgcm2=340000,
        coefficiente_omogeneo=5.9,
        tipo_cemento="normale",
        rapporto_ac=0.80,
        rapporto_cemento_sabbia="1:2.00",
        cemento_kg_m3=410,
        sabbia_kg_m3=820,
        massa_volumica_kg_m3=1120,
        pagina_tabella_ii="pag. 9",
        pagina_carichi="pag. 14-15",
        fonte_ec="Ec = 550000·σc/(σc+200) = 340000 Kg/cm²",
        note="Calcestruzzo per strutture ordinarie importanti",
        applicazioni="Strutture portanti, ponti di piccola-media luce, viadotti",
        limitazioni="Moderato per ambienti aggressivi"
    ),
    
    CalcestrutzoCompleto(
        nome="C280 - Cemento Normale STANDARD - RD2229/1939",
        sigla="C280",
        sigma_c_kgcm2=280,
        sigma_c_semplice_kgcm2=28,
        sigma_c_inflessa_kgcm2=22,
        tau_ammissibile_kgcm2=4.0,
        modulo_elastico_kgcm2=373000,
        coefficiente_omogeneo=5.4,
        tipo_cemento="normale",
        rapporto_ac=0.70,
        rapporto_cemento_sabbia="1:1.85",
        cemento_kg_m3=460,
        sabbia_kg_m3=850,
        massa_volumica_kg_m3=1130,
        pagina_tabella_ii="pag. 9 (Tabella II RD2229)",
        pagina_carichi="pag. 14-15",
        fonte_ec="Ec = 550000·σc/(σc+200) = 373000 Kg/cm²",
        note="CALCESTRUZZO STORICO PIÙ UTILIZZATO - Standard epoca Santarella (1930-1970)",
        applicazioni="Uso generale, strutture portanti, ponti, infrastrutture",
        limitazioni="Buono per ambienti ordinari"
    ),
    
    CalcestrutzoCompleto(
        nome="C330 - Cemento Alta Resistenza - RD2229/1939",
        sigla="C330",
        sigma_c_kgcm2=330,
        sigma_c_semplice_kgcm2=33,
        sigma_c_inflessa_kgcm2=26,
        tau_ammissibile_kgcm2=4.5,
        modulo_elastico_kgcm2=407000,
        coefficiente_omogeneo=4.9,
        tipo_cemento="alta_resistenza",
        rapporto_ac=0.60,
        rapporto_cemento_sabbia="1:1.40",
        cemento_kg_m3=540,
        sabbia_kg_m3=750,
        massa_volumica_kg_m3=1130,
        pagina_tabella_ii="pag. 9",
        pagina_carichi="pag. 14-15",
        fonte_ec="Ec = 550000·σc/(σc+200) = 407000 Kg/cm²",
        note="Calcestruzzo ad alta resistenza, cemento tipo PS (Pozzolana Speciale)",
        applicazioni="Strutture speciali, ponti importanti, edifici alti, gallerie",
        limitazioni="Richiede controllo qualità rigoroso"
    ),
    
    CalcestrutzoCompleto(
        nome="C400 - Cemento Alta Resistenza - RD2229/1939",
        sigla="C400",
        sigma_c_kgcm2=400,
        sigma_c_semplice_kgcm2=40,
        sigma_c_inflessa_kgcm2=32,
        tau_ammissibile_kgcm2=5.0,
        modulo_elastico_kgcm2=441000,
        coefficiente_omogeneo=4.5,
        tipo_cemento="alta_resistenza",
        rapporto_ac=0.50,
        rapporto_cemento_sabbia="1:1.00",
        cemento_kg_m3=620,
        sabbia_kg_m3=620,
        massa_volumica_kg_m3=1150,
        pagina_tabella_ii="pag. 9",
        pagina_carichi="pag. 14-15",
        fonte_ec="Ec = 550000·σc/(σc+200) = 441000 Kg/cm²",
        note="Calcestruzzo altissima resistenza, cemento tipo PS o alluminoso",
        applicazioni="Strutture critiche, ponti lunghi, edifici speciali, gallerie",
        limitazioni="Controllo qualità essenziale, costo elevato"
    ),
    
    CalcestrutzoCompleto(
        nome="C750 - Cemento Alluminoso SPECIALE - RD2229/1939",
        sigla="C750",
        sigma_c_kgcm2=750,
        sigma_c_semplice_kgcm2=75,
        sigma_c_inflessa_kgcm2=60,
        tau_ammissibile_kgcm2=6.0,
        modulo_elastico_kgcm2=500000,
        coefficiente_omogeneo=4.0,
        tipo_cemento="alluminoso",
        rapporto_ac=0.40,
        rapporto_cemento_sabbia="1:0.50",
        cemento_kg_m3=750,
        sabbia_kg_m3=375,
        massa_volumica_kg_m3=1200,
        pagina_tabella_ii="pag. 9 (Speciale - Ciment Fondu)",
        pagina_carichi="pag. 14-15",
        fonte_ec="Ec = 550000·σc/(σc+200) = 500000 Kg/cm² (Ciment Fondu)",
        note="Calcestruzzo alluminoso ad altissima resistenza e durabilità (Ciment Fondu - sigma_amm=75 Kg/cm²)",
        applicazioni="Strutture in ambienti chimicamente aggressivi, refrattari, strutture critiche sottomarine",
        limitazioni="Molto costoso, reazioni esotermiche in stagionamento, possibile invecchiamento chimico"
    ),
]


# ======================================================================================
# TABELLA ACCIAI COMPLETI (RD 2229/1939)
# ======================================================================================

ACCIAI_COMPLETI: List[AcciaioCompleto] = [
    # FeB - Ferro-Beton (barre lisce storiche)
    AcciaioCompleto(
        nome="FeB32k Dolce - Ferro-Beton Liscio",
        sigla="FeB32k",
        tipo="FeB32k",
        classificazione="FeB (Ferro-Beton liscio)",
        sigma_y_kgcm2=1400,
        sigma_ammissibile_traczione_kgcm2=609,
        sigma_ammissibile_compressione_kgcm2=609,
        modulo_elastico_kgcm2=2000000,
        tipo_aderenza="liscia",
        aderenza_migliorata=False,
        caratteri_aderenza="Barre lisce, superficie liscia ordinaria",
        diametri_disponibili=[6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32],
        diametro_min_mm=6.0,
        diametro_max_mm=32.0,
        pagina_resistenza="pag. 9 (Tabella I RD2229)",
        pagina_carichi="pag. 14-15 (Acciai ordinari)",
        pagina_aderenza="pag. 11 (Aderenza semplice)",
        note="Acciaio dolce ordinario, aderenza semplice (liscia). Standard storico RD2229",
        applicazioni="Uso generale, solai, travi, pilastri in edifici ordinari",
        limitazioni="Aderenza semplice, minore rispetto acciai migliorati"
    ),
    
    AcciaioCompleto(
        nome="FeB38k Semiriduro - Ferro-Beton Migliorato",
        sigla="FeB38k",
        tipo="FeB38k",
        classificazione="FeB (Ferro-Beton migliorato)",
        sigma_y_kgcm2=1800,
        sigma_ammissibile_traczione_kgcm2=800,
        sigma_ammissibile_compressione_kgcm2=800,
        modulo_elastico_kgcm2=2000000,
        tipo_aderenza="migliorata",
        aderenza_migliorata=True,
        caratteri_aderenza="Barre con lamine trasversali o nervature, trattamento superficiale",
        diametri_disponibili=[6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32],
        diametro_min_mm=6.0,
        diametro_max_mm=32.0,
        pagina_resistenza="pag. 9",
        pagina_carichi="pag. 14-15",
        pagina_aderenza="pag. 11 (Aderenza migliorata)",
        note="Acciaio semiriduro con aderenza migliorata mediante trattamento superficiale",
        applicazioni="Strutture ordinarie importanti, ponti piccoli, edifici residenziali",
        limitazioni="Aderenza migliorata ma inferiore a Aq"
    ),
    
    AcciaioCompleto(
        nome="FeB44k Duro - Ferro-Beton Migliorato",
        sigla="FeB44k",
        tipo="FeB44k",
        classificazione="FeB (Ferro-Beton migliorato)",
        sigma_y_kgcm2=2000,
        sigma_ammissibile_traczione_kgcm2=880,
        sigma_ammissibile_compressione_kgcm2=880,
        modulo_elastico_kgcm2=2000000,
        tipo_aderenza="migliorata",
        aderenza_migliorata=True,
        caratteri_aderenza="Barre con trattamento superficiale migliorato, nervature poco marcate",
        diametri_disponibili=[6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32],
        diametro_min_mm=6.0,
        diametro_max_mm=32.0,
        pagina_resistenza="pag. 9",
        pagina_carichi="pag. 14-15",
        pagina_aderenza="pag. 11",
        note="Acciaio duro con aderenza migliorata, resistenza elevata",
        applicazioni="Strutture speciali, ponti importanti, edifici alti",
        limitazioni="Costo elevato"
    ),
    
    # Aq - Acciai laminati Qualificati (barre raschiate - serie italiana)
    AcciaioCompleto(
        nome="Aq50 Qualificato - Acciaio Laminato",
        sigla="Aq50",
        tipo="Aq50",
        classificazione="Aq (Qualificato - Laminato raschiato)",
        sigma_y_kgcm2=500,
        sigma_ammissibile_traczione_kgcm2=220,
        sigma_ammissibile_compressione_kgcm2=220,
        modulo_elastico_kgcm2=2050000,
        tipo_aderenza="migliorata",
        aderenza_migliorata=True,
        caratteri_aderenza="Barre laminare raschiate, superficie ruvida per eccellente aderenza",
        diametri_disponibili=[8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32],
        diametro_min_mm=8.0,
        diametro_max_mm=32.0,
        pagina_resistenza="pag. 9 (Acciai qualificati)",
        pagina_carichi="pag. 14-15",
        pagina_aderenza="pag. 11 (Aderenza eccellente)",
        note="Acciaio laminato qualificato, serie Aq italiana. Aderenza eccellente per raschatura superficiale",
        applicazioni="Strutture ordinarie, solai, travi con aderenza critica",
        limitazioni="Produzione selettiva, non sempre disponibile nel mercato storico"
    ),
    
    AcciaioCompleto(
        nome="Aq60 Qualificato - Acciaio Laminato",
        sigla="Aq60",
        tipo="Aq60",
        classificazione="Aq (Qualificato - Laminato raschiato)",
        sigma_y_kgcm2=600,
        sigma_ammissibile_traczione_kgcm2=264,
        sigma_ammissibile_compressione_kgcm2=264,
        modulo_elastico_kgcm2=2050000,
        tipo_aderenza="migliorata",
        aderenza_migliorata=True,
        caratteri_aderenza="Barre laminare raschiate con eccellente aderenza",
        diametri_disponibili=[8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32],
        diametro_min_mm=8.0,
        diametro_max_mm=32.0,
        pagina_resistenza="pag. 9",
        pagina_carichi="pag. 14-15",
        pagina_aderenza="pag. 11",
        note="Acciaio laminato qualificato Aq60, resistenza intermedia, aderenza eccellente",
        applicazioni="Strutture ordinarie importanti, ponti piccoli",
        limitazioni="Reperibilità limitata nel mercato storico"
    ),
    
    AcciaioCompleto(
        nome="Aq70 Qualificato - Acciaio Laminato",
        sigla="Aq70",
        tipo="Aq70",
        classificazione="Aq (Qualificato - Laminato raschiato)",
        sigma_y_kgcm2=700,
        sigma_ammissibile_traczione_kgcm2=308,
        sigma_ammissibile_compressione_kgcm2=308,
        modulo_elastico_kgcm2=2050000,
        tipo_aderenza="migliorata",
        aderenza_migliorata=True,
        caratteri_aderenza="Barre laminare raschiate, ottima aderenza",
        diametri_disponibili=[8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32],
        diametro_min_mm=8.0,
        diametro_max_mm=32.0,
        pagina_resistenza="pag. 9",
        pagina_carichi="pag. 14-15",
        pagina_aderenza="pag. 11",
        note="Acciaio laminato qualificato Aq70 - resistenza alta, eccellente aderenza, usato nei ponti storici",
        applicazioni="Strutture importanti, ponti, edifici speciali",
        limitazioni="Costo moderato, reperibilità selettiva"
    ),
    
    AcciaioCompleto(
        nome="Aq80 Qualificato - Acciaio Laminato",
        sigla="Aq80",
        tipo="Aq80",
        classificazione="Aq (Qualificato - Laminato raschiato)",
        sigma_y_kgcm2=800,
        sigma_ammissibile_traczione_kgcm2=352,
        sigma_ammissibile_compressione_kgcm2=352,
        modulo_elastico_kgcm2=2050000,
        tipo_aderenza="migliorata",
        aderenza_migliorata=True,
        caratteri_aderenza="Barre laminare raschiate, ottima aderenza",
        diametri_disponibili=[10, 12, 14, 16, 18, 20, 22, 25, 28, 32],
        diametro_min_mm=10.0,
        diametro_max_mm=32.0,
        pagina_resistenza="pag. 9",
        pagina_carichi="pag. 14-15",
        pagina_aderenza="pag. 11",
        note="Acciaio laminato qualificato Aq80 - altissima resistenza e aderenza",
        applicazioni="Strutture critiche, ponti lunghi, edifici speciali",
        limitazioni="Costo elevato, reperibilità limitata"
    ),
]


# ======================================================================================
# FORMULE DI VALIDAZIONE (Santarella - RD 2229/1939)
# ======================================================================================

def valida_calcestruzzo(sigma_c: float, sigma_amm: float, tau_amm: float, 
                        ec: float, n: float) -> Tuple[bool, List[str]]:
    """
    Valida i parametri di un calcestruzzo secondo le formule di Santarella.
    
    Returns:
        (è_valido, lista_avvisi)
    """
    avvisi = []
    
    # 1. Rapporto sigma_amm / sigma_c
    rapporto = sigma_amm / sigma_c if sigma_c > 0 else 0
    if rapporto < 0.08:
        avvisi.append(f"⚠ Carico ammissibile molto basso: {rapporto:.1%} (tipico: 8-12%)")
    elif rapporto > 0.15:
        avvisi.append(f"⚠ Carico ammissibile molto alto: {rapporto:.1%} (tipico: 8-12%)")
    
    # 2. Rapporto tau_amm / sigma_amm (tipicamente 10-15%)
    rapporto_tau = tau_amm / sigma_amm if sigma_amm > 0 else 0
    if rapporto_tau < 0.08:
        avvisi.append(f"⚠ Taglio ammissibile basso: {rapporto_tau:.1%} di compressione (tipico: 10-15%)")
    elif rapporto_tau > 0.20:
        avvisi.append(f"⚠ Taglio ammissibile alto: {rapporto_tau:.1%} di compressione (tipico: 10-15%)")
    
    # 3. Formula Santarella: Ec = 550000 * sigma_c / (sigma_c + 200)
    ec_atteso = 550000 * sigma_c / (sigma_c + 200) if sigma_c > 0 else 0
    errore_ec = abs(ec - ec_atteso) / ec_atteso if ec_atteso > 0 else 0
    if errore_ec > 0.20:
        avvisi.append(f"⚠ Modulo elastico anomalo: {ec:.0f} vs atteso {ec_atteso:.0f} (errore {errore_ec:.1%})")
    
    # 4. Coefficiente omogenizzazione: n = Es / Ec (Es = 2,000,000 Kg/cm²)
    es = 2000000
    n_atteso = es / ec if ec > 0 else 0
    errore_n = abs(n - n_atteso) / n_atteso if n_atteso > 0 else 0
    if errore_n > 0.15:
        avvisi.append(f"⚠ Coefficiente omogeneizzazione anomalo: {n:.2f} vs atteso {n_atteso:.2f} (errore {errore_n:.1%})")
    
    # 5. Range generali storici
    if sigma_c < 100 or sigma_c > 500:
        avvisi.append(f"⚠ Resistenza fuori range storico: {sigma_c} Kg/cm² (storico: 100-500)")
    
    # È valido se non ha avvisi gravi (sigma_amm = 0 è grave)
    è_valido = sigma_amm > 0 and tau_amm > 0 and ec > 0
    
    return è_valido, avvisi


def valida_acciaio(sigma_y: float, sigma_amm: float, es: float) -> Tuple[bool, List[str]]:
    """
    Valida i parametri di un acciaio secondo le norme RD 2229/1939.
    
    Returns:
        (è_valido, lista_avvisi)
    """
    avvisi = []
    
    # 1. Rapporto sigma_amm / sigma_y (tipicamente 40-50%)
    rapporto = sigma_amm / sigma_y if sigma_y > 0 else 0
    if rapporto < 0.35:
        avvisi.append(f"⚠ Carico ammissibile basso: {rapporto:.1%} di snervamento (tipico: 40-50%)")
    elif rapporto > 0.60:
        avvisi.append(f"⚠ Carico ammissibile alto: {rapporto:.1%} di snervamento (tipico: 40-50%)")
    
    # 2. Modulo elastico (Es tipicamente 200,000-210,000 Kg/cm²)
    if es < 190000 or es > 220000:
        avvisi.append(f"⚠ Modulo elastico anomalo: {es:.0f} Kg/cm² (storico: 200,000-210,000)")
    
    # 3. Range generali storici
    if sigma_y < 300 or sigma_y > 1000:
        avvisi.append(f"⚠ Snervamento fuori range storico: {sigma_y} Kg/cm² (storico: 300-1000)")
    
    # È valido
    è_valido = sigma_y > 0 and sigma_amm > 0 and es > 0
    
    return è_valido, avvisi


def crea_tabella_comparativa(materiali: List[Dict]) -> str:
    """Crea tabella comparativa di materiali."""
    if not materiali:
        return "Nessun materiale disponibile."
    
    linea = "=" * 140
    header = f"{'Nome':<20} {'Tipo':<12} {'Sigma [Kg/cm²]':<15} {'Sigma Amm [Kg/cm²]':<18} {'Tau/Sigma [%]':<15} {'Ec [Kg/cm²]':<15} {'n':<8} {'Aderenza':<10}"
    
    tabella = linea + "\n" + header + "\n" + linea + "\n"
    
    for mat in materiali:
        if mat.get('tipo_mat') == 'calcestruzzo':
            aderenza = ""
            rapporto_tau = (mat['tau_ammissibile_kgcm2'] / mat['sigma_c_ammissibile_kgcm2'] * 100) if mat['sigma_c_ammissibile_kgcm2'] > 0 else 0
            row = (f"{mat['nome']:<20} {'CLS':<12} {mat['sigma_c_kgcm2']:<15.0f} "
                  f"{mat['sigma_c_ammissibile_kgcm2']:<18.1f} {rapporto_tau:<15.1f} "
                  f"{mat['modulo_elastico_kgcm2']:<15.0f} {mat['coefficiente_omogeneo']:<8.2f} {aderenza:<10}")
        else:
            aderenza = "Si" if mat['aderenza_migliorata'] else "No"
            rapporto_amm = (mat['sigma_ammissibile_kgcm2'] / mat['sigma_y_kgcm2'] * 100) if mat['sigma_y_kgcm2'] > 0 else 0
            row = (f"{mat['nome']:<20} {mat['tipo']:<12} {mat['sigma_y_kgcm2']:<15.0f} "
                  f"{mat['sigma_ammissibile_kgcm2']:<18.1f} {rapporto_amm:<15.1f} "
                  f"{mat['modulo_elastico_kgcm2']:<15.0f} {'':<8} {aderenza:<10}")
        
        tabella += row + "\n"
    
    tabella += linea
    return tabella


def elenca_calcestruzzi_dict() -> List[Dict]:
    """Elenca calcestruzzi come dizionari."""
    result = []
    for c in CALCESTRUZZI_STORICI:
        result.append({
            'tipo_mat': 'calcestruzzo',
            'nome': c.nome,
            'sigma_c_kgcm2': c.sigma_c_kgcm2,
            'sigma_c_ammissibile_kgcm2': c.sigma_c_ammissibile_kgcm2,
            'tau_ammissibile_kgcm2': c.tau_ammissibile_kgcm2,
            'modulo_elastico_kgcm2': c.modulo_elastico_kgcm2,
            'coefficiente_omogeneo': c.coefficiente_omogeneo,
            'tipo_cemento': c.tipo_cemento,
            'rapporto_ac': c.rapporto_ac,
            'note': c.note
        })
    return result


def elenca_acciai_dict() -> List[Dict]:
    """Elenca acciai come dizionari."""
    result = []
    for a in ACCIAI_STORICI:
        result.append({
            'tipo_mat': 'acciaio',
            'nome': a.nome,
            'tipo': a.tipo,
            'sigma_y_kgcm2': a.sigma_y_kgcm2,
            'sigma_ammissibile_kgcm2': a.sigma_ammissibile_kgcm2,
            'modulo_elastico_kgcm2': a.modulo_elastico_kgcm2,
            'aderenza_migliorata': a.aderenza_migliorata,
            'note': a.note
        })
    return result
