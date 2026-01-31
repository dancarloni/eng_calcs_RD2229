"""
GUI Calcolo Calcestruzzo - Teoria Santarella (RD 2229/1939)

Interfaccia grafica per calcolare resistenze e tensioni ammissibili
del calcestruzzo secondo le formule storiche di Santarella.
"""

import sys
from pathlib import Path

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from verifiche_dm1939.core.dati_storici_rd2229 import (
    TABELLA_II_CALCESTRUZZO,
    CarichUnitariSicurezza,
    modulo_elasticita_calcestruzzo_kgcm2,
    interpola_resistenza_calcestruzzo,
)
from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.core.conversioni_unita import kgcm2_to_mpa, mpa_to_kgcm2


def limpa_schermo():
    """Pulisce lo schermo."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def mostra_intestazione():
    """Mostra intestazione."""
    print("\n" + "="*90)
    print("CALCOLO CALCESTRUZZO - TEORIA SANTARELLA (RD 2229/1939)")
    print("Formula modulo elastico: Ec = 550000 * sigma_c / (sigma_c + 200)")
    print("="*90)


def mostra_tabella_riferimento():
    """Mostra tabella di riferimento resistenze."""
    print("\n" + "-"*90)
    print("TABELLA II - RESISTENZE DI COMPRESSIONE DISPONIBILI [Kg/cm2]")
    print("-"*90)
    print(f"{'A/C':<10} {'Normale':<15} {'Alta Res.':<15} {'Alluminoso':<15}")
    print("-"*90)
    
    ac_disponibili = set()
    for (ac, tipo), valore in TABELLA_II_CALCESTRUZZO.items():
        if tipo == "normale":
            ac_disponibili.add(ac)
    
    for ac_nom in sorted(ac_disponibili, key=lambda x: float(x.replace(',', '.'))):
        sigma_norm = TABELLA_II_CALCESTRUZZO.get((ac_nom, "normale"), "-")
        sigma_alt = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alta_resistenza"), "-")
        sigma_allum = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alluminoso"), "-")
        print(f"{ac_nom:<10} {str(sigma_norm):<15} {str(sigma_alt):<15} {str(sigma_allum):<15}")
    
    print("-"*90)


def mostra_carichi_unitari_riferimento():
    """Mostra carichi unitari di riferimento."""
    print("\n" + "-"*90)
    print("CARICHI UNITARI DI SICUREZZA - RD 2229/1939")
    print("-"*90)
    print("\nCOMPRESSIONE:")
    print(f"  Sezioni semplicemente compresse:")
    print(f"    - Cemento normale:        {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_NORM} Kg/cm2")
    print(f"    - Cemento alta resistenza: {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_ALT} Kg/cm2")
    print(f"  Sezioni inflesse:")
    print(f"    - Cemento normale:        {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_NORM} Kg/cm2")
    print(f"    - Cemento alta resistenza: {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_ALT} Kg/cm2")
    
    print("\nTAGLIO:")
    print(f"  Cemento normale:        {CarichUnitariSicurezza.TAU_TAGLIO_NORMALE} Kg/cm2")
    print(f"  Cemento alta resistenza: {CarichUnitariSicurezza.TAU_TAGLIO_ALTA_RESISTENZA} Kg/cm2")
    print(f"  Cemento alluminoso:      {CarichUnitariSicurezza.TAU_TAGLIO_ALLUMINOSO} Kg/cm2")
    print("-"*90)


def menu_principale():
    """Menu principale."""
    while True:
        mostra_intestazione()
        print("\nMENU PRINCIPALE:")
        print("  1. Calcolo da resistenza nota (Kg/cm2)")
        print("  2. Calcolo da rapporto A/C e tipo cemento")
        print("  3. Calcolo con interpolazione rapporto A/C")
        print("  4. Visualizza Tabella II completa")
        print("  5. Visualizza Carichi Unitari")
        print("  6. Confronto calcestruzzi")
        print("  0. Esci")
        print()
        
        scelta = input("Scegli un'opzione: ").strip()
        
        if scelta == "1":
            calcolo_da_resistenza()
        elif scelta == "2":
            calcolo_da_rapporto_ac()
        elif scelta == "3":
            calcolo_con_interpolazione()
        elif scelta == "4":
            mostra_tabella_riferimento()
        elif scelta == "5":
            mostra_carichi_unitari_riferimento()
        elif scelta == "6":
            confronto_calcestruzzi()
        elif scelta == "0":
            print("\nArrivederci!")
            break
        else:
            print("\nScelta non valida. Riprova.")
        
        if scelta != "0":
            print("\nPremere INVIO per continuare...", end="")
            input()


def calcolo_da_resistenza():
    """Calcolo calcestruzzo da resistenza nota."""
    print("\n" + "="*90)
    print("CALCOLO CALCESTRUZZO DA RESISTENZA NOTA")
    print("="*90)
    
    print("\nRESISTENZE COMUNI (Kg/cm2):")
    print("  140, 180, 200, 240, 280, 330, 380, 400, 450, 500")
    print("  (o inserisci un valore personalizzato)")
    
    try:
        sigma_kgcm2 = float(input("\nInserisci resistenza compressione [Kg/cm2]: ").strip())
        
        print("\nTIPO CEMENTO:")
        print("  1. Normale")
        print("  2. Alta resistenza")
        print("  3. Alluminoso")
        tipo_scelta = input("Scegli (1-3) [1]: ").strip() or "1"
        
        tipo_map = {"1": "normale", "2": "alta_resistenza", "3": "alluminoso"}
        tipo_cemento = tipo_map.get(tipo_scelta, "normale")
        
        rapporto_ac_str = input("Rapporto A/C (opzionale, es. 0.50) [auto]: ").strip()
        rapporto_ac = float(rapporto_ac_str) if rapporto_ac_str else None
        
        # Crea calcestruzzo con teoria Santarella
        cls = Calcestruzzo.da_tabella_storica(sigma_kgcm2, tipo_cemento, rapporto_ac)
        
        # Mostra risultati
        mostra_risultati_calcestruzzo(cls, sigma_kgcm2, tipo_cemento, rapporto_ac)
        
    except ValueError as e:
        print(f"\nErrore: valore non valido - {e}")
    except Exception as e:
        print(f"\nErrore durante il calcolo: {e}")


def calcolo_da_rapporto_ac():
    """Calcolo calcestruzzo da rapporto A/C tabellare."""
    print("\n" + "="*90)
    print("CALCOLO CALCESTRUZZO DA RAPPORTO A/C TABELLARE")
    print("="*90)
    
    mostra_tabella_riferimento()
    
    try:
        print("\nRAPPORTI A/C DISPONIBILI:")
        print("  0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00")
        
        rapporto_str = input("\nInserisci rapporto A/C (es. 0.50): ").strip()
        rapporto_ac = float(rapporto_str)
        
        print("\nTIPO CEMENTO:")
        print("  1. Normale")
        print("  2. Alta resistenza")
        print("  3. Alluminoso")
        tipo_scelta = input("Scegli (1-3) [1]: ").strip() or "1"
        
        tipo_map = {"1": "normale", "2": "alta_resistenza", "3": "alluminoso"}
        tipo_cemento = tipo_map.get(tipo_scelta, "normale")
        
        # Cerca resistenza in tabella
        chiave = (f"{rapporto_ac:.2f}".replace('.', ','), tipo_cemento)
        sigma_kgcm2 = TABELLA_II_CALCESTRUZZO.get(chiave)
        
        if sigma_kgcm2 is None:
            print(f"\nRapporto A/C {rapporto_ac} non trovato in tabella.")
            print("Usa l'opzione 3 per interpolazione.")
            return
        
        # Crea calcestruzzo
        cls = Calcestruzzo.da_tabella_storica(sigma_kgcm2, tipo_cemento, rapporto_ac)
        
        # Mostra risultati
        mostra_risultati_calcestruzzo(cls, sigma_kgcm2, tipo_cemento, rapporto_ac)
        
    except ValueError as e:
        print(f"\nErrore: valore non valido - {e}")
    except Exception as e:
        print(f"\nErrore durante il calcolo: {e}")


def calcolo_con_interpolazione():
    """Calcolo con interpolazione per rapporti A/C intermedi."""
    print("\n" + "="*90)
    print("CALCOLO CON INTERPOLAZIONE RAPPORTO A/C")
    print("="*90)
    
    print("\nQuesta opzione permette di calcolare valori per rapporti A/C non tabellari")
    print("usando interpolazione lineare tra i valori della Tabella II.")
    
    try:
        rapporto_str = input("\nInserisci rapporto A/C (es. 0.55, 0.75): ").strip()
        rapporto_ac = float(rapporto_str)
        
        print("\nTIPO CEMENTO:")
        print("  1. Normale")
        print("  2. Alta resistenza")
        print("  3. Alluminoso")
        tipo_scelta = input("Scegli (1-3) [1]: ").strip() or "1"
        
        tipo_map = {"1": "normale", "2": "alta_resistenza", "3": "alluminoso"}
        tipo_cemento = tipo_map.get(tipo_scelta, "normale")
        
        # Interpola resistenza
        sigma_kgcm2 = interpola_resistenza_calcestruzzo(rapporto_ac, tipo_cemento)
        
        if sigma_kgcm2 is None:
            print(f"\nRapporto A/C {rapporto_ac} fuori dal range della tabella (0.40-1.00).")
            return
        
        print(f"\nResistenza interpolata: {sigma_kgcm2:.1f} Kg/cm2")
        
        # Crea calcestruzzo
        cls = Calcestruzzo.da_tabella_storica(sigma_kgcm2, tipo_cemento, rapporto_ac)
        
        # Mostra risultati
        mostra_risultati_calcestruzzo(cls, sigma_kgcm2, tipo_cemento, rapporto_ac, interpolato=True)
        
    except ValueError as e:
        print(f"\nErrore: valore non valido - {e}")
    except Exception as e:
        print(f"\nErrore durante il calcolo: {e}")


def mostra_risultati_calcestruzzo(cls, sigma_input_kgcm2, tipo_cemento, rapporto_ac=None, interpolato=False):
    """Mostra i risultati del calcolo del calcestruzzo."""
    print("\n" + "="*90)
    print("RISULTATI CALCOLO CALCESTRUZZO - TEORIA SANTARELLA")
    print("="*90)
    
    # Dati di input
    print("\nDATI DI INPUT:")
    print(f"  Resistenza compressione: {sigma_input_kgcm2:.1f} Kg/cm2" + (" (interpolato)" if interpolato else ""))
    print(f"  Tipo cemento: {tipo_cemento.replace('_', ' ').title()}")
    if rapporto_ac:
        print(f"  Rapporto A/C: {rapporto_ac:.2f}")
    
    # Resistenza caratteristica
    print("\nRESISTENZA CARATTERISTICA:")
    print(f"  Rck = {cls.resistenza_caratteristica:.2f} MPa")
    print(f"      = {mpa_to_kgcm2(cls.resistenza_caratteristica):.1f} Kg/cm2")
    
    # Tensioni ammissibili
    print("\nTENSIONI AMMISSIBILI:")
    print(f"  Compressione (sigma_c,amm):")
    print(f"    = {cls.tensione_ammissibile_compressione:.3f} MPa")
    print(f"    = {mpa_to_kgcm2(cls.tensione_ammissibile_compressione):.1f} Kg/cm2")
    
    print(f"  Taglio (tau_c,amm):")
    print(f"    = {cls.tensione_ammissibile_taglio:.3f} MPa")
    print(f"    = {mpa_to_kgcm2(cls.tensione_ammissibile_taglio):.1f} Kg/cm2")
    
    # Modulo elastico (Formula Santarella)
    sigma_c_kgcm2 = mpa_to_kgcm2(cls.resistenza_caratteristica)
    ec_santarella_kgcm2 = modulo_elasticita_calcestruzzo_kgcm2(sigma_c_kgcm2)
    
    print("\nMODULO ELASTICO (Formula Santarella):")
    print(f"  Ec = 550000 * sigma_c / (sigma_c + 200)")
    print(f"     = 550000 * {sigma_c_kgcm2:.1f} / ({sigma_c_kgcm2:.1f} + 200)")
    print(f"     = {ec_santarella_kgcm2:.0f} Kg/cm2")
    print(f"     = {cls.modulo_elastico:.0f} MPa")
    
    # Coefficiente di omogeneizzazione
    print("\nCOEFFICIENTE DI OMOGENEIZZAZIONE:")
    print(f"  n = Es / Ec")
    print(f"    = 200000 MPa / {cls.modulo_elastico:.0f} MPa")
    print(f"    = {cls.coefficiente_omogeneizzazione:.2f}")
    
    # Note tecniche
    print("\nNOTE TECNICHE:")
    print(f"  - Es (acciaio) = 200000 MPa = 2000000 Kg/cm2 (costante storica)")
    print(f"  - Carichi unitari secondo RD 2229/1939 pag. 14-15")
    print(f"  - Formula Santarella da Prontuario anni '30-'70")
    
    print("="*90)


def confronto_calcestruzzi():
    """Confronta diversi calcestruzzi."""
    print("\n" + "="*90)
    print("CONFRONTO CALCESTRUZZI")
    print("="*90)
    
    print("\nQuesta opzione calcola e confronta diversi calcestruzzi.")
    print("Inserisci le resistenze da confrontare (vuoto per terminare):")
    
    calcestruzzi = []
    
    while True:
        try:
            sigma_str = input(f"\nResistenza {len(calcestruzzi)+1} [Kg/cm2] (invio per terminare): ").strip()
            if not sigma_str:
                break
            
            sigma_kgcm2 = float(sigma_str)
            
            print("  Tipo cemento (1=Normale, 2=Alta res., 3=Alluminoso) [1]: ", end="")
            tipo_scelta = input().strip() or "1"
            tipo_map = {"1": "normale", "2": "alta_resistenza", "3": "alluminoso"}
            tipo_cemento = tipo_map.get(tipo_scelta, "normale")
            
            cls = Calcestruzzo.da_tabella_storica(sigma_kgcm2, tipo_cemento)
            calcestruzzi.append((sigma_kgcm2, tipo_cemento, cls))
            
        except ValueError:
            print("  Valore non valido, riprova.")
    
    if len(calcestruzzi) < 2:
        print("\nServono almeno 2 calcestruzzi per il confronto.")
        return
    
    # Tabella comparativa
    print("\n" + "="*90)
    print("TABELLA COMPARATIVA")
    print("="*90)
    print(f"{'Sigma [Kg/cm2]':<18} {'Tipo':<15} {'Rck [MPa]':<12} {'Ec [MPa]':<12} {'n':<8} {'sigma_amm [MPa]':<18}")
    print("-"*90)
    
    for sigma_kgcm2, tipo, cls in calcestruzzi:
        tipo_short = tipo.replace('alta_resistenza', 'Alta res.').replace('normale', 'Normale').replace('alluminoso', 'Allum.')
        print(f"{sigma_kgcm2:<18.1f} {tipo_short:<15} {cls.resistenza_caratteristica:<12.2f} "
              f"{cls.modulo_elastico:<12.0f} {cls.coefficiente_omogeneizzazione:<8.2f} "
              f"{cls.tensione_ammissibile_compressione:<18.3f}")
    
    print("="*90)
    
    # Analisi comparativa
    print("\nANALISI COMPARATIVA:")
    
    max_rck = max(calcestruzzi, key=lambda x: x[2].resistenza_caratteristica)
    min_rck = min(calcestruzzi, key=lambda x: x[2].resistenza_caratteristica)
    
    print(f"  Massima Rck: {max_rck[2].resistenza_caratteristica:.2f} MPa "
          f"(sigma = {max_rck[0]:.0f} Kg/cm2, {max_rck[1]})")
    print(f"  Minima Rck:  {min_rck[2].resistenza_caratteristica:.2f} MPa "
          f"(sigma = {min_rck[0]:.0f} Kg/cm2, {min_rck[1]})")
    
    max_ec = max(calcestruzzi, key=lambda x: x[2].modulo_elastico)
    min_ec = min(calcestruzzi, key=lambda x: x[2].modulo_elastico)
    
    print(f"  Massimo Ec:  {max_ec[2].modulo_elastico:.0f} MPa "
          f"(sigma = {max_ec[0]:.0f} Kg/cm2)")
    print(f"  Minimo Ec:   {min_ec[2].modulo_elastico:.0f} MPa "
          f"(sigma = {min_ec[0]:.0f} Kg/cm2)")
    
    print("\nNOTE:")
    print("  - Il modulo elastico aumenta con la resistenza (formula Santarella)")
    print("  - Il coefficiente n diminuisce all'aumentare di Ec")
    print("  - Le tensioni ammissibili seguono i carichi unitari RD 2229/1939")


if __name__ == "__main__":
    try:
        menu_principale()
    except KeyboardInterrupt:
        print("\n\nOperazione annullata dall'utente.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nErrore inaspettato: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
