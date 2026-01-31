"""
Tabella Malta - Quantitativi di Cemento e Sabbia.

Fonte: RD 2229/1939 - Tabella III pag. 6-7
       Prontuario dell'Ing. Luigi Santarella
       "Quantitativi di cemento e sabbia per 1 m³ di malta"

Contiene:
- Dosatura maltana in rapporti volumetrici A/C
- Quantitativi cemento e sabbia per metro cubo
- Pesi specifici apparenti
- Percentuali umidità (quando disponibili)
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DosaturaMalta:
    """Dosatura malta per 1 m³."""
    
    rapporto_ac: str                   # Es. "1:1", "1:1.40"
    rapporto_ac_numerico: float        # Es. 1.0, 1.40
    cemento_kg: float                  # kg/m³
    sabbia_kg: float                   # kg/m³
    peso_specifico_apparente: float    # kg/m³
    umidita_percentuale: Optional[float] = None  # %


# ============================================================================
# TABELLA III - DOSATURA MALTA PER 1 M³
# Da pag. 6-7 del documento RD 2229 (Santarella)
# ============================================================================

TABELLA_III_MALTA = [
    DosaturaMalta(
        rapporto_ac="1:1",
        rapporto_ac_numerico=1.0,
        cemento_kg=1050,
        sabbia_kg=900,
        peso_specifico_apparente=1100,
        umidita_percentuale=None
    ),
    DosaturaMalta(
        rapporto_ac="1:1.40",
        rapporto_ac_numerico=1.40,
        cemento_kg=800,
        sabbia_kg=1080,
        peso_specifico_apparente=1080,
        umidita_percentuale=None
    ),
    DosaturaMalta(
        rapporto_ac="1:1.85",
        rapporto_ac_numerico=1.85,
        cemento_kg=715,
        sabbia_kg=1215,
        peso_specifico_apparente=1080,
        umidita_percentuale=None
    ),
    DosaturaMalta(
        rapporto_ac="1:2.30",
        rapporto_ac_numerico=2.30,
        cemento_kg=685,
        sabbia_kg=1405,
        peso_specifico_apparente=1080,
        umidita_percentuale=None
    ),
    DosaturaMalta(
        rapporto_ac="1:2.70",
        rapporto_ac_numerico=2.70,
        cemento_kg=625,
        sabbia_kg=1520,
        peso_specifico_apparente=1100,
        umidita_percentuale=None
    ),
    DosaturaMalta(
        rapporto_ac="1:3.70",
        rapporto_ac_numerico=3.70,
        cemento_kg=385,
        sabbia_kg=1530,
        peso_specifico_apparente=1070,
        umidita_percentuale=None
    ),
]


# ============================================================================
# DIZIONARIO ACCESSO VELOCE
# ============================================================================

MALTA_PER_RAPPORTO: Dict[str, DosaturaMalta] = {
    dosatura.rapporto_ac: dosatura
    for dosatura in TABELLA_III_MALTA
}

MALTA_PER_RAPPORTO_NUMERICO: Dict[float, DosaturaMalta] = {
    dosatura.rapporto_ac_numerico: dosatura
    for dosatura in TABELLA_III_MALTA
}


# ============================================================================
# FUNZIONI AUSILIARIE
# ============================================================================

def get_malta_da_rapporto(rapporto_ac: str) -> Optional[DosaturaMalta]:
    """
    Recupera dosatura malta da rapporto A/C.
    
    Args:
        rapporto_ac: Rapporto in formato stringa (es. "1:1", "1:1.40")
    
    Returns:
        Oggetto DosaturaMalta o None se non trovato
    """
    return MALTA_PER_RAPPORTO.get(rapporto_ac)


def get_malta_da_rapporto_numerico(rapporto: float) -> Optional[DosaturaMalta]:
    """
    Recupera dosatura malta da rapporto numerico.
    
    Args:
        rapporto: Rapporto numerico (es. 1.0, 1.40, 2.70)
    
    Returns:
        Oggetto DosaturaMalta o None se non trovato
    """
    # Cerca il valore esatto o il più vicino
    for rap_nominale, dosatura in sorted(MALTA_PER_RAPPORTO_NUMERICO.items()):
        if abs(rap_nominale - rapporto) < 0.1:
            return dosatura
    
    return None


def interpola_dosatura_malta(rapporto_ac: float) -> Optional[Dict[str, float]]:
    """
    Interpola linealmente dosatura per rapporti A/C intermedi.
    
    Args:
        rapporto_ac: Rapporto A/C numerico
    
    Returns:
        Dizionario con cemento_kg, sabbia_kg, peso_specifico_apparente
    """
    rapporti_ordinati = sorted(MALTA_PER_RAPPORTO_NUMERICO.keys())
    
    # Verifica se è un valore tabulato
    for rap in rapporti_ordinati:
        if abs(rap - rapporto_ac) < 0.05:
            dosatura = MALTA_PER_RAPPORTO_NUMERICO[rap]
            return {
                "cemento_kg": dosatura.cemento_kg,
                "sabbia_kg": dosatura.sabbia_kg,
                "peso_specifico_apparente": dosatura.peso_specifico_apparente,
            }
    
    # Interpolazione lineare tra due valori
    for i in range(len(rapporti_ordinati) - 1):
        rap1 = rapporti_ordinati[i]
        rap2 = rapporti_ordinati[i + 1]
        
        if rap1 <= rapporto_ac <= rap2:
            dosatura1 = MALTA_PER_RAPPORTO_NUMERICO[rap1]
            dosatura2 = MALTA_PER_RAPPORTO_NUMERICO[rap2]
            
            # Peso interpolazione
            peso = (rapporto_ac - rap1) / (rap2 - rap1)
            
            cemento_interp = dosatura1.cemento_kg + peso * (dosatura2.cemento_kg - dosatura1.cemento_kg)
            sabbia_interp = dosatura1.sabbia_kg + peso * (dosatura2.sabbia_kg - dosatura1.sabbia_kg)
            peso_spec_interp = dosatura1.peso_specifico_apparente + peso * (dosatura2.peso_specifico_apparente - dosatura1.peso_specifico_apparente)
            
            return {
                "cemento_kg": cemento_interp,
                "sabbia_kg": sabbia_interp,
                "peso_specifico_apparente": peso_spec_interp,
            }
    
    return None


def calcola_malta_per_volume(rapporto_ac: float, volume_m3: float) -> Optional[Dict[str, float]]:
    """
    Calcola quantitativi malta per un volume dato.
    
    Args:
        rapporto_ac: Rapporto A/C numerico
        volume_m3: Volume di malta richiesto in m³
    
    Returns:
        Dizionario con quantitativi in kg
    """
    dosatura = interpola_dosatura_malta(rapporto_ac)
    
    if dosatura is None:
        return None
    
    return {
        "cemento_kg": dosatura["cemento_kg"] * volume_m3,
        "sabbia_kg": dosatura["sabbia_kg"] * volume_m3,
        "peso_specifico_apparente": dosatura["peso_specifico_apparente"],
        "peso_totale_malta": dosatura["peso_specifico_apparente"] * volume_m3,
    }


def genera_tabella_malta_testo() -> str:
    """
    Genera rappresentazione testuale della Tabella III.
    
    Returns:
        Stringa formattata della tabella
    """
    output = []
    output.append("=" * 80)
    output.append("TABELLA III - QUANTITATIVI DI CEMENTO E SABBIA PER 1 m³ DI MALTA")
    output.append("Fonte: RD 2229/1939 - Prontuario Santarella (pag. 6-7)")
    output.append("=" * 80)
    output.append("")
    output.append(f"{'Rapporto A/C':<15} {'Cemento (kg)':<15} {'Sabbia (kg)':<15} {'Peso spec. app.':<18}")
    output.append(f"{'':15} {'per m³':<15} {'per m³':<15} {'(kg/m³)':<18}")
    output.append("-" * 80)
    
    for dosatura in TABELLA_III_MALTA:
        output.append(
            f"{dosatura.rapporto_ac:<15} {dosatura.cemento_kg:>6.0f} kg{'':<7} "
            f"{dosatura.sabbia_kg:>6.0f} kg{'':<7} {dosatura.peso_specifico_apparente:>6.0f}"
        )
    
    output.append("=" * 80)
    output.append("")
    
    return "\n".join(output)


def genera_tabella_malta_html() -> str:
    """
    Genera rappresentazione HTML della Tabella III.
    
    Returns:
        String HTML
    """
    html = []
    html.append('<div class="tabella-malta">')
    html.append('<h3>Tabella III - Quantitativi Cemento e Sabbia per 1 m³ Malta</h3>')
    html.append('<table border="1" cellpadding="8">')
    html.append('<tr><th>Rapporto A/C</th><th>Cemento (kg/m³)</th><th>Sabbia (kg/m³)</th><th>Peso spec. app. (kg/m³)</th></tr>')
    
    for dosatura in TABELLA_III_MALTA:
        html.append(
            f'<tr>'
            f'<td>{dosatura.rapporto_ac}</td>'
            f'<td>{dosatura.cemento_kg:.0f}</td>'
            f'<td>{dosatura.sabbia_kg:.0f}</td>'
            f'<td>{dosatura.peso_specifico_apparente:.0f}</td>'
            f'</tr>'
        )
    
    html.append('</table>')
    html.append('</div>')
    
    return "\n".join(html)
