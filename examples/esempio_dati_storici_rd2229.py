"""
Esempi di utilizzo dei dati storici RD 2229/1939.

Mostra come usare le tabelle e formule dall'epoca di Santarella.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.core.dati_storici_rd2229 import (
    TABELLA_II_CALCESTRUZZO,
    CarichUnitariSicurezza,
    modulo_elasticita_calcestruzzo_kgcm2,
    interpola_resistenza_calcestruzzo,
)
from verifiche_dm1939.core.conversioni_unita import kgcm2_to_mpa, mpa_to_kgcm2


def esempio_1_tabella_ii():
    """Esempio 1: Lettura della Tabella II - Rapporti A/C e Resistenze."""
    print("\n" + "="*70)
    print("ESEMPIO 1 - TABELLA II RD 2229: RAPPORTI A/C E RESISTENZE")
    print("="*70 + "\n")
    
    print("Resistenze di compressione a 28 giorni [Kg/cm²]\n")
    print("A/C      | Cemento Normale | Alta Resistenza | Alluminoso")
    print("-" * 65)
    
    for ac_nom in ["0,40", "0,50", "0,60", "0,70", "0,80"]:
        sigma_norm = TABELLA_II_CALCESTRUZZO.get((ac_nom, "normale"), "-")
        sigma_alt = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alta_resistenza"), "-")
        sigma_allum = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alluminoso"), "-")
        print(f"{ac_nom:7} | {str(sigma_norm):15} | {str(sigma_alt):15} | {str(sigma_allum):9}")
    
    print("\nConversione in MPa:")
    sigma_280_kgcm2 = 280  # Valore da tabella per A/C=0.50, cemento normale
    sigma_280_mpa = kgcm2_to_mpa(sigma_280_kgcm2)
    print(f"  280 Kg/cm² = {sigma_280_mpa:.2f} MPa")


def esempio_2_carichi_unitari():
    """Esempio 2: Carichi unitari di sicurezza da RD 2229."""
    print("\n" + "="*70)
    print("ESEMPIO 2 - CARICHI UNITARI DI SICUREZZA (RD 2229)")
    print("="*70 + "\n")
    
    print("COMPRESSIONE NEL CALCESTRUZZO:")
    print(f"  Sezioni semplicemente compresse (normale): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_NORM} Kg/cm²")
    print(f"  Sezioni semplicemente compresse (alta res.): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_ALT} Kg/cm²")
    print(f"  Sezioni inflesse (normale): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_NORM} Kg/cm²")
    print(f"  Sezioni inflesse (alta res.): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_ALT} Kg/cm²")
    
    print("\nTAGLIO NEL CALCESTRUZZO:")
    print(f"  Cemento normale: {CarichUnitariSicurezza.TAU_TAGLIO_NORMALE} Kg/cm²")
    print(f"  Cemento alta resistenza: {CarichUnitariSicurezza.TAU_TAGLIO_ALTA_RESISTENZA} Kg/cm²")
    print(f"  Cemento alluminoso: {CarichUnitariSicurezza.TAU_TAGLIO_ALLUMINOSO} Kg/cm²")
    
    print("\nACCIAI:")
    print(f"  Acciaio dolce max: {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_DOLCE_NORMAL} Kg/cm²")
    print(f"  Acciaio semiriduro max: {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_SEMI} Kg/cm²")
    print(f"  Acciaio duro max: {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_DURO_NORMAL} Kg/cm²")


def esempio_3_modulo_elastico():
    """Esempio 3: Calcolo modulo elastico da formula storica Santarella."""
    print("\n" + "="*70)
    print("ESEMPIO 3 - MODULO ELASTICO (FORMULA STORICA SANTARELLA)")
    print("="*70 + "\n")
    
    print("Formula: Ec = 550000 · σc / (σc + 200) [Kg/cm²]\n")
    
    for sigma_c in [250, 280, 350]:
        ec = modulo_elasticita_calcestruzzo_kgcm2(sigma_c)
        ec_mpa = kgcm2_to_mpa(ec)
        n = 2_000_000 / ec  # Coefficiente omogeneizzazione
        print(f"σc = {sigma_c:3d} Kg/cm²  →  Ec = {ec:7.0f} Kg/cm² = {ec_mpa:7.0f} MPa  →  n = {n:4.1f}")


def esempio_4_calcestruzzo_storico():
    """Esempio 4: Creare un calcestruzzo usando dati storici."""
    print("\n" + "="*70)
    print("ESEMPIO 4 - CREAZIONE CALCESTRUZZO DA DATI STORICI")
    print("="*70 + "\n")
    
    # Scenario: Calcestruzzo con resistenza 280 Kg/cm² (A/C=0.50, cemento normale)
    print("Scenario: A/C = 0.50, Cemento normale → σc = 280 Kg/cm²\n")
    
    cls_storico = Calcestruzzo.da_tabella_storica(
        resistenza_compressione_kgcm2=280,
        tipo_cemento="normale",
        rapporto_ac=0.50
    )
    
    print(f"Calcestruzzo creato:")
    print(f"  Rck: {cls_storico.resistenza_caratteristica:.2f} MPa ({mpa_to_kgcm2(cls_storico.resistenza_caratteristica):.0f} Kg/cm²)")
    print(f"  Modulo elastico: {cls_storico.modulo_elastico:.0f} MPa ({mpa_to_kgcm2(cls_storico.modulo_elastico):.0f} Kg/cm²)")
    print(f"  Tensione ammissibile compressione: {cls_storico.tensione_ammissibile_compressione:.2f} MPa ({mpa_to_kgcm2(cls_storico.tensione_ammissibile_compressione):.0f} Kg/cm²)")
    print(f"  Tensione ammissibile taglio: {cls_storico.tensione_ammissibile_taglio:.3f} MPa ({mpa_to_kgcm2(cls_storico.tensione_ammissibile_taglio):.1f} Kg/cm²)")
    print(f"  Coefficiente omogeneizzazione: n = {cls_storico.coefficiente_omogeneizzazione:.1f}")


def esempio_5_interpolazione():
    """Esempio 5: Interpolazione per A/C intermedi."""
    print("\n" + "="*70)
    print("ESEMPIO 5 - INTERPOLAZIONE PER A/C INTERMEDI")
    print("="*70 + "\n")
    
    print("Interpolazione lineare per valori A/C tra quelli tabulati:\n")
    
    for ac in [0.42, 0.55, 0.75]:
        sigma_c = interpola_resistenza_calcestruzzo(ac, tipo_cemento="normale")
        sigma_c_mpa = kgcm2_to_mpa(sigma_c)
        print(f"A/C = {ac} → σc = {sigma_c:.0f} Kg/cm² = {sigma_c_mpa:.2f} MPa")


def esempio_6_confronto_moderno_vs_storico():
    """Esempio 6: Confronto tra calcolo moderno e storico."""
    print("\n" + "="*70)
    print("ESEMPIO 6 - CONFRONTO CALCOLO MODERNO VS STORICO")
    print("="*70 + "\n")
    
    rck_mpa = 27.5  # Equivalente a 280 Kg/cm²
    
    # Metodo moderno
    cls_moderno = Calcestruzzo(
        resistenza_caratteristica=rck_mpa,
        calcola_auto=True,
        da_tabella_storica=False
    )
    
    # Metodo storico
    cls_storico = Calcestruzzo(
        resistenza_caratteristica=rck_mpa,
        calcola_auto=True,
        da_tabella_storica=True,
        tipo_cemento="normale"
    )
    
    print(f"Per Rck = {rck_mpa} MPa ({mpa_to_kgcm2(rck_mpa):.0f} Kg/cm²):\n")
    
    print("METODO MODERNO (formule semplici):")
    print(f"  σc,amm = Rck/3 = {cls_moderno.tensione_ammissibile_compressione:.2f} MPa")
    print(f"  τc,amm = 0.054·Rck = {cls_moderno.tensione_ammissibile_taglio:.3f} MPa")
    print(f"  Ec = 5700·√Rck = {cls_moderno.modulo_elastico:.0f} MPa")
    print(f"  n = Es/Ec = {cls_moderno.coefficiente_omogeneizzazione:.1f}")
    
    print("\nMETODO STORICO (formule RD 2229 Santarella):")
    print(f"  σc,amm (carico unitario) = {cls_storico.tensione_ammissibile_compressione:.2f} MPa")
    print(f"  τc,amm (tab. carico) = {cls_storico.tensione_ammissibile_taglio:.3f} MPa")
    print(f"  Ec = 550000·σc/(σc+200) = {cls_storico.modulo_elastico:.0f} MPa")
    print(f"  n = Es/Ec = {cls_storico.coefficiente_omogeneizzazione:.1f}")
    
    print("\nDifferenze:")
    print(f"  Modulo elastico: {abs(cls_moderno.modulo_elastico - cls_storico.modulo_elastico):.0f} MPa ({abs(cls_moderno.modulo_elastico - cls_storico.modulo_elastico)/cls_storico.modulo_elastico*100:.1f}%)")


if __name__ == "__main__":
    esempio_1_tabella_ii()
    esempio_2_carichi_unitari()
    esempio_3_modulo_elastico()
    esempio_4_calcestruzzo_storico()
    esempio_5_interpolazione()
    esempio_6_confronto_moderno_vs_storico()
    
    print("\n" + "="*70)
    print("FINE ESEMPI - Dati storici RD 2229/1939 implementati")
    print("="*70 + "\n")
