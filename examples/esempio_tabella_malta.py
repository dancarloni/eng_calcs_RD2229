"""
Esempio utilizzo Tabella III Malta - Quantitativi Cemento e Sabbia.

Mostra come usare la tabella per:
- Consultare dosature standard
- Interpolare per rapporti intermedi
- Calcolare quantitativi per volume specifico
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from verifiche_dm1939.core.tabella_malta import (
    TABELLA_III_MALTA,
    MALTA_PER_RAPPORTO,
    get_malta_da_rapporto,
    interpola_dosatura_malta,
    calcola_malta_per_volume,
    genera_tabella_malta_testo,
    genera_tabella_malta_html,
)


def esempio_1_lettura_tabella():
    """Esempio 1: Lettura della Tabella III."""
    print("\n" + "="*80)
    print("ESEMPIO 1 - LETTURA TABELLA III - QUANTITATIVI MALTA")
    print("="*80 + "\n")
    
    print(genera_tabella_malta_testo())


def esempio_2_consultazione_rapporto():
    """Esempio 2: Consultazione dosatura per rapporto specifico."""
    print("\n" + "="*80)
    print("ESEMPIO 2 - CONSULTAZIONE DOSATURA PER RAPPORTO A/C")
    print("="*80 + "\n")
    
    rapporto_ricerca = "1:1.85"
    
    dosatura = get_malta_da_rapporto(rapporto_ricerca)
    
    if dosatura:
        print(f"Dosatura per rapporto A/C = {rapporto_ricerca}:\n")
        print(f"  Cemento: {dosatura.cemento_kg} kg/m³")
        print(f"  Sabbia: {dosatura.sabbia_kg} kg/m³")
        print(f"  Peso specifico apparente: {dosatura.peso_specifico_apparente} kg/m³")
        print()
        print(f"  Composizione per m³:")
        print(f"    - {dosatura.cemento_kg} kg di cemento")
        print(f"    - {dosatura.sabbia_kg} kg di sabbia")
        print(f"    - Peso totale malta: {dosatura.peso_specifico_apparente} kg")
    else:
        print(f"Rapporto A/C '{rapporto_ricerca}' non trovato in tabella")


def esempio_3_interpolazione():
    """Esempio 3: Interpolazione per rapporti intermedi."""
    print("\n" + "="*80)
    print("ESEMPIO 3 - INTERPOLAZIONE PER RAPPORTI INTERMEDI")
    print("="*80 + "\n")
    
    print("Rapporti A/C intermedi (non in tabella) vengono interpolati:\n")
    
    rapporti_test = [1.0, 1.2, 1.5, 1.75, 2.0, 2.5, 3.0, 3.7]
    
    print(f"{'Rapporto A/C':<15} {'Cemento (kg)':<15} {'Sabbia (kg)':<15} {'Peso spec. (kg)':<15}")
    print("-" * 65)
    
    for rapporto in rapporti_test:
        dosatura = interpola_dosatura_malta(rapporto)
        if dosatura:
            print(
                f"{rapporto:<15.2f} "
                f"{dosatura['cemento_kg']:>6.0f} kg{'':<7} "
                f"{dosatura['sabbia_kg']:>6.0f} kg{'':<7} "
                f"{dosatura['peso_specifico_apparente']:>6.0f}"
            )


def esempio_4_calcolo_volume():
    """Esempio 4: Calcolo quantitativi per volume specifico."""
    print("\n" + "="*80)
    print("ESEMPIO 4 - CALCOLO QUANTITATIVI PER VOLUME SPECIFICO")
    print("="*80 + "\n")
    
    rapporto = 1.5
    volume_m3 = 0.5  # 500 litri di malta
    
    print(f"Scenario: Preparo malta con rapporto A/C = {rapporto}")
    print(f"          Volume richiesto: {volume_m3} m³ (= {volume_m3*1000:.0f} litri)\n")
    
    quantitativo = calcola_malta_per_volume(rapporto, volume_m3)
    
    if quantitativo:
        print(f"Quantitativi necessari:\n")
        print(f"  Cemento: {quantitativo['cemento_kg']:.1f} kg")
        print(f"  Sabbia: {quantitativo['sabbia_kg']:.1f} kg")
        print(f"  Peso totale malta: {quantitativo['peso_totale_malta']:.1f} kg")
        print()
        print(f"Peso specifico apparente: {quantitativo['peso_specifico_apparente']:.0f} kg/m³")


def esempio_5_calcolo_malta_per_intonaco():
    """Esempio 5: Calcolo malta per intonaco."""
    print("\n" + "="*80)
    print("ESEMPIO 5 - CALCOLO MALTA PER INTONACO")
    print("="*80 + "\n")
    
    # Intonaco tipico: rapporto A/C = 1:2.30
    rapporto = 2.30
    
    # Superficie da intonacare: 100 m² con spessore 2 cm
    superficie_m2 = 100
    spessore_m = 0.02
    volume_m3 = superficie_m2 * spessore_m
    
    print(f"Intonaco su superficie: {superficie_m2} m²")
    print(f"Spessore intonaco: {spessore_m*100:.1f} cm")
    print(f"Volume malta necessario: {volume_m3} m³")
    print(f"Rapporto A/C: 1:{rapporto}\n")
    
    dosatura = interpola_dosatura_malta(rapporto)
    
    if dosatura:
        cemento_tot = dosatura['cemento_kg'] * volume_m3
        sabbia_tot = dosatura['sabbia_kg'] * volume_m3
        
        print(f"Quantitativi malta necessaria:\n")
        print(f"  Cemento: {cemento_tot:.1f} kg (ca. {cemento_tot/50:.0f} sacchi da 50 kg)")
        print(f"  Sabbia: {sabbia_tot:.1f} kg")
        print(f"  Peso totale: {dosatura['peso_specifico_apparente'] * volume_m3:.0f} kg")


def esempio_6_confronto_rapporti():
    """Esempio 6: Confronto tra rapporti A/C diversi."""
    print("\n" + "="*80)
    print("ESEMPIO 6 - CONFRONTO TRA RAPPORTI A/C DIVERSI")
    print("="*80 + "\n")
    
    print("Effetto della variazione rapporto A/C su 1 m³ di malta:\n")
    print(f"{'Rapporto':<12} {'Cemento (kg)':<14} {'Sabbia (kg)':<14} {'Resistenza':<12}")
    print("-" * 55)
    
    resistenze = {
        "1:1": "Molto alta",
        "1:1.40": "Alta",
        "1:1.85": "Media-Alta",
        "1:2.30": "Media",
        "1:2.70": "Media-Bassa",
        "1:3.70": "Bassa"
    }
    
    for dosatura in TABELLA_III_MALTA:
        resistenza = resistenze.get(dosatura.rapporto_ac, "")
        print(
            f"{dosatura.rapporto_ac:<12} "
            f"{dosatura.cemento_kg:>6.0f} kg{'':<6} "
            f"{dosatura.sabbia_kg:>6.0f} kg{'':<6} "
            f"{resistenza}"
        )


def esempio_7_resa_malta():
    """Esempio 7: Calcolo resa della malta (volume effettivo)."""
    print("\n" + "="*80)
    print("ESEMPIO 7 - RESA DELLA MALTA (VOLUME EFFETTIVO VS TEORICO)")
    print("="*80 + "\n")
    
    print("La malta confezionata ha resa inferiore al volume teorico.\n")
    print("Resa tipica: 85-90% del volume teorico (per assestamento e porosità)\n")
    
    rapporto = 1.85
    volume_teorico = 1.0  # 1 m³
    resa_percentuale = 0.87  # 87%
    
    dosatura = interpola_dosatura_malta(rapporto)
    
    if dosatura:
        volume_effettivo = volume_teorico * resa_percentuale
        
        print(f"Rapporto A/C: 1:{rapporto}")
        print(f"Volume teorico (confezionamento): {volume_teorico} m³")
        print(f"Volume effettivo (dopo assestamento): {volume_effettivo} m³ ({resa_percentuale*100:.0f}%)")
        print()
        
        # Quantitativi per volume effettivo
        cemento_effettivo = dosatura['cemento_kg'] * volume_effettivo
        sabbia_effettiva = dosatura['sabbia_kg'] * volume_effettivo
        
        print(f"Quantitativi per volume effettivo:")
        print(f"  Cemento: {cemento_effettivo:.0f} kg")
        print(f"  Sabbia: {sabbia_effettiva:.0f} kg")


if __name__ == "__main__":
    esempio_1_lettura_tabella()
    esempio_2_consultazione_rapporto()
    esempio_3_interpolazione()
    esempio_4_calcolo_volume()
    esempio_5_calcolo_malta_per_intonaco()
    esempio_6_confronto_rapporti()
    esempio_7_resa_malta()
    
    print("\n" + "="*80)
    print("FINE ESEMPI - Tabella III Malta implementata e testata")
    print("="*80 + "\n")
