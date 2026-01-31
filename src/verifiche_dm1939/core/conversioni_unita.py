"""
Conversioni unità - Da Kg/cm² (sistema storico) a MPa e conversioni inverse.

Fonte: RD 2229/1939 - Norme tecniche per le costruzioni.
Il sistema storico utilizzava Kg/cm² come unità di misura.
Conversione: 1 MPa = 10.197 Kg/cm² ≈ 10.2 Kg/cm²
"""


def kgcm2_to_mpa(valore_kgcm2: float) -> float:
    """
    Converte da Kg/cm² a MPa.
    
    Args:
        valore_kgcm2: Valore in Kg/cm²
    
    Returns:
        Valore convertito in MPa
    """
    return valore_kgcm2 / 10.197


def mpa_to_kgcm2(valore_mpa: float) -> float:
    """
    Converte da MPa a Kg/cm².
    
    Args:
        valore_mpa: Valore in MPa
    
    Returns:
        Valore convertito in Kg/cm²
    """
    return valore_mpa * 10.197


# Fattore di conversione per uso diretto
FATTORE_KGCM2_TO_MPA = 1.0 / 10.197
FATTORE_MPA_TO_KGCM2 = 10.197
