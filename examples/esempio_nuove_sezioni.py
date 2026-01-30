"""
Esempio completo delle nuove sezioni con tutte le funzionalità.

Dimostra:
- Tutte le geometrie di sezione (rettangolare, T, I, L, U, cave, circolari)
- Calcolo proprietà geometriche complete
- Coefficiente omogeneizzazione auto/manuale
- Calcolo asse neutro con N e M
- Utility calcolo area ferro
- Rotazione 90 gradi
- Info tooltip
"""

import sys
sys.path.insert(0, 'src')

from verifiche_dm1939.materials import Calcestruzzo, Acciaio
from verifiche_dm1939.sections import (
    SezioneRettangolare,
    SezioneT,
    SezioneI,
    SezioneL,
    SezioneU,
    SezioneRettangolareCava,
    SezioneCircolare,
    SezioneCircolareCava
)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def stampa_separatore(titolo: str):
    """Stampa separatore decorativo."""
    print("\n" + "=" * 80)
    print(f"  {titolo}")
    print("=" * 80)


def disegna_sezione(sezione, titolo: str, ax):
    """Disegna una sezione con le sue armature."""
    # Contorno
    contorno = sezione.get_contorno()
    xs = [p[0] for p in contorno] + [contorno[0][0]]
    ys = [p[1] for p in contorno] + [contorno[0][1]]
    
    ax.plot(xs, ys, 'b-', linewidth=2)
    ax.fill(xs, ys, alpha=0.1, color='blue')
    
    # Proprietà geometriche
    prop = sezione.calcola_proprieta_geometriche()
    
    # Baricentro
    ax.plot(0, prop.y_baricentro, 'ro', markersize=8, label='Baricentro')
    
    # Armature inferiori
    for barra in sezione.barre_inferiori:
        circle = plt.Circle((barra.x_pos, barra.y_pos), barra.diametro/2,
                           color='red', fill=True, alpha=0.7)
        ax.add_patch(circle)
    
    # Armature superiori
    for barra in sezione.barre_superiori:
        circle = plt.Circle((barra.x_pos, barra.y_pos), barra.diametro/2,
                           color='green', fill=True, alpha=0.7)
        ax.add_patch(circle)
    
    # Asse neutro (se ci sono armature)
    if sezione.As > 0 and hasattr(sezione, 'posizione_asse_neutro'):
        try:
            x_an = sezione.posizione_asse_neutro()
            dim = sezione.get_dimensioni_principali()
            larghezza = dim.get('b', dim.get('bf', dim.get('D', 300)))
            ax.plot([-larghezza/2, larghezza/2], [x_an, x_an], 
                   'r--', linewidth=2, label=f'Asse neutro (x={x_an:.0f} mm)')
        except:
            pass
    
    ax.set_title(titolo, fontsize=10, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')


def main():
    """Funzione principale."""
    
    print("\n" + "=" * 80)
    print("  ESEMPIO COMPLETO NUOVE SEZIONI - DM 2229/1939")
    print("  Geometrie avanzate con proprietà complete")
    print("=" * 80)
    
    # Materiali standard DM 2229/1939
    cls = Calcestruzzo(resistenza_caratteristica=15.0)
    acc = Acciaio(tipo='FeB32k', tensione_snervamento=320.0)
    
    print(f"\nMateriali:")
    print(f"  Calcestruzzo: Rck={cls.resistenza_caratteristica} MPa, Ec={cls.modulo_elastico:.0f} MPa")
    print(f"  Acciaio: {acc.tipo}, Es={acc.modulo_elastico:.0f} MPa")
    print(f"  Coeff. omogeneizzazione n = {acc.modulo_elastico/cls.modulo_elastico:.2f}")
    
    # ========== 1. SEZIONE RETTANGOLARE ==========
    stampa_separatore("1. SEZIONE RETTANGOLARE (300x500 mm)")
    
    sez_rett = SezioneRettangolare(300, 500, cls, acc, copriferro=30)
    sez_rett.aggiungi_armatura_inferiore(20, 3)  # 3φ20 inferiore
    sez_rett.aggiungi_armatura_superiore(16, 2)  # 2φ16 superiore
    sez_rett.aggiungi_staffe(8, 150, 2)  # Staffe φ8/150
    
    prop = sez_rett.calcola_proprieta_geometriche()
    print(f"\nProprietà geometriche:")
    print(f"  Area: {prop.area:.0f} mm²")
    print(f"  Baricentro: y={prop.y_baricentro:.1f} mm")
    print(f"  Ix: {prop.momento_inerzia_x:.2e} mm⁴")
    print(f"  Iy: {prop.momento_inerzia_y:.2e} mm⁴")
    print(f"  Wx,sup: {prop.modulo_resistenza_sup:.2e} mm³")
    
    print(f"\nArmature:")
    print(f"  As (inf): {sez_rett.As:.0f} mm²")
    print(f"  As' (sup): {sez_rett.As_prime:.0f} mm²")
    print(f"  d: {sez_rett.d:.0f} mm")
    print(f"  d': {sez_rett.d_prime:.0f} mm")
    print(f"  ρ: {sez_rett.percentuale_armatura:.2f}%")
    
    # Calcolo asse neutro
    an = sez_rett.calcola_asse_neutro(M=50.0, N=-100.0)
    print(f"\nAsse neutro (M=50 kNm, N=-100 kN compressione):")
    print(f"  Posizione: x={an.posizione:.1f} mm")
    print(f"  Tipo rottura: {an.tipo_rottura}")
    print(f"  εc,sup: {an.epsilon_cls_sup:.5f}")
    print(f"  εs,inf: {an.epsilon_acciaio_inf:.5f}")
    
    # Calcolo area ferro necessaria
    As_nec = sez_rett.calcola_area_ferro_necessaria(M=80.0, N=0.0, posizione='inferiore')
    print(f"\nArea ferro necessaria per M=80 kNm:")
    print(f"  As,nec = {As_nec:.0f} mm² → {As_nec/314:.1f}φ20")
    
    # ========== 2. SEZIONE A T ==========
    stampa_separatore("2. SEZIONE A T (Trave con soletta)")
    
    sez_t = SezioneT(bw=200, h=600, bf=800, tf=120, 
                     calcestruzzo=cls, acciaio=acc)
    sez_t.aggiungi_armatura_inferiore(24, 4)
    sez_t.aggiungi_armatura_superiore(16, 2)
    
    prop_t = sez_t.calcola_proprieta_geometriche()
    print(f"\nProprietà geometriche:")
    print(f"  Area: {prop_t.area:.0f} mm²")
    print(f"  Baricentro: y={prop_t.y_baricentro:.1f} mm (da lembo sup)")
    print(f"  Ix: {prop_t.momento_inerzia_x:.2e} mm⁴")
    
    print(f"\nArmature: As={sez_t.As:.0f} mm², d={sez_t.d:.0f} mm")
    
    # ========== 3. SEZIONE A I (DOPPIA T) ==========
    stampa_separatore("3. SEZIONE A I (Doppia T)")
    
    sez_i = SezioneI(bw=150, h=500, 
                     bf_sup=400, tf_sup=100,
                     bf_inf=400, tf_inf=100,
                     calcestruzzo=cls, acciaio=acc)
    sez_i.aggiungi_armatura_inferiore(20, 3)
    sez_i.aggiungi_armatura_superiore(16, 2)
    
    prop_i = sez_i.calcola_proprieta_geometriche()
    print(f"\nProprietà: A={prop_i.area:.0f} mm², y_G={prop_i.y_baricentro:.1f} mm")
    print(f"Ix={prop_i.momento_inerzia_x:.2e} mm⁴")
    
    # ========== 4. SEZIONE A L ==========
    stampa_separatore("4. SEZIONE A L")
    
    sez_l = SezioneL(b1=300, t1=100, h=400, b2=300, t2=100,
                     calcestruzzo=cls, acciaio=acc)
    sez_l.aggiungi_armatura_inferiore(16, 2)
    
    prop_l = sez_l.calcola_proprieta_geometriche()
    print(f"\nProprietà: A={prop_l.area:.0f} mm², y_G={prop_l.y_baricentro:.1f} mm")
    
    # ========== 5. SEZIONE A U ==========
    stampa_separatore("5. SEZIONE A U (Canale)")
    
    sez_u = SezioneU(b=400, h=500, tf=80, tw=100,
                     calcestruzzo=cls, acciaio=acc)
    sez_u.aggiungi_armatura_inferiore(20, 3)
    
    prop_u = sez_u.calcola_proprieta_geometriche()
    print(f"\nProprietà: A={prop_u.area:.0f} mm², Ix={prop_u.momento_inerzia_x:.2e} mm⁴")
    
    # ========== 6. SEZIONE RETTANGOLARE CAVA ==========
    stampa_separatore("6. SEZIONE RETTANGOLARE CAVA (Scatolare)")
    
    sez_cava = SezioneRettangolareCava(b=400, h=500, tw=80, ts=80, ti=80,
                                       calcestruzzo=cls, acciaio=acc)
    sez_cava.aggiungi_armatura_inferiore(20, 2)
    sez_cava.aggiungi_armatura_superiore(16, 2)
    
    prop_cava = sez_cava.calcola_proprieta_geometriche()
    print(f"\nProprietà: A={prop_cava.area:.0f} mm², Ix={prop_cava.momento_inerzia_x:.2e} mm⁴")
    
    # ========== 7. SEZIONE CIRCOLARE ==========
    stampa_separatore("7. SEZIONE CIRCOLARE (Pilastro)")
    
    sez_circ = SezioneCircolare(D=400, calcestruzzo=cls, acciaio=acc)
    # Armatura distribuita sul perimetro
    for i in range(8):
        angolo = i * 45  # gradi
        r = 400/2 - 40  # raggio - copriferro
        x_pos = r * np.cos(np.radians(angolo))
        y_pos = 200 + r * np.sin(np.radians(angolo))
        sez_circ.barre_inferiori.append(
            type('Barra', (), {'diametro': 16, 'n_barre': 1, 'x_pos': x_pos, 'y_pos': y_pos, 
                              'area': 201})()
        )
    
    prop_circ = sez_circ.calcola_proprieta_geometriche()
    print(f"\nProprietà: A={prop_circ.area:.0f} mm², Ix=Iy={prop_circ.momento_inerzia_x:.2e} mm⁴")
    
    # ========== 8. SEZIONE CIRCOLARE CAVA ==========
    stampa_separatore("8. SEZIONE CIRCOLARE CAVA (Tubo)")
    
    sez_tubo = SezioneCircolareCava(De=400, Di=300, calcestruzzo=cls, acciaio=acc)
    sez_tubo.aggiungi_armatura_inferiore(16, 6)
    
    prop_tubo = sez_tubo.calcola_proprieta_geometriche()
    print(f"\nProprietà: A={prop_tubo.area:.0f} mm², Ix=Iy={prop_tubo.momento_inerzia_x:.2e} mm⁴")
    print(f"Spessore: {(sez_tubo.De - sez_tubo.Di)/2:.0f} mm")
    
    # ========== TEST ROTAZIONE 90° ==========
    stampa_separatore("TEST ROTAZIONE 90°")
    
    print("\nSezione rettangolare 300x500 - PRIMA della rotazione:")
    prop_orig = sez_rett.calcola_proprieta_geometriche()
    print(f"  Ix = {prop_orig.momento_inerzia_x:.2e} mm⁴")
    print(f"  Iy = {prop_orig.momento_inerzia_y:.2e} mm⁴")
    
    sez_rett.ruota_90_gradi()
    print("\nDOPO la rotazione:")
    prop_ruot = sez_rett.calcola_proprieta_geometriche()
    print(f"  Ix = {prop_ruot.momento_inerzia_x:.2e} mm⁴ (era Iy)")
    print(f"  Iy = {prop_ruot.momento_inerzia_y:.2e} mm⁴ (era Ix)")
    print(f"  Rotazione verificata: {'✓' if abs(prop_ruot.momento_inerzia_x - prop_orig.momento_inerzia_y) < 1 else '✗'}")
    
    sez_rett.ruota_90_gradi()  # Ripristina
    
    # ========== TEST COEFF. OMOGENEIZZAZIONE ==========
    stampa_separatore("TEST COEFFICIENTE OMOGENEIZZAZIONE")
    
    print(f"\nCalcolo AUTOMATICO (Es/Ec):")
    print(f"  n = {sez_rett.coeff_omogeneizzazione:.2f}")
    
    print(f"\nImpostazione MANUALE n=15:")
    sez_rett.coeff_omogeneizzazione = 15.0
    print(f"  n = {sez_rett.coeff_omogeneizzazione:.2f}")
    
    print(f"\nRipristino automatico:")
    sez_rett.coeff_omogeneizzazione = None
    print(f"  n = {sez_rett.coeff_omogeneizzazione:.2f}")
    
    # ========== GRAFICO TUTTE LE SEZIONI ==========
    print("\n\nGenerazione grafico comparativo...")
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle('Confronto Tutte le Geometrie di Sezione - DM 2229/1939', 
                 fontsize=14, fontweight='bold')
    
    sezioni = [
        (sez_rett, "Rettangolare\n300×500 mm", axes[0, 0]),
        (sez_t, "Sezione a T\nbf=800, h=600", axes[0, 1]),
        (sez_i, "Sezione a I\nh=500 mm", axes[0, 2]),
        (sez_l, "Sezione a L\n300×400 mm", axes[0, 3]),
        (sez_u, "Sezione a U\nb=400, h=500", axes[1, 0]),
        (sez_cava, "Rett. Cava\n400×500 mm", axes[1, 1]),
        (sez_circ, "Circolare\nD=400 mm", axes[1, 2]),
        (sez_tubo, "Tubo\nDe=400, Di=300", axes[1, 3]),
    ]
    
    for sez, titolo, ax in sezioni:
        disegna_sezione(sez, titolo, ax)
    
    plt.tight_layout()
    plt.savefig('examples/output/confronto_sezioni.png', dpi=150, bbox_inches='tight')
    print("Salvato: examples/output/confronto_sezioni.png")
    
    # ========== RIEPILOGO FINALE ==========
    stampa_separatore("RIEPILOGO FUNZIONALITÀ IMPLEMENTATE")
    
    print("\n✓ 8 geometrie di sezione:")
    print("  - Rettangolare, T, I, L, U, Rett. cava, Circolare, Circolare cava")
    print("\n✓ Proprietà geometriche complete:")
    print("  - Area, baricentro, momenti statici, momenti inerzia, moduli resistenza")
    print("\n✓ Coefficiente omogeneizzazione:")
    print("  - Automatico (n = Es/Ec) o manuale a scelta utente")
    print("\n✓ Calcolo asse neutro:")
    print("  - Considera forma sezione, geometria masse, armature, N e M")
    print("\n✓ Utility area ferro:")
    print("  - Calcolo automatico As necessaria per M e N dati")
    print("\n✓ Rotazione 90 gradi:")
    print("  - Tutte le sezioni ruotabili con aggiornamento proprietà")
    print("\n✓ Info contestuali:")
    print("  - Tooltip con informazioni su punti sezione")
    print("\n✓ Convenzioni DM 2229/1939:")
    print("  - As/As', d/d', M+/M-, N-/N+ secondo normativa")
    
    print("\n" + "=" * 80)
    print("  ESEMPIO COMPLETATO CON SUCCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    main()
