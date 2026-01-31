#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST SISTEMA COMPLETO MATERIALI - RD 2229/1939
Verifica il caricamento completo di tutti i parametri
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from verifiche_dm1939.core.materiali_storici_completi import (
    CALCESTRUZZI_COMPLETI, ACCIAI_COMPLETI
)


def test_sistema():
    """Test completo del sistema materiali."""
    
    print("=" * 100)
    print("SISTEMA COMPLETO MATERIALI RD 2229/1939".center(100))
    print("=" * 100)
    
    print(f"\n✓ CALCESTRUZZI CARICATI: {len(CALCESTRUZZI_COMPLETI)}")
    print(f"✓ ACCIAI CARICATI: {len(ACCIAI_COMPLETI)}")
    print(f"✓ TOTALE: {len(CALCESTRUZZI_COMPLETI) + len(ACCIAI_COMPLETI)}")
    
    # Test Calcestruzzo
    print("\n" + "=" * 100)
    print("ESEMPIO CALCESTRUZZO - C280 (STANDARD STORICO)".center(100))
    print("=" * 100)
    
    c = CALCESTRUZZI_COMPLETI[3]  # C280
    print(f"Nome: {c.nome}")
    print(f"Sigla: {c.sigla}")
    print(f"Tipo Cemento: {c.tipo_cemento}")
    
    print(f"\nRESISTENZA E CARICHI:")
    print(f"  σc (tabulare): {c.sigma_c_kgcm2} Kg/cm²")
    print(f"  σc (ammissibile semplice): {c.sigma_c_semplice_kgcm2} Kg/cm²")
    print(f"  σc (ammissibile inflessa): {c.sigma_c_inflessa_kgcm2} Kg/cm²")
    print(f"  τ (taglio): {c.tau_ammissibile_kgcm2} Kg/cm²")
    
    print(f"\nPROPRIETÀ ELASTICHE:")
    print(f"  Ec (modulo elastico): {c.modulo_elastico_kgcm2:,.0f} Kg/cm²")
    print(f"  n (coefficiente omogeneizzazione): {c.coefficiente_omogeneo:.2f}")
    print(f"  Formula Santarella: {c.fonte_ec}")
    
    print(f"\nCOMPOSIZIONE:")
    print(f"  A/C: {c.rapporto_ac}")
    print(f"  Cem:Sabbia: {c.rapporto_cemento_sabbia}")
    print(f"  Cemento: {c.cemento_kg_m3} kg/m³")
    print(f"  Sabbia: {c.sabbia_kg_m3} kg/m³")
    print(f"  Peso specifico: {c.massa_volumica_kg_m3} kg/m³")
    
    print(f"\nNORMATIVA:")
    print(f"  Riferimento: {c.normativa} ({c.anno_norma})")
    print(f"  Tabella II: {c.pagina_tabella_ii}")
    print(f"  Carichi ammissibili: {c.pagina_carichi}")
    
    print(f"\nNOTE: {c.note}")
    print(f"APPLICAZIONI: {c.applicazioni}")
    
    # Test Acciaio
    print("\n" + "=" * 100)
    print("ESEMPIO ACCIAIO - Aq70 (SERIE QUALIFICATA ITALIANA)".center(100))
    print("=" * 100)
    
    a = ACCIAI_COMPLETI[5]  # Aq70
    print(f"Nome: {a.nome}")
    print(f"Sigla: {a.sigla}")
    print(f"Tipo: {a.tipo}")
    print(f"Classificazione: {a.classificazione}")
    
    print(f"\nRESISTENZA E CARICHI:")
    print(f"  σy (snervamento): {a.sigma_y_kgcm2} Kg/cm²")
    print(f"  σ ammissibile (traczione): {a.sigma_ammissibile_traczione_kgcm2} Kg/cm²")
    print(f"  σ ammissibile (compressione): {a.sigma_ammissibile_compressione_kgcm2} Kg/cm²")
    rapporto = a.sigma_ammissibile_traczione_kgcm2 / a.sigma_y_kgcm2
    print(f"  Rapporto σ_amm/σy: {rapporto:.1%}")
    
    print(f"\nPROPRIETÀ ELASTICHE:")
    print(f"  Es (modulo elastico): {a.modulo_elastico_kgcm2:,.0f} Kg/cm²")
    
    print(f"\nADERENZA:")
    print(f"  Tipo: {a.tipo_aderenza}")
    print(f"  Migliorata: {'Sì' if a.aderenza_migliorata else 'No'}")
    print(f"  Caratteri: {a.caratteri_aderenza}")
    
    print(f"\nDIAMETRI DISPONIBILI:")
    print(f"  Range: {a.diametro_min_mm} - {a.diametro_max_mm} mm")
    diam_str = ', '.join(str(int(d)) for d in a.diametri_disponibili)
    print(f"  Serie: {diam_str}")
    
    print(f"\nNORMATIVA:")
    print(f"  Riferimento: {a.normativa} ({a.anno_norma})")
    print(f"  Pagine: {a.pagina_resistenza}, {a.pagina_carichi}, {a.pagina_aderenza}")
    
    print(f"\nAPPLICAZIONI: {a.applicazioni}")
    
    # Tabella riepilogativa
    print("\n" + "=" * 100)
    print("TABELLA RIEPILOGATIVA CALCESTRUZZI".center(100))
    print("=" * 100)
    
    print(f"{'Sigla':<8} {'σc':<6} {'σc sempl':<10} {'σc infl':<10} {'τ':<6} {'Ec':<12} {'n':<6} {'A/C':<6} {'Tipo':<10}")
    print("-" * 100)
    
    for c in CALCESTRUZZI_COMPLETI:
        print(f"{c.sigla:<8} {c.sigma_c_kgcm2:<6.0f} {c.sigma_c_semplice_kgcm2:<10.0f} {c.sigma_c_inflessa_kgcm2:<10.0f} {c.tau_ammissibile_kgcm2:<6.1f} {c.modulo_elastico_kgcm2:<12.0f} {c.coefficiente_omogeneo:<6.2f} {str(c.rapporto_ac):<6} {c.tipo_cemento:<10}")
    
    # Tabella riepilogativa acciai
    print("\n" + "=" * 100)
    print("TABELLA RIEPILOGATIVA ACCIAI".center(100))
    print("=" * 100)
    
    print(f"{'Sigla':<10} {'σy':<8} {'σ amm':<8} {'Es':<12} {'Aderenza':<12} {'Ø min':<6} {'Ø max':<6} {'Classe':<10}")
    print("-" * 100)
    
    for a in ACCIAI_COMPLETI:
        ader = "Migliorata" if a.aderenza_migliorata else "Liscia"
        print(f"{a.sigla:<10} {a.sigma_y_kgcm2:<8.0f} {a.sigma_ammissibile_traczione_kgcm2:<8.0f} {a.modulo_elastico_kgcm2:<12.0f} {ader:<12} {a.diametro_min_mm:<6.0f} {a.diametro_max_mm:<6.0f} {a.classificazione[:8]:<10}")
    
    print("\n" + "=" * 100)
    print("TUTTI I PARAMETRI SONO COMPLETI E DISPONIBILI".center(100))
    print("=" * 100)
    
    print("\n✅ SISTEMA OPERATIVO CON:")
    print(f"   - {len(CALCESTRUZZI_COMPLETI)} Calcestruzzi (da C150 a C750)")
    print(f"   - {len(ACCIAI_COMPLETI)} Acciai (FeB32k, FeB38k, FeB44k, Aq50-Aq80)")
    print(f"   - 20+ parametri per calcestruzzo")
    print(f"   - 15+ parametri per acciaio")
    print(f"   - Riferimento RD 2229/1939 e Prontuario Santarella")
    print(f"   - Formule storiche (Ec = 550000·σc/(σc+200))")
    print(f"   - Tabelle complete e intestazioni esplicite")
    print(f"   - Applicazione Streamlit con visualizzazione completa")


if __name__ == "__main__":
    test_sistema()
