"""Test esecuzione Dati Storici RD 2229."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.materials.acciaio import Acciaio
from verifiche_dm1939.core.conversioni_unita import kgcm2_to_mpa, mpa_to_kgcm2
from verifiche_dm1939.core.dati_storici_rd2229 import CarichUnitariSicurezza

print("\n" + "="*70)
print("ESECUZIONE DATI STORICI RD 2229/1939 SANTARELLA")
print("="*70)

# Test 1: Conversioni
print("\nTEST 1: CONVERSIONI UNITA (Kg/cm2 <-> MPa)")
print("-"*70)
valori_test = [280, 40, 4, 1400]
for val_kgcm2 in valori_test:
    val_mpa = kgcm2_to_mpa(val_kgcm2)
    val_riconvertito = mpa_to_kgcm2(val_mpa)
    print(f"{val_kgcm2:4.0f} Kg/cm2 = {val_mpa:7.3f} MPa = {val_riconvertito:6.1f} Kg/cm2")

# Test 2: Calcestruzzo storico
print("\nTEST 2: CALCESTRUZZO DA TABELLA STORICA (280 Kg/cm2)")
print("-"*70)
cls_storico = Calcestruzzo.da_tabella_storica(
    resistenza_compressione_kgcm2=280,
    tipo_cemento="normale",
    rapporto_ac=0.50
)
print(f"Rck: {cls_storico.resistenza_caratteristica:.2f} MPa ({mpa_to_kgcm2(cls_storico.resistenza_caratteristica):.0f} Kg/cm2)")
print(f"sigma_c,amm: {cls_storico.tensione_ammissibile_compressione:.2f} MPa ({mpa_to_kgcm2(cls_storico.tensione_ammissibile_compressione):.0f} Kg/cm2)")
print(f"tau_c,amm: {cls_storico.tensione_ammissibile_taglio:.3f} MPa ({mpa_to_kgcm2(cls_storico.tensione_ammissibile_taglio):.1f} Kg/cm2)")
print(f"Ec (formula Santarella): {cls_storico.modulo_elastico:.0f} MPa")
print(f"n (Es/Ec): {cls_storico.coefficiente_omogeneizzazione:.1f}")

# Test 3: Acciaio storico
print("\nTEST 3: ACCIAIO DA TABELLA STORICA (1400 Kg/cm2)")
print("-"*70)
acc_storico = Acciaio.da_tabella_storica(
    resistenza_kgcm2=1400,
    tipo_acciaio="dolce"
)
print(f"Tipo: {acc_storico.tipo}")
print(f"fyk: {acc_storico.tensione_snervamento:.0f} MPa ({mpa_to_kgcm2(acc_storico.tensione_snervamento):.0f} Kg/cm2)")
print(f"sigma_s,amm: {acc_storico.tensione_ammissibile:.1f} MPa ({mpa_to_kgcm2(acc_storico.tensione_ammissibile):.0f} Kg/cm2)")
print(f"Aderenza: {'Migliorata' if acc_storico.aderenza_migliorata else 'Liscia'}")

# Test 4: Carichi unitari
print("\nTEST 4: CARICHI UNITARI DI SICUREZZA")
print("-"*70)
print(f"Compressione cls (inflesso, normale): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_NORM} Kg/cm2")
print(f"Compressione cls (inflesso, alta res.): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_ALT} Kg/cm2")
print(f"Taglio cls (normale): {CarichUnitariSicurezza.TAU_TAGLIO_NORMALE} Kg/cm2")
print(f"Taglio cls (alta resistenza): {CarichUnitariSicurezza.TAU_TAGLIO_ALTA_RESISTENZA} Kg/cm2")

print("\n" + "="*70)
print("ESECUZIONE COMPLETATA - OK")
print("="*70)
