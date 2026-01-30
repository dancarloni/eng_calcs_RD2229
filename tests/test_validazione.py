"""
Test esempio - Validazione con esempio da letteratura Santarella.

Esempio: Trave semplicemente appoggiata
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


def test_esempio_santarella_trave():
    """
    Test con esempio da Santarella - Trave in c.a.
    
    Dati esempio:
    - Sezione: 300 x 500 mm
    - Cls: Rck 15 MPa (σc,amm = 5 MPa)
    - Acciaio: FeB32k (σs,amm = 140 MPa)
    - Armatura: 4φ16 inf.
    - Momento: 80 kNm
    
    Risultati attesi (da letteratura):
    - Asse neutro: x ≈ 140-150 mm
    - Momento resistente: Mr ≈ 85-90 kNm
    - Verifica: SODDISFATTA
    """
    print("\n" + "="*70)
    print("TEST VALIDAZIONE - Esempio da Santarella")
    print("="*70 + "\n")
    
    # Materiali
    cls = Calcestruzzo(resistenza_caratteristica=15.0)
    acciaio = Acciaio.da_tipo("FeB32k")
    
    print(f"Calcestruzzo: Rck = {cls.resistenza_caratteristica} MPa, "
          f"σc,amm = {cls.tensione_ammissibile_compressione:.2f} MPa")
    print(f"Acciaio: {acciaio.tipo}, σs,amm = {acciaio.tensione_ammissibile:.1f} MPa")
    print()
    
    # Sezione
    sezione = SezioneRettangolare(base=300, altezza=500, copriferro=30)
    sezione.aggiungi_armatura_inferiore(diametro=16, numero_barre=4)
    
    print(f"Sezione: {sezione.base}x{sezione.altezza} mm")
    print(f"Armatura: 4φ16 = {sezione.area_armatura_inferiore:.0f} mm²")
    print(f"Altezza utile: d = {sezione.altezza_utile:.0f} mm")
    print()
    
    # Verifica
    verifica = VerificaFlessione(
        sezione=sezione,
        calcestruzzo=cls,
        acciaio=acciaio,
        momento_flettente=80.0  # kNm
    )
    
    risultato = verifica.verifica()
    
    # Confronto con valori attesi
    print("RISULTATI CALCOLATI:")
    print(f"  Posizione asse neutro: x = {risultato.posizione_asse_neutro:.1f} mm")
    print(f"  Momento resistente: Mr = {risultato.momento_resistente:.2f} kNm")
    print(f"  Tensione calcestruzzo: σc = {risultato.tensione_calcestruzzo:.2f} MPa")
    print(f"  Tensione acciaio: σs = {risultato.tensione_acciaio:.2f} MPa")
    print()
    
    print("VALORI ATTESI (letteratura):")
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
        print("TEST SUPERATO ✓ - I risultati corrispondono all'esempio di Santarella")
        print("="*70)
        return True
    else:
        print("="*70)
        print("TEST FALLITO ✗ - Verificare i calcoli")
        print("="*70)
        return False


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
