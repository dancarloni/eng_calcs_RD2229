"""
Dati Storici RD 2229/1939 - Tabelle e formule parametriche.

Fonte: Regio Decreto Legge n. 2229 del 16 novembre 1939
       Norme tecniche per l'esecuzione delle opere in conglomerato cementizio
       Prontuari dell'Ing. Santarella

Contiene:
- Tabelle resistenze cimenti
- Classi calcestruzzo con rapporti A/C
- Carichi unitari di sicurezza
- Moduli di elasticità
- Formule parametriche epoca

Unità: Kg/cm² (sistema storico)
Conversione: 1 MPa = 10.197 Kg/cm² ≈ 10.2 Kg/cm²
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ClasseCalcestrutzoStorica:
    """Classe storica di calcestruzzo RD 2229."""
    
    nome: str                          # Es. "A/C = 0,40"
    rapporto_ac: float                 # Rapporto acqua/cemento
    resistenza_compressione: float     # σcas in Kg/cm² a 28 giorni
    resistenza_trazione: float         # Resistenza a trazione in Kg/cm²
    tipo_cemento: str                  # "normale", "alta_resistenza", "alluminoso"


# ============================================================================
# TABELLA II - RAPPORTI ACQUA/CEMENTO E RESISTENZE DI COMPRESSIONE
# Da pag. 9 del documento RD 2229
# ============================================================================

TABELLA_II_CALCESTRUZZO = {
    # (A/C, tipo_cemento) -> resistenza_compressione [Kg/cm²] a 28 giorni
    
    # Cemento NORMALE (40 Kg/cm² resistenza)
    ("0,40", "normale"):                380,
    ("0,45", "normale"):                330,
    ("0,50", "normale"):                280,
    ("0,55", "normale"):                250,
    ("0,60", "normale"):                225,
    ("0,70", "normale"):                180,
    ("0,80", "normale"):                140,
    
    # Cemento AD ALTA RESISTENZA (60 Kg/cm² resistenza)
    ("0,40", "alta_resistenza"):        500,
    ("0,45", "alta_resistenza"):        400,
    ("0,50", "alta_resistenza"):        350,
    ("0,55", "alta_resistenza"):        290,
    ("0,60", "alta_resistenza"):        250,
    ("0,70", "alta_resistenza"):        200,
    ("0,80", "alta_resistenza"):        170,
    
    # Cemento ALLUMINOSO
    ("0,40", "alluminoso"):             400,
    ("0,45", "alluminoso"):             330,
    ("0,50", "alluminoso"):             280,
}

# Mappatura stringhe A/C a valori numerici
RAPPORTI_AC_NOMINALI = {
    "0,40": 0.40,
    "0,45": 0.45,
    "0,50": 0.50,
    "0,55": 0.55,
    "0,60": 0.60,
    "0,70": 0.70,
    "0,80": 0.80,
}


# ============================================================================
# CARICHI UNITARI DI SICUREZZA NEL CALCESTRUZZO ARMATO
# Da pag. 14-15 del documento RD 2229
# ============================================================================

class CarichUnitariSicurezza:
    """Carichi unitari ammissibili per verifiche a tensioni ammissibili."""
    
    # SEZIONI SEMPLICEMENTE COMPRESSE (pilastri - carico di punta)
    SIGMA_C_COMPRESSIONE_SEMPLICE_NORM = 35  # Kg/cm² con σcss > 120 Kg/cm² (cls normale)
    SIGMA_C_COMPRESSIONE_SEMPLICE_ALT = 45   # Kg/cm² con cemento alta resistenza
    
    # SEZIONI INFLESSE E PRESSO-INFLESSE
    SIGMA_C_COMPRESSIONE_INFLESSA_NORM = 40  # Kg/cm² per cemento normale, σcss > 120
    SIGMA_C_COMPRESSIONE_INFLESSA_ALT = 50   # Kg/cm² per cemento alta resistenza, σcss > 160
    
    # CARICHI MASSIMI NEL CALCESTRUZZO ARMATO
    # Per sezioni semplicemente compresse
    SIGMA_C_MAX_SEMPLICE_NORM = 35            # Kg/cm² (con σcss > 120 Kg/cm²)
    SIGMA_C_MAX_SEMPLICE_ALT = 45             # Kg/cm² (con cemento ad alta resistenza)
    
    # RESISTENZA AL TAGLIO (pag. 15)
    TAU_TAGLIO_NORMALE = 4                    # Kg/cm² per conglomerati cemento normale
    TAU_TAGLIO_ALTA_RESISTENZA = 6            # Kg/cm² per cemento ad alta resistenza
    TAU_TAGLIO_ALLUMINOSO = 6                 # Kg/cm² per cemento alluminoso
    
    # CARICHI MASSIMI NELLE ARMATURE (pag. 15)
    # Acciaio dolce (fy = 1400 Kg/cm²)
    SIGMA_S_MAX_ACCIAIO_DOLCE_NORMAL = 1400   # σf max = 1400 Kg/cm² per barre φ < 30mm
    SIGMA_S_MAX_ACCIAIO_DOLCE_SMALL = 1400    # σf max per barre semidritte
    
    # Acciaio semiriduro (fy = 1800 Kg/cm²)
    SIGMA_S_MAX_ACCIAIO_SEMI = 1800            # Kg/cm²
    
    # Acciaio duro (fy = 1600-2000 Kg/cm²)
    SIGMA_S_MAX_ACCIAIO_DURO_SMALL = 1600      # Kg/cm² per barre φ < 26 mm
    SIGMA_S_MAX_ACCIAIO_DURO_NORMAL = 2000     # Kg/cm² per barre φ >= 26 mm


# ============================================================================
# MODULI DI ELASTICITÀ - FORMULE STORICHE
# Da pag. 13-14 del documento RD 2229
# ============================================================================

def modulo_elasticita_calcestruzzo_kgcm2(resistenza_compressione: float) -> float:
    """
    Calcola il modulo di elasticità del calcestruzzo.
    
    Formula storica (pag. 13):
    Ec = 550000 · σc / (σc + 200)
    
    Dove:
    - σc = resistenza a compressione in Kg/cm²
    - Ec = modulo elastico in Kg/cm²
    
    Args:
        resistenza_compressione: Resistenza a compressione in Kg/cm²
    
    Returns:
        Modulo di elasticità Ec in Kg/cm²
    """
    if resistenza_compressione <= 0:
        raise ValueError("Resistenza deve essere positiva")
    
    ec = 550000 * resistenza_compressione / (resistenza_compressione + 200)
    return ec


def modulo_elasticita_calcestruzzo_mpa(resistenza_compressione: float) -> float:
    """
    Calcola il modulo di elasticità del calcestruzzo in MPa.
    
    Args:
        resistenza_compressione: Resistenza a compressione in MPa
    
    Returns:
        Modulo di elasticità Ec in MPa
    """
    from verifiche_dm1939.core.conversioni_unita import kgcm2_to_mpa, mpa_to_kgcm2
    
    # Converti MPa → Kg/cm²
    sigma_c_kgcm2 = mpa_to_kgcm2(resistenza_compressione)
    
    # Calcola con formula storica
    ec_kgcm2 = modulo_elasticita_calcestruzzo_kgcm2(sigma_c_kgcm2)
    
    # Converti back → MPa
    ec_mpa = kgcm2_to_mpa(ec_kgcm2)
    
    return ec_mpa


# Modulo elastico acciaio (pag. 14)
MODULO_ELASTICITA_ACCIAIO_KGCM2 = 2_000_000  # Es = 2.000.000 Kg/cm²
MODULO_ELASTICITA_ACCIAIO_MPA = 196_000      # ≈ 196.000 MPa


# ============================================================================
# COEFFICIENTE DI OMOGENEIZZAZIONE n = Es / Ec
# ============================================================================

def coefficiente_omogeneizzazione(ec_kgcm2: float) -> float:
    """
    Calcola il coefficiente di omogeneizzazione n = Es / Ec.
    
    Epoca: es = 2.000.000 Kg/cm²
    """
    n = MODULO_ELASTICITA_ACCIAIO_KGCM2 / ec_kgcm2
    return n


# ============================================================================
# TABELLE STORICHE PILASTRI
# Da pag. 17 - PILASTRI CON SFORZO ASSIALE E COMPRESSIONE
# ============================================================================

class Pilastri:
    """Norme storiche per pilastri RD 2229."""
    
    # Rapporto lunghezza libera / minore dimensione trasversale
    # Percentuale minima di ferro (armatura longitudinale)
    MIN_ARMATURA_PERCENTUALE = 0.5   # 0,5% minimo
    MAX_ARMATURA_PERCENTUALE = 8.0   # 8% massimo per esigenza costruttiva
    
    # Per Fe < 2000 cm²: non inferiore a 0,8% della sezione
    # Per Fe > 8000 cm²: non inferiore a 0,5% della sezione
    # Per valori intermedi: interpolazione lineare tra i due limiti


# ============================================================================
# FUNZIONI AUSILIARIE PER ACCESSO TABELLE
# ============================================================================

def get_resistenza_calcestruzzo(rapporto_ac: float, tipo_cemento: str = "normale") -> Optional[float]:
    """
    Recupera la resistenza di compressione da Tabella II.
    
    Args:
        rapporto_ac: Rapporto A/C (es. 0.40, 0.50, 0.80)
        tipo_cemento: "normale", "alta_resistenza", "alluminoso"
    
    Returns:
        Resistenza in Kg/cm² a 28 giorni, oppure None se non trovata
    """
    # Cerca la chiave esatta o la più vicina
    for ac_nom, ac_val in RAPPORTI_AC_NOMINALI.items():
        if abs(ac_val - rapporto_ac) < 0.02:  # Tolleranza 0.02
            chiave = (ac_nom, tipo_cemento)
            if chiave in TABELLA_II_CALCESTRUZZO:
                return TABELLA_II_CALCESTRUZZO[chiave]
    
    return None


def interpola_resistenza_calcestruzzo(rapporto_ac: float, tipo_cemento: str = "normale") -> float:
    """
    Interpola linearmente la resistenza per A/C intermedi.
    
    Args:
        rapporto_ac: Rapporto A/C
        tipo_cemento: Tipo di cemento
    
    Returns:
        Resistenza interpolata in Kg/cm²
    """
    # Ordina i rapporti A/C disponibili
    ac_disponibili = sorted(RAPPORTI_AC_NOMINALI.values())
    
    # Trova i due valori più vicini
    for i in range(len(ac_disponibili) - 1):
        ac1 = ac_disponibili[i]
        ac2 = ac_disponibili[i + 1]
        
        if ac1 <= rapporto_ac <= ac2:
            # Ottieni le chiavi stringhe
            ac1_str = [k for k, v in RAPPORTI_AC_NOMINALI.items() if v == ac1][0]
            ac2_str = [k for k, v in RAPPORTI_AC_NOMINALI.items() if v == ac2][0]
            
            sigma1 = TABELLA_II_CALCESTRUZZO.get((ac1_str, tipo_cemento))
            sigma2 = TABELLA_II_CALCESTRUZZO.get((ac2_str, tipo_cemento))
            
            if sigma1 is not None and sigma2 is not None:
                # Interpolazione lineare
                peso = (rapporto_ac - ac1) / (ac2 - ac1)
                sigma_interpol = sigma1 + peso * (sigma2 - sigma1)
                return sigma_interpol
    
    # Fallback: se fuori range, usa il valore più vicino
    if rapporto_ac < ac_disponibili[0]:
        ac_str = [k for k, v in RAPPORTI_AC_NOMINALI.items() if v == ac_disponibili[0]][0]
        return TABELLA_II_CALCESTRUZZO.get((ac_str, tipo_cemento), 380)
    else:
        ac_str = [k for k, v in RAPPORTI_AC_NOMINALI.items() if v == ac_disponibili[-1]][0]
        return TABELLA_II_CALCESTRUZZO.get((ac_str, tipo_cemento), 140)
