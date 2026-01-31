"""
MATERIALI STORICI COMPLETI - RD 2229/1939
Tabelle complete di calcestruzzi e acciai storici con tutti i parametri espliciti

Fonti:
- Prontuario Santarella (1930-1970)
- RD 2229/1939 Norme Tecniche delle Costruzioni
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# ======================================================================================
# CALCESTRUZZI STORICI
# ======================================================================================

@dataclass
class CalcestrutzoStorico:
    """Calcestruzzo storico con parametri completi."""
    nome: str
    sigma_c_kgcm2: float  # Resistenza compressione tabulare [Kg/cm²]
    sigma_c_ammissibile_kgcm2: float  # Tensione ammissibile compressione [Kg/cm²]
    tau_ammissibile_kgcm2: float  # Tensione ammissibile taglio [Kg/cm²]
    modulo_elastico_kgcm2: float  # Modulo elastico Ec [Kg/cm²]
    coefficiente_omogeneo: float  # n = Es/Ec (Es = 2,000,000 Kg/cm²)
    tipo_cemento: str  # 'normale', 'alta_resistenza', 'alluminoso'
    rapporto_ac: Optional[float] = None  # Rapporto A/C se disponibile
    note: str = ""


@dataclass
class AcciaioStorico:
    """Acciaio storico con parametri completi."""
    nome: str
    tipo: str  # 'FeB32k', 'FeB38k', 'FeB44k', 'Aq50', 'Aq60', 'Aq70', etc.
    sigma_y_kgcm2: float  # Tensione snervamento [Kg/cm²]
    sigma_ammissibile_kgcm2: float  # Tensione ammissibile [Kg/cm²]
    modulo_elastico_kgcm2: float  # Modulo elastico Es [Kg/cm²]
    aderenza_migliorata: bool  # True se aderenza migliorata
    note: str = ""


# ======================================================================================
# TABELLA CALCESTRUZZI STORICI (RD 2229/1939)
# ======================================================================================

CALCESTRUZZI_STORICI: List[CalcestrutzoStorico] = [
    # Calcestruzzi storici comuni (da Tabella II RD 2229/1939)
    
    # Categoria bassa (150-200 Kg/cm²) - Edilizia ordinaria
    CalcestrutzoStorico(
        nome="C150 (150 Kg/cm²)",
        sigma_c_kgcm2=150,
        sigma_c_ammissibile_kgcm2=15,  # 10% della resistenza
        tau_ammissibile_kgcm2=2.5,
        modulo_elastico_kgcm2=250000,  # Ec = 550000*150/(150+200)
        coefficiente_omogeneo=8.0,
        tipo_cemento="normale",
        rapporto_ac=1.10,
        note="Edilizia ordinaria, scariche limitate"
    ),
    
    CalcestrutzoStorico(
        nome="C200 (200 Kg/cm²)",
        sigma_c_kgcm2=200,
        sigma_c_ammissibile_kgcm2=20,
        tau_ammissibile_kgcm2=3.0,
        modulo_elastico_kgcm2=303000,  # Ec = 550000*200/(200+200)
        coefficiente_omogeneo=6.6,
        tipo_cemento="normale",
        rapporto_ac=0.95,
        note="Uso generale, strutture ordinarie"
    ),
    
    # Categoria media (240-280 Kg/cm²) - Strutture importanti
    CalcestrutzoStorico(
        nome="C240 (240 Kg/cm²)",
        sigma_c_kgcm2=240,
        sigma_c_ammissibile_kgcm2=24,
        tau_ammissibile_kgcm2=3.5,
        modulo_elastico_kgcm2=340000,  # Ec = 550000*240/(240+200)
        coefficiente_omogeneo=5.9,
        tipo_cemento="normale",
        rapporto_ac=0.80,
        note="Strutture ordinarie importanti"
    ),
    
    CalcestrutzoStorico(
        nome="C280 (280 Kg/cm²) - Standard",
        sigma_c_kgcm2=280,
        sigma_c_ammissibile_kgcm2=28,
        tau_ammissibile_kgcm2=4.0,
        modulo_elastico_kgcm2=373000,  # Ec = 550000*280/(280+200)
        coefficiente_omogeneo=5.4,
        tipo_cemento="normale",
        rapporto_ac=0.70,
        note="Calcestruzzo standard storico, più usato"
    ),
    
    # Categoria alta (330-400 Kg/cm²) - Strutture speciali
    CalcestrutzoStorico(
        nome="C330 (330 Kg/cm²)",
        sigma_c_kgcm2=330,
        sigma_c_ammissibile_kgcm2=33,
        tau_ammissibile_kgcm2=4.5,
        modulo_elastico_kgcm2=407000,  # Ec = 550000*330/(330+200)
        coefficiente_omogeneo=4.9,
        tipo_cemento="alta_resistenza",
        rapporto_ac=0.60,
        note="Alta resistenza, strutture speciali"
    ),
    
    CalcestrutzoStorico(
        nome="C400 (400 Kg/cm²)",
        sigma_c_kgcm2=400,
        sigma_c_ammissibile_kgcm2=40,
        tau_ammissibile_kgcm2=5.0,
        modulo_elastico_kgcm2=441000,  # Ec = 550000*400/(400+200)
        coefficiente_omogeneo=4.5,
        tipo_cemento="alta_resistenza",
        rapporto_ac=0.50,
        note="Altissima resistenza, ponti/strutture critiche"
    ),
    
    # Calcestruzzi con sigma ammissibile elevato (75 Kg/cm²)
    CalcestrutzoStorico(
        nome="C750 (75 Kg/cm² ammissibile)",
        sigma_c_kgcm2=750,  # Fittizio, rappresenta il carico ammissibile alto
        sigma_c_ammissibile_kgcm2=75,  # Carico ammissibile elevato
        tau_ammissibile_kgcm2=6.0,
        modulo_elastico_kgcm2=500000,
        coefficiente_omogeneo=4.0,
        tipo_cemento="alluminoso",
        rapporto_ac=0.40,
        note="Calcestruzzo alluminoso ad altissima resistenza, sigma_amm=75 Kg/cm²"
    ),
]


# ======================================================================================
# TABELLA ACCIAI STORICI (RD 2229/1939)
# ======================================================================================

ACCIAI_STORICI: List[AcciaioStorico] = [
    # FeB - Acciai ordinari (ferro-beton)
    AcciaioStorico(
        nome="FeB32k (Dolce)",
        tipo="FeB32k",
        sigma_y_kgcm2=1400,
        sigma_ammissibile_kgcm2=609,  # ~44% di fy secondo RD 2229
        modulo_elastico_kgcm2=2000000,
        aderenza_migliorata=False,
        note="Acciaio dolce ordinario, barre lisce"
    ),
    
    AcciaioStorico(
        nome="FeB38k (Semiriduro)",
        tipo="FeB38k",
        sigma_y_kgcm2=1800,
        sigma_ammissibile_kgcm2=800,  # ~44% di fy
        modulo_elastico_kgcm2=2000000,
        aderenza_migliorata=True,
        note="Acciaio semiriduro, migliore aderenza"
    ),
    
    AcciaioStorico(
        nome="FeB44k (Duro)",
        tipo="FeB44k",
        sigma_y_kgcm2=2000,
        sigma_ammissibile_kgcm2=880,  # ~44% di fy
        modulo_elastico_kgcm2=2000000,
        aderenza_migliorata=True,
        note="Acciaio duro, migliore aderenza"
    ),
    
    # Aq - Acciai laminati qualificati (Aq-qualificati)
    AcciaioStorico(
        nome="Aq50 (Qualificato 50)",
        tipo="Aq50",
        sigma_y_kgcm2=500,  # 5000 kg per cm² in unità storiche
        sigma_ammissibile_kgcm2=220,  # ~44% di fy
        modulo_elastico_kgcm2=2050000,
        aderenza_migliorata=True,
        note="Acciaio laminato qualificato, barre raschiate"
    ),
    
    AcciaioStorico(
        nome="Aq60 (Qualificato 60)",
        tipo="Aq60",
        sigma_y_kgcm2=600,  # 6000 kg per cm² in unità storiche
        sigma_ammissibile_kgcm2=264,  # ~44% di fy
        modulo_elastico_kgcm2=2050000,
        aderenza_migliorata=True,
        note="Acciaio laminato qualificato, resistenza media"
    ),
    
    AcciaioStorico(
        nome="Aq70 (Qualificato 70)",
        tipo="Aq70",
        sigma_y_kgcm2=700,  # 7000 kg per cm² in unità storiche
        sigma_ammissibile_kgcm2=308,  # ~44% di fy
        modulo_elastico_kgcm2=2050000,
        aderenza_migliorata=True,
        note="Acciaio laminato qualificato, alta resistenza"
    ),
    
    AcciaioStorico(
        nome="Aq80 (Qualificato 80)",
        tipo="Aq80",
        sigma_y_kgcm2=800,  # 8000 kg per cm² in unità storiche
        sigma_ammissibile_kgcm2=352,  # ~44% di fy
        modulo_elastico_kgcm2=2050000,
        aderenza_migliorata=True,
        note="Acciaio laminato qualificato, altissima resistenza"
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
