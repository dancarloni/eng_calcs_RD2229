"""
Test esempio - Validazione con esempio da letteratura Santarella.

Esempio: Trave semplicemente appoggiata con dati storici RD 2229/1939
Dati dal testo "Il cemento armato" - Santarella, L.
"""

import sys
from pathlib import Path

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.materials.acciaio import Acciaio
from verifiche_dm1939.sections.sezione_rettangolare import SezioneRettangolare
from verifiche_dm1939.verifications.verifica_flessione import VerificaFlessione
from verifiche_dm1939.core.conversioni_unita import kgcm2_to_mpa, mpa_to_kgcm2
from verifiche_dm1939.core.dati_storici_rd2229 import CarichUnitariSicurezza


def test_esempio_santarella_trave():
    """
    Test con esempio da Santarella - Trave in c.a.
    
    Dati esempio storici (Kg/cm²):
    - Sezione: 300 x 500 mm
    - Cls: 280 Kg/cm² (Rck 27.5 MPa, A/C=0.50, cemento normale)
    - Acciaio: 1400 Kg/cm² (FeB32k - Acciaio dolce)
    - Armatura: 4φ16 inf.
    - Momento: 80 kNm
    
    Risultati attesi (da letteratura):
    - Asse neutro: x ≈ 140-150 mm
    - Momento resistente: Mr ≈ 85-90 kNm
    - Verifica: SODDISFATTA
    """
    print("\n" + "="*70)
    print("TEST VALIDAZIONE - Esempio da Santarella (Dati Storici RD 2229)")
    print("="*70 + "\n")
    
    # Materiali - da tabella storica RD 2229
    print("CREAZIONE MATERIALI DA DATI STORICI RD 2229:\n")
    
    cls = Calcestruzzo.da_tabella_storica(
        resistenza_compressione_kgcm2=280,
        tipo_cemento="normale",
        rapporto_ac=0.50
    )
    
    acc = Acciaio.da_tabella_storica(
        resistenza_kgcm2=1400,
        tipo_acciaio="dolce"
    )
    
    print(f"Calcestruzzo (storico RD 2229):")
    print(f"  σc = 280 Kg/cm² → Rck = {cls.resistenza_caratteristica:.2f} MPa")
    print(f"  σc,amm = {mpa_to_kgcm2(cls.tensione_ammissibile_compressione):.0f} Kg/cm² ({cls.tensione_ammissibile_compressione:.2f} MPa)")
    print(f"  τc,amm = {mpa_to_kgcm2(cls.tensione_ammissibile_taglio):.1f} Kg/cm² ({cls.tensione_ammissibile_taglio:.3f} MPa)")
    print(f"  Ec = {mpa_to_kgcm2(cls.modulo_elastico):.0f} Kg/cm² ({cls.modulo_elastico:.0f} MPa)")
    print(f"  n = {cls.coefficiente_omogeneizzazione:.1f}")
    print()
    
    print(f"Acciaio (storico RD 2229):")
    print(f"  Tipo: {acc.tipo} (fy = 1400 Kg/cm²)")
    print(f"  fyk = {acc.tensione_snervamento:.0f} MPa ({mpa_to_kgcm2(acc.tensione_snervamento):.0f} Kg/cm²)")
    print(f"  σs,amm = {acc.tensione_ammissibile:.1f} MPa ({mpa_to_kgcm2(acc.tensione_ammissibile):.0f} Kg/cm²)")
    print(f"  Aderenza: {'Migliorata' if acc.aderenza_migliorata else 'Liscia'}")
    print()
    
    # Sezione
    sezione = SezioneRettangolare(base=300, altezza=500, copriferro=30)
    sezione.aggiungi_armatura_inferiore(diametro=16, numero_barre=4)
    
    print(f"Sezione:")
    print(f"  Dimensioni: {sezione.base}x{sezione.altezza} mm")
    print(f"  Armatura: 4φ16 = {sezione.area_armatura_inferiore:.0f} mm²")
    print(f"  Altezza utile: d = {sezione.altezza_utile:.0f} mm")
    print()
    
    # Verifica
    verifica = VerificaFlessione(
        sezione=sezione,
        calcestruzzo=cls,
        acciaio=acc,
        momento_flettente=80.0  # kNm
    )
    
    risultato = verifica.verifica()
    
    # Confronto con valori attesi
    print("RISULTATI CALCOLATI:")
    print(f"  Posizione asse neutro: x = {risultato.posizione_asse_neutro:.1f} mm")
    print(f"  Momento resistente: Mr = {risultato.momento_resistente:.2f} kNm")
    print(f"  Tensione calcestruzzo: σc = {risultato.tensione_calcestruzzo:.2f} MPa ({mpa_to_kgcm2(risultato.tensione_calcestruzzo):.0f} Kg/cm²)")
    print(f"  Tensione acciaio: σs = {risultato.tensione_acciaio:.2f} MPa ({mpa_to_kgcm2(risultato.tensione_acciaio):.0f} Kg/cm²)")
    print()
    
    print("VALORI ATTESI (letteratura Santarella):")
    print("  Posizione asse neutro: x ≈ 140-150 mm")
    print("  Momento resistente: Mr ≈ 85-90 kNm")
    print()
    
    # Validazione
    validazione_x = 140 <= risultato.posizione_asse_neutro <= 150
    validazione_Mr = 85 <= risultato.momento_resistente <= 90
    validazione_verifica = risultato.verificato
    
    print("VALIDAZIONE:")
    print(f"  Asse neutro nel range atteso: {'✓ SI' if validazione_x else '✗ NO'}")
    print(f"  Momento resistente nel range atteso: {'✓ SI' if validazione_Mr else '✗ NO'}")
    print(f"  Verifica soddisfatta: {'✓ SI' if validazione_verifica else '✗ NO'}")
    print()
    
    if validazione_x and validazione_Mr and validazione_verifica:
        print("="*70)
        print("TEST SUPERATO ✓ - Dati storici RD 2229 validati con Santarella")
        print("="*70)
        return True
    else:
        print("="*70)
        print("TEST FALLITO ✗ - Verificare i calcoli")
        print("="*70)
        return False


def test_carichi_unitari_sicurezza():
    """Test validazione carichi unitari da RD 2229."""
    print("\n" + "="*70)
    print("TEST - Carichi Unitari di Sicurezza RD 2229")
    print("="*70 + "\n")
    
    print("Validazione costanti da tabelle storiche:\n")
    
    assert CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_NORM == 40, "σc,amm normale inflessa deve essere 40 Kg/cm²"
    assert CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_ALT == 50, "σc,amm alta resistenza inflessa deve essere 50 Kg/cm²"
    assert CarichUnitariSicurezza.TAU_TAGLIO_NORMALE == 4, "τ,amm normale deve essere 4 Kg/cm²"
    assert CarichUnitariSicurezza.TAU_TAGLIO_ALTA_RESISTENZA == 6, "τ,amm alta resistenza deve essere 6 Kg/cm²"
    assert CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_DOLCE_NORMAL == 1400, "σf,max acciaio dolce deve essere 1400 Kg/cm²"
    
    print("✓ Tutti i carichi unitari corrispondono alle tabelle RD 2229")
    print()
    
    # Conversione Kg/cm² → MPa
    sigma_c_40_mpa = kgcm2_to_mpa(40)
    tau_4_mpa = kgcm2_to_mpa(4)
    
    print(f"Conversioni:")
    print(f"  40 Kg/cm² = {sigma_c_40_mpa:.2f} MPa")
    print(f"  4 Kg/cm² = {tau_4_mpa:.3f} MPa")
    print()
    
    print("="*70)
    print("TEST SUPERATO ✓ - Carichi unitari validati")
    print("="*70)
    return True


def test_materiali():
    """Test creazione e proprietà materiali."""
    print("\n" + "="*70)
    print("TEST MATERIALI")
    print("="*70 + "\n")
    
    # Test calcestruzzo
    cls_15 = Calcestruzzo.da_classe("Rck15")
    assert cls_15.resistenza_caratteristica == 15.0
    assert cls_15.tensione_ammissibile_compressione == 5.0  # 15/3
    print(f"✓ Calcestruzzo Rck15: σc,amm = {cls_15.tensione_ammissibile_compressione} MPa")
    
    cls_20 = Calcestruzzo(resistenza_caratteristica=20.0, calcola_auto=True)
    assert abs(cls_20.tensione_ammissibile_compressione - 6.67) < 0.1
    print(f"✓ Calcestruzzo Rck20: σc,amm = {cls_20.tensione_ammissibile_compressione:.2f} MPa")
    
    # Test acciaio
    feb32 = Acciaio.da_tipo("FeB32k")
    assert feb32.tensione_snervamento == 320.0
    assert 135 < feb32.tensione_ammissibile < 145  # 320/2.3 ≈ 139
    print(f"✓ Acciaio FeB32k: σs,amm = {feb32.tensione_ammissibile:.1f} MPa")
    
    feb38 = Acciaio.da_tipo("FeB38k")
    assert feb38.tensione_snervamento == 375.0
    print(f"✓ Acciaio FeB38k: σs,amm = {feb38.tensione_ammissibile:.1f} MPa")
    
    print("\nTest materiali completato con successo ✓")


def test_sezione():
    """Test creazione sezione e armature."""
    print("\n" + "="*70)
    print("TEST SEZIONE")
    print("="*70 + "\n")
    
    sez = SezioneRettangolare(base=300, altezza=500, copriferro=30)
    assert sez.area_calcestruzzo == 150000  # mm²
    print(f"✓ Area sezione: {sez.area_calcestruzzo} mm²")
    
    sez.aggiungi_armatura_inferiore(diametro=16, numero_barre=4)
    area_attesa = 4 * 3.14159 * 8**2  # 4 * π * r²
    assert abs(sez.area_armatura_inferiore - area_attesa) < 10
    print(f"✓ Area armatura 4φ16: {sez.area_armatura_inferiore:.0f} mm²")
    
    # Altezza utile
    d_atteso = 500 - 30 - 8  # h - c - φ/2
    assert abs(sez.altezza_utile - d_atteso) < 5
    print(f"✓ Altezza utile: {sez.altezza_utile:.1f} mm")
    
    # Staffe
    sez.aggiungi_staffe(diametro=8, passo=200, numero_bracci=2)
    assert sez.staffe is not None
    assert sez.staffe.passo == 200
    print(f"✓ Staffe: φ{sez.staffe.diametro}/{sez.staffe.passo}")
    
    print("\nTest sezione completato con successo ✓")


if __name__ == "__main__":
    print("\n" + "╔"+"═"*68+"╗")
    print("║" + " "*15 + "TEST VALIDAZIONE VERIFICHE DM 1939" + " "*19 + "║")
    print("╚"+"═"*68+"╝")
    
    # Esegui test
    test_materiali()
    test_sezione()
    successo = test_esempio_santarella_trave()
    
    print("\n" + "="*70)
    if successo:
        print("TUTTI I TEST COMPLETATI CON SUCCESSO ✓✓✓")
    else:
        print("ALCUNI TEST FALLITI - VERIFICARE")
    print("="*70 + "\n")
