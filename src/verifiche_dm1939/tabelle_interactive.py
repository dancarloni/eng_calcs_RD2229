"""
Visualizzatore Tabelle Storiche RD 2229 - Interfaccia Interattiva.

Mostra le tabelle storiche Santarella in formato testo/HTML/Markdown.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from verifiche_dm1939.core.dati_storici_rd2229 import (
    TABELLA_II_CALCESTRUZZO,
    CarichUnitariSicurezza,
    RAPPORTI_AC_NOMINALI,
)
from verifiche_dm1939.core.tabella_malta import (
    TABELLA_III_MALTA,
    genera_tabella_malta_testo,
)


def mostra_menu_principale():
    """Mostra menu principale."""
    print("\n" + "="*80)
    print("VISUALIZZATORE TABELLE STORICHE RD 2229/1939")
    print("Prontuario dell'Ing. Luigi Santarella - Edizioni '30-'70")
    print("="*80)
    print()
    print("Tabelle Disponibili:")
    print("  1. Tabella II - Rapporti A/C e Resistenze Calcestruzzo")
    print("  2. Tabella III - Quantitativi Cemento e Sabbia per Malta")
    print("  3. Carichi Unitari di Sicurezza")
    print("  4. Esci")
    print()


def mostra_tabella_ii():
    """Mostra Tabella II - Calcestruzzo."""
    print("\n" + "="*80)
    print("TABELLA II - RAPPORTI A/C E RESISTENZE DI COMPRESSIONE")
    print("Fonte: RD 2229/1939 (pag. 9)")
    print("="*80)
    print()
    
    print(f"{'A/C':<8} {'Cemento Normale':<20} {'Alta Resistenza':<20} {'Alluminoso':<15}")
    print(f"{'':8} {'[Kg/cm2]':<20} {'[Kg/cm2]':<20} {'[Kg/cm2]':<15}")
    print("-" * 80)
    
    # Estrai solo i valori di A/C disponibili nel normale
    ac_disponibili = set()
    for (ac, tipo), valore in TABELLA_II_CALCESTRUZZO.items():
        if tipo == "normale":
            ac_disponibili.add(ac)
    
    for ac_nom in sorted(ac_disponibili, key=lambda x: float(x.replace(',', '.'))):
        sigma_norm = TABELLA_II_CALCESTRUZZO.get((ac_nom, "normale"), "-")
        sigma_alt = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alta_resistenza"), "-")
        sigma_allum = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alluminoso"), "-")
        
        sigma_norm_str = f"{sigma_norm}" if isinstance(sigma_norm, (int, float)) else sigma_norm
        sigma_alt_str = f"{sigma_alt}" if isinstance(sigma_alt, (int, float)) else sigma_alt
        sigma_allum_str = f"{sigma_allum}" if isinstance(sigma_allum, (int, float)) else sigma_allum
        
        print(
            f"{ac_nom:<8} {sigma_norm_str:<20} {sigma_alt_str:<20} {sigma_allum_str:<15}"
        )
    
    print()
    print("Interpretazione:")
    print("- A/C: Rapporto volumetrico cemento (1) su sabbia (C)")
    print("- Valori sono resistenze a compressione a 28 giorni in Kg/cm2")
    print("- Conversione: 1 MPa = 10.197 Kg/cm2")


def mostra_tabella_iii():
    """Mostra Tabella III - Malta."""
    print("\n" + genera_tabella_malta_testo())


def mostra_carichi_unitari():
    """Mostra Carichi Unitari di Sicurezza."""
    print("\n" + "="*80)
    print("CARICHI UNITARI DI SICUREZZA")
    print("Fonte: RD 2229/1939 (pag. 14-15)")
    print("="*80)
    print()
    
    print("COMPRESSIONE NEL CALCESTRUZZO [Kg/cm2]:")
    print(f"  Sezioni semplicemente compresse (normale): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_NORM}")
    print(f"  Sezioni semplicemente compresse (alta res.): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_ALT}")
    print(f"  Sezioni inflesse (normale): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_NORM}")
    print(f"  Sezioni inflesse (alta res.): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_ALT}")
    print()
    
    print("TAGLIO NEL CALCESTRUZZO [Kg/cm2]:")
    print(f"  Cemento normale: {CarichUnitariSicurezza.TAU_TAGLIO_NORMALE}")
    print(f"  Cemento alta resistenza: {CarichUnitariSicurezza.TAU_TAGLIO_ALTA_RESISTENZA}")
    print(f"  Cemento alluminoso: {CarichUnitariSicurezza.TAU_TAGLIO_ALLUMINOSO}")
    print()
    
    print("ACCIAI [Kg/cm2]:")
    print(f"  Acciaio dolce (FeB24k, FeB32k): max = {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_DOLCE_NORMAL}")
    print(f"  Acciaio semiriduro (FeB38k): max = {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_SEMI}")
    print(f"  Acciaio duro (FeB44k): max = {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_DURO_NORMAL}")
    print()
    
    print("NOTE:")
    print("- Valori ammissibili per verifiche alle tensioni ammissibili")
    print("- Coefficienti di sicurezza incorporati nei carichi unitari")
    print("- Applicabili a strutture progettate secondo DM 2229/1939")


def esporta_tabelle_html():
    """Esporta tutte le tabelle in HTML."""
    from verifiche_dm1939.core.tabella_malta import genera_tabella_malta_html
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Tabelle Storiche RD 2229/1939</title>
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
        <p>Regio Decreto Legge n. 2229 del 16 novembre 1939</p>
        <p>Prontuario dell'Ing. Luigi Santarella (edizioni 1930-1970)</p>
        
        <h2>Tabella II - Rapporti A/C e Resistenze di Compressione</h2>
        <table border="1">
            <tr>
                <th>A/C</th>
                <th>Cemento Normale (Kg/cm2)</th>
                <th>Alta Resistenza (Kg/cm2)</th>
                <th>Alluminoso (Kg/cm2)</th>
            </tr>
"""
    
    # Aggiungi Tabella II
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
        <div class="fonte">Fonte: RD 2229/1939 (pag. 9)</div>
        
        <h2>Tabella III - Quantitativi di Cemento e Sabbia per 1 m³ di Malta</h2>
"""
    
    html_content += genera_tabella_malta_html()
    
    html_content += """
        <div class="fonte">Fonte: RD 2229/1939 (pag. 6-7)</div>
        
        <h2>Carichi Unitari di Sicurezza</h2>
        <table>
            <tr><th>Elemento</th><th>Valore (Kg/cm2)</th></tr>
            <tr><td>Compressione cls (inflesso, normale)</td><td>40</td></tr>
            <tr><td>Compressione cls (inflesso, alta res.)</td><td>50</td></tr>
            <tr><td>Taglio cls (normale)</td><td>4</td></tr>
            <tr><td>Taglio cls (alta res.)</td><td>6</td></tr>
            <tr><td>Acciaio dolce (FeB32k)</td><td>1400</td></tr>
            <tr><td>Acciaio semiriduro (FeB38k)</td><td>1800</td></tr>
            <tr><td>Acciaio duro (FeB44k)</td><td>2000</td></tr>
        </table>
        <div class="fonte">Fonte: RD 2229/1939 (pag. 14-15)</div>
    </div>
</body>
</html>
"""
    
    # Scrivi file
    output_path = Path(__file__).parent.parent / "output" / "tabelle_rd2229.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nFile HTML esportato: {output_path}")


def main():
    """Loop principale."""
    while True:
        mostra_menu_principale()
        scelta = input("Scegli un'opzione (1-4): ").strip()
        
        if scelta == "1":
            mostra_tabella_ii()
        elif scelta == "2":
            mostra_tabella_iii()
        elif scelta == "3":
            mostra_carichi_unitari()
        elif scelta == "4":
            print("\nEsporta tabelle in HTML? (s/n): ", end="")
            if input().lower() == 's':
                esporta_tabelle_html()
            print("\nArrivederci!")
            break
        else:
            print("\nScelta non valida. Riprova.")
        
        print("\nPremere INVIO per continuare...", end="")
        input()


if __name__ == "__main__":
    main()
