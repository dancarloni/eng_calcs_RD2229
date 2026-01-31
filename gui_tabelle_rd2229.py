"""
GUI Interattiva - Tabelle Storiche RD 2229/1939 Santarella

Interfaccia interattiva per consultare e usare le tabelle storiche
con menu principale e visualizzazione dati.
"""

import sys
from pathlib import Path

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from verifiche_dm1939.core.dati_storici_rd2229 import (
    TABELLA_II_CALCESTRUZZO,
    CarichUnitariSicurezza,
)
from verifiche_dm1939.core.tabella_malta import (
    TABELLA_III_MALTA,
    genera_tabella_malta_testo,
    get_malta_da_rapporto,
    interpola_dosatura_malta,
    calcola_malta_per_volume,
)
from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.materials.acciaio import Acciaio
from verifiche_dm1939.core.conversioni_unita import kgcm2_to_mpa, mpa_to_kgcm2


def limpa_schermo():
    """Pulisce lo schermo."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def mostra_intestazione():
    """Mostra l'intestazione della GUI."""
    print("\n" + "="*80)
    print("VERIFICHE STRUTTURALI RD 2229/1939 - PRONTUARIO SANTARELLA")
    print("Interfaccia Interattiva - Tabelle Storiche e Calcoli")
    print("="*80)


def menu_principale():
    """Menu principale."""
    while True:
        mostra_intestazione()
        print("\nMENU PRINCIPALE:")
        print("  1. Tabella II - Calcestruzzo (Rapporti A/C e Resistenze)")
        print("  2. Tabella III - Malta (Quantitativi Cemento e Sabbia)")
        print("  3. Carichi Unitari di Sicurezza")
        print("  4. Calcoli Materiali Storici")
        print("  5. Convertitore Unita (Kg/cm2 <-> MPa)")
        print("  6. Esporta Tabelle HTML")
        print("  0. Esci")
        print()
        
        scelta = input("Scegli un'opzione: ").strip()
        
        if scelta == "1":
            mostra_tabella_ii()
        elif scelta == "2":
            mostra_tabella_iii()
        elif scelta == "3":
            mostra_carichi_unitari()
        elif scelta == "4":
            mostra_calcoli_materiali()
        elif scelta == "5":
            mostra_convertitore()
        elif scelta == "6":
            esporta_html()
        elif scelta == "0":
            print("\nArrivederci!")
            break
        else:
            print("\nScelta non valida. Riprova.")
        
        print("\nPremere INVIO per continuare...", end="")
        input()


def mostra_tabella_ii():
    """Visualizza Tabella II - Calcestruzzo."""
    print("\n" + "="*80)
    print("TABELLA II - RAPPORTI A/C E RESISTENZE DI COMPRESSIONE")
    print("Fonte: RD 2229/1939 (pag. 9)")
    print("="*80 + "\n")
    
    print(f"{'A/C':<8} {'Cemento Normale':<20} {'Alta Resistenza':<20} {'Alluminoso':<15}")
    print(f"{'':8} {'[Kg/cm2]':<20} {'[Kg/cm2]':<20} {'[Kg/cm2]':<15}")
    print("-" * 80)
    
    ac_disponibili = set()
    for (ac, tipo), valore in TABELLA_II_CALCESTRUZZO.items():
        if tipo == "normale":
            ac_disponibili.add(ac)
    
    for ac_nom in sorted(ac_disponibili, key=lambda x: float(x.replace(',', '.'))):
        sigma_norm = TABELLA_II_CALCESTRUZZO.get((ac_nom, "normale"), "-")
        sigma_alt = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alta_resistenza"), "-")
        sigma_allum = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alluminoso"), "-")
        
        print(f"{ac_nom:<8} {str(sigma_norm):<20} {str(sigma_alt):<20} {str(sigma_allum):<15}")
    
    print("\n" + "="*80)


def mostra_tabella_iii():
    """Visualizza Tabella III - Malta."""
    print()
    print(genera_tabella_malta_testo())
    
    # Menu sottomenu Tabella III
    while True:
        print("\nOPZIONI TABELLA III:")
        print("  1. Consultazione rapporto specifico")
        print("  2. Interpolazione rapporto intermedio")
        print("  3. Calcolo quantitativi per volume")
        print("  0. Torna indietro")
        print()
        
        scelta = input("Scegli un'opzione: ").strip()
        
        if scelta == "1":
            consultazione_malta()
        elif scelta == "2":
            interpolazione_malta()
        elif scelta == "3":
            calcolo_volume_malta()
        elif scelta == "0":
            break
        else:
            print("\nScelta non valida.")
        
        print("\nPremere INVIO per continuare...", end="")
        input()


def consultazione_malta():
    """Consultazione rapporto malta."""
    print("\n" + "-"*80)
    print("CONSULTAZIONE RAPPORTO MALTA")
    print("-"*80)
    print("\nRapporti disponibili: 1:1 | 1:1.40 | 1:1.85 | 1:2.30 | 1:2.70 | 1:3.70")
    rapporto = input("\nInserisci rapporto A/C (es. 1:1.85): ").strip()
    
    dosatura = get_malta_da_rapporto(rapporto)
    if dosatura:
        print("\nRISULTATI:")
        print(f"  Rapporto A/C: {dosatura.rapporto_ac}")
        print(f"  Cemento: {dosatura.cemento_kg:.0f} kg/m3")
        print(f"  Sabbia: {dosatura.sabbia_kg:.0f} kg/m3")
        print(f"  Peso specifico apparente: {dosatura.peso_specifico_apparente:.0f} kg/m3")
    else:
        print(f"\nRapporto '{rapporto}' non trovato in tabella.")


def interpolazione_malta():
    """Interpolazione malta."""
    print("\n" + "-"*80)
    print("INTERPOLAZIONE RAPPORTO MALTA")
    print("-"*80)
    
    try:
        rapporto = float(input("\nInserisci rapporto A/C numerico (es. 1.5, 2.0, 2.5): ").strip())
        dosatura = interpola_dosatura_malta(rapporto)
        
        if dosatura:
            print("\nRISULTATI INTERPOLATI:")
            print(f"  Rapporto A/C: 1:{rapporto}")
            print(f"  Cemento: {dosatura['cemento_kg']:.0f} kg/m3")
            print(f"  Sabbia: {dosatura['sabbia_kg']:.0f} kg/m3")
            print(f"  Peso specifico apparente: {dosatura['peso_specifico_apparente']:.0f} kg/m3")
        else:
            print("\nRapporto fuori range.")
    except ValueError:
        print("\nValore non valido.")


def calcolo_volume_malta():
    """Calcolo quantitativi per volume."""
    print("\n" + "-"*80)
    print("CALCOLO QUANTITATIVI MALTA PER VOLUME")
    print("-"*80)
    
    try:
        rapporto = float(input("\nInserisci rapporto A/C (es. 2.30): ").strip())
        volume = float(input("Inserisci volume in m3 (es. 2.0): ").strip())
        
        quant = calcola_malta_per_volume(rapporto, volume)
        if quant:
            print("\nQUANTITATIVI NECESSARI:")
            print(f"  Volume: {volume:.2f} m3")
            print(f"  Cemento: {quant['cemento_kg']:.0f} kg")
            print(f"    -> Sacchi 50kg: ca. {quant['cemento_kg']/50:.0f} sacchi")
            print(f"  Sabbia: {quant['sabbia_kg']:.0f} kg")
            print(f"  Peso totale malta: {quant['peso_totale_malta']:.0f} kg")
    except ValueError:
        print("\nValori non validi.")


def mostra_carichi_unitari():
    """Visualizza carichi unitari di sicurezza."""
    print("\n" + "="*80)
    print("CARICHI UNITARI DI SICUREZZA")
    print("Fonte: RD 2229/1939 (pag. 14-15)")
    print("="*80)
    
    print("\nCOMPRESSIONE NEL CALCESTRUZZO [Kg/cm2]:")
    print(f"  Sezioni semplicemente compresse (normale): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_NORM}")
    print(f"  Sezioni semplicemente compresse (alta res.): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_ALT}")
    print(f"  Sezioni inflesse (normale): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_NORM}")
    print(f"  Sezioni inflesse (alta res.): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_ALT}")
    
    print("\nTAGLIO NEL CALCESTRUZZO [Kg/cm2]:")
    print(f"  Cemento normale: {CarichUnitariSicurezza.TAU_TAGLIO_NORMALE}")
    print(f"  Cemento alta resistenza: {CarichUnitariSicurezza.TAU_TAGLIO_ALTA_RESISTENZA}")
    print(f"  Cemento alluminoso: {CarichUnitariSicurezza.TAU_TAGLIO_ALLUMINOSO}")
    
    print("\nACCIAI [Kg/cm2]:")
    print(f"  Acciaio dolce (FeB32k): max = {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_DOLCE_NORMAL}")
    print(f"  Acciaio semiriduro (FeB38k): max = {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_SEMI}")
    print(f"  Acciaio duro (FeB44k): max = {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_DURO_NORMAL}")
    
    print("\n" + "="*80)


def mostra_calcoli_materiali():
    """Calcoli materiali da tabelle storiche."""
    print("\n" + "="*80)
    print("CALCOLI MATERIALI STORICI")
    print("="*80)
    
    print("\nSCEGLI MATERIALE:")
    print("  1. Calcestruzzo da tabella storica")
    print("  2. Acciaio da tabella storica")
    print("  0. Torna indietro")
    
    scelta = input("\nScegli: ").strip()
    
    if scelta == "1":
        calcola_calcestruzzo()
    elif scelta == "2":
        calcola_acciaio()


def calcola_calcestruzzo():
    """Calcolo calcestruzzo storico."""
    print("\n" + "-"*80)
    print("CALCESTRUZZO DA TABELLA STORICA")
    print("-"*80)
    
    print("\nRESISTENZE DISPONIBILI (Kg/cm2):")
    print("  280, 330, 380, 400, 500 (comuni)")
    
    try:
        sigma = float(input("\nInserisci resistenza in Kg/cm2: ").strip())
        tipo = input("Tipo cemento (normale/alta_resistenza/alluminoso) [normale]: ").strip() or "normale"
        ac = input("Rapporto A/C (opzionale, es. 0.50): ").strip()
        ac_val = float(ac) if ac else None
        
        cls_storico = Calcestruzzo.da_tabella_storica(sigma, tipo, ac_val)
        
        print("\nCALCESTRUZZO STORICO CALCOLATO:")
        print(f"  σc (input): {sigma:.0f} Kg/cm2 = {mpa_to_kgcm2(cls_storico.resistenza_caratteristica):.0f} Kg/cm2")
        print(f"  Rck: {cls_storico.resistenza_caratteristica:.2f} MPa")
        print(f"  σc,amm: {cls_storico.tensione_ammissibile_compressione:.2f} MPa ({mpa_to_kgcm2(cls_storico.tensione_ammissibile_compressione):.0f} Kg/cm2)")
        print(f"  τc,amm: {cls_storico.tensione_ammissibile_taglio:.3f} MPa ({mpa_to_kgcm2(cls_storico.tensione_ammissibile_taglio):.1f} Kg/cm2)")
        print(f"  Ec (formula Santarella): {cls_storico.modulo_elastico:.0f} MPa")
        print(f"  n (Es/Ec): {cls_storico.coefficiente_omogeneizzazione:.1f}")
    except ValueError:
        print("\nValori non validi.")


def calcola_acciaio():
    """Calcolo acciaio storico."""
    print("\n" + "-"*80)
    print("ACCIAIO DA TABELLA STORICA")
    print("-"*80)
    
    print("\nRESISTENZE DISPONIBILI (Kg/cm2):")
    print("  1400 (FeB32k - dolce)")
    print("  1800 (FeB38k - semiriduro)")
    print("  2000 (FeB44k - duro)")
    
    try:
        sigma = float(input("\nInserisci resistenza in Kg/cm2: ").strip())
        tipo = input("Tipo acciaio (dolce/semiriduro/duro) [dolce]: ").strip() or "dolce"
        
        acc_storico = Acciaio.da_tabella_storica(sigma, tipo)
        
        print("\nACCIAIO STORICO CALCOLATO:")
        print(f"  Tipo: {acc_storico.tipo}")
        print(f"  fyk: {acc_storico.tensione_snervamento:.0f} MPa ({mpa_to_kgcm2(acc_storico.tensione_snervamento):.0f} Kg/cm2)")
        print(f"  σs,amm: {acc_storico.tensione_ammissibile:.1f} MPa ({mpa_to_kgcm2(acc_storico.tensione_ammissibile):.0f} Kg/cm2)")
        print(f"  Aderenza: {'Migliorata' if acc_storico.aderenza_migliorata else 'Liscia'}")
    except ValueError:
        print("\nValori non validi.")


def mostra_convertitore():
    """Convertitore unita."""
    print("\n" + "="*80)
    print("CONVERTITORE UNITA")
    print("="*80)
    
    print("\n1. Kg/cm2 -> MPa")
    print("2. MPa -> Kg/cm2")
    
    scelta = input("\nScegli: ").strip()
    
    try:
        if scelta == "1":
            valore = float(input("Inserisci valore in Kg/cm2: ").strip())
            risultato = kgcm2_to_mpa(valore)
            print(f"\nRISULTATO: {valore:.1f} Kg/cm2 = {risultato:.4f} MPa")
        elif scelta == "2":
            valore = float(input("Inserisci valore in MPa: ").strip())
            risultato = mpa_to_kgcm2(valore)
            print(f"\nRISULTATO: {valore:.4f} MPa = {risultato:.1f} Kg/cm2")
    except ValueError:
        print("\nValore non valido.")


def esporta_html():
    """Esporta tabelle in HTML."""
    from verifiche_dm1939.core.tabella_malta import genera_tabella_malta_html
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Tabelle RD 2229/1939</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        h1, h2 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; background-color: white; }
        th, td { border: 1px solid #999; padding: 10px; text-align: left; }
        th { background-color: #4CAF50; color: white; font-weight: bold; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .fonte { font-size: 0.9em; color: #666; margin-top: 10px; }
        .contenitore { max-width: 1200px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="contenitore">
        <h1>Tabelle Storiche RD 2229/1939</h1>
        <p>Prontuario dell'Ing. Luigi Santarella (anni 1930-1970)</p>
        
        <h2>Tabella II - Rapporti A/C e Resistenze di Compressione</h2>
        <table border="1">
            <tr>
                <th>A/C</th>
                <th>Cemento Normale (Kg/cm2)</th>
                <th>Alta Resistenza (Kg/cm2)</th>
                <th>Alluminoso (Kg/cm2)</th>
            </tr>
"""
    
    ac_disponibili = set()
    for (ac, tipo), valore in TABELLA_II_CALCESTRUZZO.items():
        if tipo == "normale":
            ac_disponibili.add(ac)
    
    for ac_nom in sorted(ac_disponibili, key=lambda x: float(x.replace(',', '.'))):
        sigma_norm = TABELLA_II_CALCESTRUZZO.get((ac_nom, "normale"), "-")
        sigma_alt = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alta_resistenza"), "-")
        sigma_allum = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alluminoso"), "-")
        html_content += f"<tr><td>{ac_nom}</td><td>{sigma_norm}</td><td>{sigma_alt}</td><td>{sigma_allum}</td></tr>\n"
    
    html_content += """        </table>
        
        <h2>Tabella III - Quantitativi di Cemento e Sabbia per 1 m3 di Malta</h2>
"""
    html_content += genera_tabella_malta_html()
    html_content += """
    </div>
</body>
</html>
"""
    
    output_path = Path(__file__).parent / "tabelle_rd2229.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nFile esportato: {output_path}")


if __name__ == "__main__":
    try:
        menu_principale()
    except KeyboardInterrupt:
        print("\n\nOperazione annullata.")
        sys.exit(0)
