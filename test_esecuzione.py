"""Test esecuzione Tabella III Malta."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from verifiche_dm1939.core.tabella_malta import (
    get_malta_da_rapporto,
    interpola_dosatura_malta,
    calcola_malta_per_volume,
    genera_tabella_malta_testo,
)

print("\n" + "="*70)
print("ESECUZIONE TABELLA III MALTA - RD 2229/1939")
print("="*70)

# Visualizza tabella completa
print(genera_tabella_malta_testo())

# Test 1: Consultazione
print("\nTEST 1: CONSULTAZIONE RAPPORTO TABULATO (1:1.85)")
print("-"*70)
dosatura = get_malta_da_rapporto("1:1.85")
print(f"Cemento: {dosatura.cemento_kg:.0f} kg/m3")
print(f"Sabbia: {dosatura.sabbia_kg:.0f} kg/m3")
print(f"Peso spec. apparente: {dosatura.peso_specifico_apparente:.0f} kg/m3")

# Test 2: Interpolazione
print("\nTEST 2: INTERPOLAZIONE RAPPORTO INTERMEDIO (1:2.00)")
print("-"*70)
dosatura_interp = interpola_dosatura_malta(2.0)
print(f"Cemento: {dosatura_interp['cemento_kg']:.0f} kg/m3")
print(f"Sabbia: {dosatura_interp['sabbia_kg']:.0f} kg/m3")

# Test 3: Calcolo per volume
print("\nTEST 3: CALCOLO MALTA PER INTONACO")
print("-"*70)
print("Scenario: Intonaco su 100 m2, spessore 2 cm, rapporto 1:2.30")
volume = 100 * 0.02
quant = calcola_malta_per_volume(2.30, volume)
print(f"Volume malta: {volume:.1f} m3")
print(f"Cemento: {quant['cemento_kg']:.0f} kg ({quant['cemento_kg']/50:.0f} sacchi 50kg)")
print(f"Sabbia: {quant['sabbia_kg']:.0f} kg")
print(f"Peso totale: {quant['peso_totale_malta']:.0f} kg")

print("\n" + "="*70)
print("ESECUZIONE COMPLETATA - OK")
print("="*70)
