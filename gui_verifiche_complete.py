"""
GUI VERIFICHE STRUTTURALI COMPLETE - RD 2229/1939
Interfaccia completa per calcolo materiali storici Santarella e verifiche strutturali

Funzionalità:
- Calcolo materiali da tabelle storiche (calcestruzzo e acciaio Santarella)
- Libreria materiali salvati
- Definizione sezioni geometriche
- Verifiche: flessione, taglio, pressoflessione
- Generazione report
"""

import sys
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from verifiche_dm1939.core.dati_storici_rd2229 import (
    TABELLA_II_CALCESTRUZZO,
    CarichUnitariSicurezza,
    modulo_elasticita_calcestruzzo_kgcm2,
    interpola_resistenza_calcestruzzo,
)
from verifiche_dm1939.core.tabella_malta import (
    TABELLA_III_MALTA,
    get_malta_da_rapporto,
    calcola_malta_per_volume,
)
from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.materials.acciaio import Acciaio
from verifiche_dm1939.core.conversioni_unita import kgcm2_to_mpa, mpa_to_kgcm2

from verifiche_dm1939.sections.sezione_rettangolare import SezioneRettangolare
from verifiche_dm1939.sections.sezione_circolare import SezioneCircolare
from verifiche_dm1939.sections.sezione_t import SezioneT

from verifiche_dm1939.verifications.verifica_flessione import VerificaFlessione
from verifiche_dm1939.verifications.verifica_taglio import VerificaTaglio
from verifiche_dm1939.verifications.verifica_pressoflessione import VerificaPressoflessioneRetta


# ======================================================================================
# GESTIONE LIBRERIA MATERIALI
# ======================================================================================

@dataclass
class MaterialeSalvato:
    """Classe per salvare i materiali in libreria."""
    nome: str
    tipo: str  # 'calcestruzzo' o 'acciaio'
    parametri: Dict
    note: str = ""


class LibreriaMateriali:
    """Gestisce la libreria dei materiali salvati."""
    
    def __init__(self, file_path: str = "libreria_materiali.json"):
        self.file_path = Path(file_path)
        self.materiali: Dict[str, MaterialeSalvato] = {}
        self.carica()
    
    def carica(self):
        """Carica materiali dal file JSON."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for nome, mat_dict in data.items():
                        self.materiali[nome] = MaterialeSalvato(**mat_dict)
            except Exception as e:
                print(f"Errore caricamento libreria: {e}")
    
    def salva(self):
        """Salva materiali nel file JSON."""
        try:
            data = {nome: asdict(mat) for nome, mat in self.materiali.items()}
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Errore salvataggio libreria: {e}")
    
    def aggiungi_calcestruzzo(self, nome: str, cls: Calcestruzzo, note: str = ""):
        """Aggiunge calcestruzzo alla libreria."""
        parametri = {
            'resistenza_caratteristica': cls.resistenza_caratteristica,
            'modulo_elastico': cls.modulo_elastico,
            'tensione_ammissibile_compressione': cls.tensione_ammissibile_compressione,
            'tensione_ammissibile_taglio': cls.tensione_ammissibile_taglio,
            'coefficiente_omogeneizzazione': cls.coefficiente_omogeneizzazione,
        }
        self.materiali[nome] = MaterialeSalvato(nome, 'calcestruzzo', parametri, note)
        self.salva()
    
    def aggiungi_acciaio(self, nome: str, acc: Acciaio, note: str = ""):
        """Aggiunge acciaio alla libreria."""
        parametri = {
            'tipo': acc.tipo,
            'tensione_snervamento': acc.tensione_snervamento,
            'tensione_ammissibile': acc.tensione_ammissibile,
            'modulo_elastico': acc.modulo_elastico,
            'aderenza_migliorata': acc.aderenza_migliorata,
        }
        self.materiali[nome] = MaterialeSalvato(nome, 'acciaio', parametri, note)
        self.salva()
    
    def rimuovi(self, nome: str):
        """Rimuove materiale dalla libreria."""
        if nome in self.materiali:
            del self.materiali[nome]
            self.salva()
    
    def elenca_calcestruzzi(self) -> List[str]:
        """Elenca i calcestruzzi salvati."""
        return [nome for nome, mat in self.materiali.items() if mat.tipo == 'calcestruzzo']
    
    def elenca_acciai(self) -> List[str]:
        """Elenca gli acciai salvati."""
        return [nome for nome, mat in self.materiali.items() if mat.tipo == 'acciaio']
    
    def recupera_calcestruzzo(self, nome: str) -> Optional[Calcestruzzo]:
        """Recupera un calcestruzzo dalla libreria."""
        if nome in self.materiali and self.materiali[nome].tipo == 'calcestruzzo':
            p = self.materiali[nome].parametri
            return Calcestruzzo(
                resistenza_caratteristica=p['resistenza_caratteristica'],
                modulo_elastico=p['modulo_elastico'],
                tensione_ammissibile_compressione=p['tensione_ammissibile_compressione'],
                tensione_ammissibile_taglio=p['tensione_ammissibile_taglio'],
                coefficiente_omogeneizzazione=p['coefficiente_omogeneizzazione']
            )
        return None
    
    def recupera_acciaio(self, nome: str) -> Optional[Acciaio]:
        """Recupera un acciaio dalla libreria."""
        if nome in self.materiali and self.materiali[nome].tipo == 'acciaio':
            p = self.materiali[nome].parametri
            return Acciaio(
                tipo=p['tipo'],
                tensione_snervamento=p['tensione_snervamento'],
                tensione_ammissibile=p['tensione_ammissibile'],
                modulo_elastico=p['modulo_elastico'],
                aderenza_migliorata=p['aderenza_migliorata']
            )
        return None


# ======================================================================================
# INTERFACCIA GRAFICA
# ======================================================================================

class GUIVerificheComplete:
    """Interfaccia grafica principale."""
    
    def __init__(self):
        self.libreria = LibreriaMateriali()
        self.sezione_corrente = None
        self.calcestruzzo_corrente = None
        self.acciaio_corrente = None
    
    def limpa_schermo(self):
        """Pulisce lo schermo."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostra_intestazione(self):
        """Mostra intestazione."""
        print("\n" + "="*100)
        print("VERIFICHE STRUTTURALI RD 2229/1939 - PRONTUARIO SANTARELLA")
        print("Sistema completo: Materiali storici + Verifiche strutturali")
        print("="*100)
    
    def menu_principale(self):
        """Menu principale."""
        while True:
            self.mostra_intestazione()
            self.mostra_stato_corrente()
            
            print("\nMENU PRINCIPALE:")
            print("  1. MATERIALI - Calcolo e gestione materiali storici")
            print("  2. SEZIONI - Definizione geometrie")
            print("  3. VERIFICHE - Flessione, taglio, pressoflessione")
            print("  4. TABELLE STORICHE - Consultazione Tabelle II e III")
            print("  5. REPORT - Genera documentazione")
            print("  0. Esci")
            print()
            
            scelta = input("Scegli un'opzione: ").strip()
            
            if scelta == "1":
                self.menu_materiali()
            elif scelta == "2":
                self.menu_sezioni()
            elif scelta == "3":
                self.menu_verifiche()
            elif scelta == "4":
                self.menu_tabelle_storiche()
            elif scelta == "5":
                self.menu_report()
            elif scelta == "0":
                print("\nArrivederci!")
                break
            else:
                print("\nScelta non valida.")
                input("\nPremere INVIO per continuare...")
    
    def mostra_stato_corrente(self):
        """Mostra lo stato corrente del sistema."""
        print("\nSTATO CORRENTE:")
        
        # Materiali in libreria
        cls_salvati = self.libreria.elenca_calcestruzzi()
        acc_salvati = self.libreria.elenca_acciai()
        print(f"  Libreria: {len(cls_salvati)} calcestruzzi, {len(acc_salvati)} acciai")
        
        # Materiali selezionati
        if self.calcestruzzo_corrente:
            print(f"  Calcestruzzo attivo: Rck={self.calcestruzzo_corrente.resistenza_caratteristica:.1f} MPa")
        else:
            print("  Calcestruzzo attivo: Nessuno")
        
        if self.acciaio_corrente:
            print(f"  Acciaio attivo: {self.acciaio_corrente.tipo}, fyk={self.acciaio_corrente.tensione_snervamento:.0f} MPa")
        else:
            print("  Acciaio attivo: Nessuno")
        
        # Sezione
        if self.sezione_corrente:
            print(f"  Sezione attiva: {type(self.sezione_corrente).__name__}")
        else:
            print("  Sezione attiva: Nessuna")
    
    # ======================================================================================
    # MENU MATERIALI
    # ======================================================================================
    
    def menu_materiali(self):
        """Menu gestione materiali."""
        while True:
            self.mostra_intestazione()
            print("\nGESTIONE MATERIALI:")
            print("  1. Calcola CALCESTRUZZO da tabelle storiche Santarella")
            print("  2. Calcola ACCIAIO da tabelle storiche")
            print("  3. Visualizza LIBRERIA materiali salvati")
            print("  4. Seleziona materiale dalla libreria (per verifiche)")
            print("  5. Elimina materiale dalla libreria")
            print("  0. Torna al menu principale")
            print()
            
            scelta = input("Scegli: ").strip()
            
            if scelta == "1":
                self.calcola_calcestruzzo_storico()
            elif scelta == "2":
                self.calcola_acciaio_storico()
            elif scelta == "3":
                self.visualizza_libreria()
            elif scelta == "4":
                self.seleziona_materiali_da_libreria()
            elif scelta == "5":
                self.elimina_materiale()
            elif scelta == "0":
                break
            else:
                print("\nScelta non valida.")
            
            if scelta != "0":
                input("\nPremere INVIO per continuare...")
    
    def calcola_calcestruzzo_storico(self):
        """Calcola calcestruzzo da tabelle storiche."""
        print("\n" + "="*100)
        print("CALCOLO CALCESTRUZZO - TABELLE STORICHE SANTARELLA")
        print("="*100)
        
        print("\nMETODO:")
        print("  1. Da resistenza nota (Kg/cm2)")
        print("  2. Da rapporto A/C tabellare")
        print("  3. Con interpolazione rapporto A/C")
        
        metodo = input("\nScegli metodo: ").strip()
        
        try:
            if metodo == "1":
                sigma_kgcm2 = float(input("\nResistenza compressione [Kg/cm2]: ").strip())
            elif metodo == "2":
                print("\nRapporti A/C disponibili: 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00")
                rapporto_ac = float(input("Rapporto A/C: ").strip())
                print("\nTipo: 1=Normale, 2=Alta resistenza, 3=Alluminoso")
                tipo_scelta = input("Tipo: ").strip()
                tipo_map = {"1": "normale", "2": "alta_resistenza", "3": "alluminoso"}
                tipo_cemento = tipo_map.get(tipo_scelta, "normale")
                
                chiave = (f"{rapporto_ac:.2f}".replace('.', ','), tipo_cemento)
                sigma_kgcm2 = TABELLA_II_CALCESTRUZZO.get(chiave)
                if not sigma_kgcm2:
                    print("\nRapporto non trovato in tabella.")
                    return
            elif metodo == "3":
                rapporto_ac = float(input("\nRapporto A/C (es. 0.55): ").strip())
                print("Tipo: 1=Normale, 2=Alta resistenza, 3=Alluminoso")
                tipo_scelta = input("Tipo: ").strip()
                tipo_map = {"1": "normale", "2": "alta_resistenza", "3": "alluminoso"}
                tipo_cemento = tipo_map.get(tipo_scelta, "normale")
                
                sigma_kgcm2 = interpola_resistenza_calcestruzzo(rapporto_ac, tipo_cemento)
                if not sigma_kgcm2:
                    print("\nRapporto fuori range.")
                    return
                print(f"\nResistenza interpolata: {sigma_kgcm2:.1f} Kg/cm2")
            else:
                print("\nMetodo non valido.")
                return
            
            # Tipo cemento se non già definito
            if metodo == "1":
                print("\nTipo: 1=Normale, 2=Alta resistenza, 3=Alluminoso")
                tipo_scelta = input("Tipo [1]: ").strip() or "1"
                tipo_map = {"1": "normale", "2": "alta_resistenza", "3": "alluminoso"}
                tipo_cemento = tipo_map.get(tipo_scelta, "normale")
            
            # Crea calcestruzzo
            cls = Calcestruzzo.da_tabella_storica(sigma_kgcm2, tipo_cemento)
            
            # Mostra risultati
            print("\n" + "-"*100)
            print("RISULTATI:")
            print(f"  Resistenza input: {sigma_kgcm2:.1f} Kg/cm2")
            print(f"  Rck = {cls.resistenza_caratteristica:.2f} MPa ({mpa_to_kgcm2(cls.resistenza_caratteristica):.1f} Kg/cm2)")
            print(f"  sigma_c,amm = {cls.tensione_ammissibile_compressione:.3f} MPa ({mpa_to_kgcm2(cls.tensione_ammissibile_compressione):.1f} Kg/cm2)")
            print(f"  tau_c,amm = {cls.tensione_ammissibile_taglio:.3f} MPa ({mpa_to_kgcm2(cls.tensione_ammissibile_taglio):.1f} Kg/cm2)")
            print(f"  Ec (Santarella) = {cls.modulo_elastico:.0f} MPa")
            print(f"  n = {cls.coefficiente_omogeneizzazione:.2f}")
            print("-"*100)
            
            # Salva in libreria
            salva = input("\nSalvare in libreria? (s/n): ").strip().lower()
            if salva == 's':
                nome = input("Nome identificativo: ").strip()
                note = input("Note (opzionale): ").strip()
                self.libreria.aggiungi_calcestruzzo(nome, cls, note)
                print(f"\nCalcestruzzo '{nome}' salvato in libreria.")
                
                # Imposta come corrente
                self.calcestruzzo_corrente = cls
                print("Impostato come calcestruzzo attivo.")
        
        except ValueError as e:
            print(f"\nErrore: {e}")
    
    def calcola_acciaio_storico(self):
        """Calcola acciaio da tabelle storiche."""
        print("\n" + "="*100)
        print("CALCOLO ACCIAIO - TABELLE STORICHE RD 2229/1939")
        print("="*100)
        
        print("\nRESISTENZE STORICHE:")
        print("  1400 Kg/cm2 - FeB32k (acciaio dolce)")
        print("  1800 Kg/cm2 - FeB38k (acciaio semiriduro)")
        print("  2000 Kg/cm2 - FeB44k (acciaio duro)")
        
        try:
            sigma_kgcm2 = float(input("\nResistenza [Kg/cm2]: ").strip())
            
            print("\nTipo: 1=Dolce (FeB32k), 2=Semiriduro (FeB38k), 3=Duro (FeB44k)")
            tipo_scelta = input("Tipo [1]: ").strip() or "1"
            tipo_map = {"1": "dolce", "2": "semiriduro", "3": "duro"}
            tipo_acciaio = tipo_map.get(tipo_scelta, "dolce")
            
            # Crea acciaio
            acc = Acciaio.da_tabella_storica(sigma_kgcm2, tipo_acciaio)
            
            # Mostra risultati
            print("\n" + "-"*100)
            print("RISULTATI:")
            print(f"  Tipo: {acc.tipo}")
            print(f"  fyk = {acc.tensione_snervamento:.0f} MPa ({mpa_to_kgcm2(acc.tensione_snervamento):.0f} Kg/cm2)")
            print(f"  sigma_s,amm = {acc.tensione_ammissibile:.1f} MPa ({mpa_to_kgcm2(acc.tensione_ammissibile):.0f} Kg/cm2)")
            print(f"  Aderenza: {'Migliorata' if acc.aderenza_migliorata else 'Liscia'}")
            print("-"*100)
            
            # Salva in libreria
            salva = input("\nSalvare in libreria? (s/n): ").strip().lower()
            if salva == 's':
                nome = input("Nome identificativo: ").strip()
                note = input("Note (opzionale): ").strip()
                self.libreria.aggiungi_acciaio(nome, acc, note)
                print(f"\nAcciaio '{nome}' salvato in libreria.")
                
                # Imposta come corrente
                self.acciaio_corrente = acc
                print("Impostato come acciaio attivo.")
        
        except ValueError as e:
            print(f"\nErrore: {e}")
    
    def visualizza_libreria(self):
        """Visualizza la libreria materiali."""
        print("\n" + "="*100)
        print("LIBRERIA MATERIALI SALVATI")
        print("="*100)
        
        cls_salvati = self.libreria.elenca_calcestruzzi()
        acc_salvati = self.libreria.elenca_acciai()
        
        if cls_salvati:
            print("\nCALCESTRUZZI:")
            print(f"{'Nome':<20} {'Rck [MPa]':<12} {'Ec [MPa]':<12} {'n':<8} {'Note':<30}")
            print("-"*100)
            for nome in cls_salvati:
                mat = self.libreria.materiali[nome]
                p = mat.parametri
                print(f"{nome:<20} {p['resistenza_caratteristica']:<12.2f} "
                      f"{p['modulo_elastico']:<12.0f} {p['coefficiente_omogeneizzazione']:<8.2f} "
                      f"{mat.note:<30}")
        
        if acc_salvati:
            print("\nACCIAI:")
            print(f"{'Nome':<20} {'Tipo':<12} {'fyk [MPa]':<12} {'sigma_amm [MPa]':<18} {'Note':<30}")
            print("-"*100)
            for nome in acc_salvati:
                mat = self.libreria.materiali[nome]
                p = mat.parametri
                print(f"{nome:<20} {p['tipo']:<12} {p['tensione_snervamento']:<12.0f} "
                      f"{p['tensione_ammissibile']:<18.1f} {mat.note:<30}")
        
        if not cls_salvati and not acc_salvati:
            print("\nNessun materiale salvato in libreria.")
    
    def seleziona_materiali_da_libreria(self):
        """Seleziona materiali dalla libreria per le verifiche."""
        print("\n" + "="*100)
        print("SELEZIONE MATERIALI DA LIBRERIA")
        print("="*100)
        
        # Calcestruzzo
        cls_salvati = self.libreria.elenca_calcestruzzi()
        if cls_salvati:
            print("\nCALCESTRUZZI DISPONIBILI:")
            for i, nome in enumerate(cls_salvati, 1):
                mat = self.libreria.materiali[nome]
                p = mat.parametri
                print(f"  {i}. {nome} - Rck={p['resistenza_caratteristica']:.1f} MPa")
            
            scelta = input("\nSeleziona calcestruzzo (numero o 0 per saltare): ").strip()
            if scelta != "0":
                try:
                    idx = int(scelta) - 1
                    if 0 <= idx < len(cls_salvati):
                        nome_cls = cls_salvati[idx]
                        self.calcestruzzo_corrente = self.libreria.recupera_calcestruzzo(nome_cls)
                        print(f"Calcestruzzo '{nome_cls}' selezionato.")
                except ValueError:
                    print("Selezione non valida.")
        
        # Acciaio
        acc_salvati = self.libreria.elenca_acciai()
        if acc_salvati:
            print("\nACCIAI DISPONIBILI:")
            for i, nome in enumerate(acc_salvati, 1):
                mat = self.libreria.materiali[nome]
                p = mat.parametri
                print(f"  {i}. {nome} - {p['tipo']}, fyk={p['tensione_snervamento']:.0f} MPa")
            
            scelta = input("\nSeleziona acciaio (numero o 0 per saltare): ").strip()
            if scelta != "0":
                try:
                    idx = int(scelta) - 1
                    if 0 <= idx < len(acc_salvati):
                        nome_acc = acc_salvati[idx]
                        self.acciaio_corrente = self.libreria.recupera_acciaio(nome_acc)
                        print(f"Acciaio '{nome_acc}' selezionato.")
                except ValueError:
                    print("Selezione non valida.")
    
    def elimina_materiale(self):
        """Elimina materiale dalla libreria."""
        print("\n" + "="*100)
        print("ELIMINAZIONE MATERIALE")
        print("="*100)
        
        tutti = list(self.libreria.materiali.keys())
        if not tutti:
            print("\nNessun materiale in libreria.")
            return
        
        print("\nMATERIALI:")
        for i, nome in enumerate(tutti, 1):
            mat = self.libreria.materiali[nome]
            print(f"  {i}. {nome} ({mat.tipo})")
        
        scelta = input("\nMateriale da eliminare (numero): ").strip()
        try:
            idx = int(scelta) - 1
            if 0 <= idx < len(tutti):
                nome = tutti[idx]
                conferma = input(f"Confermi eliminazione di '{nome}'? (s/n): ").strip().lower()
                if conferma == 's':
                    self.libreria.rimuovi(nome)
                    print(f"Materiale '{nome}' eliminato.")
        except ValueError:
            print("Selezione non valida.")
    
    # ======================================================================================
    # MENU SEZIONI
    # ======================================================================================
    
    def menu_sezioni(self):
        """Menu definizione sezioni."""
        while True:
            self.mostra_intestazione()
            print("\nDEFINIZIONE SEZIONI:")
            print("  1. Sezione RETTANGOLARE")
            print("  2. Sezione CIRCOLARE")
            print("  3. Sezione a T")
            print("  4. Visualizza sezione corrente")
            print("  0. Torna al menu principale")
            print()
            
            scelta = input("Scegli: ").strip()
            
            if scelta == "1":
                self.definisci_sezione_rettangolare()
            elif scelta == "2":
                self.definisci_sezione_circolare()
            elif scelta == "3":
                self.definisci_sezione_t()
            elif scelta == "4":
                self.visualizza_sezione()
            elif scelta == "0":
                break
            else:
                print("\nScelta non valida.")
            
            if scelta != "0":
                input("\nPremere INVIO per continuare...")
    
    def definisci_sezione_rettangolare(self):
        """Definisce sezione rettangolare."""
        print("\n" + "="*100)
        print("SEZIONE RETTANGOLARE")
        print("="*100)
        
        if not self.calcestruzzo_corrente or not self.acciaio_corrente:
            print("\nATTENZIONE: Seleziona prima calcestruzzo e acciaio dal menu materiali.")
            return
        
        try:
            base = float(input("\nBase [mm]: ").strip())
            altezza = float(input("Altezza [mm]: ").strip())
            copriferro = float(input("Copriferro [mm]: ").strip())
            
            self.sezione_corrente = SezioneRettangolare(
                base=base,
                altezza=altezza,
                calcestruzzo=self.calcestruzzo_corrente,
                acciaio=self.acciaio_corrente,
                copriferro=copriferro
            )
            
            print(f"\nSezione rettangolare {base}x{altezza} mm creata.")
            print(f"Area calcestruzzo: {self.sezione_corrente.area_calcestruzzo():.0f} mm2")
            
        except ValueError as e:
            print(f"\nErrore: {e}")
    
    def definisci_sezione_circolare(self):
        """Definisce sezione circolare."""
        print("\n" + "="*100)
        print("SEZIONE CIRCOLARE")
        print("="*100)
        
        if not self.calcestruzzo_corrente or not self.acciaio_corrente:
            print("\nATTENZIONE: Seleziona prima calcestruzzo e acciaio dal menu materiali.")
            return
        
        try:
            diametro = float(input("\nDiametro [mm]: ").strip())
            copriferro = float(input("Copriferro [mm]: ").strip())
            
            self.sezione_corrente = SezioneCircolare(
                diametro=diametro,
                calcestruzzo=self.calcestruzzo_corrente,
                acciaio=self.acciaio_corrente,
                copriferro=copriferro
            )
            
            print(f"\nSezione circolare D={diametro} mm creata.")
            print(f"Area calcestruzzo: {self.sezione_corrente.area_calcestruzzo():.0f} mm2")
            
        except ValueError as e:
            print(f"\nErrore: {e}")
    
    def definisci_sezione_t(self):
        """Definisce sezione a T."""
        print("\n" + "="*100)
        print("SEZIONE A T")
        print("="*100)
        
        if not self.calcestruzzo_corrente or not self.acciaio_corrente:
            print("\nATTENZIONE: Seleziona prima calcestruzzo e acciaio dal menu materiali.")
            return
        
        try:
            larghezza_piattabanda = float(input("\nLarghezza piattabanda [mm]: ").strip())
            spessore_piattabanda = float(input("Spessore piattabanda [mm]: ").strip())
            larghezza_anima = float(input("Larghezza anima [mm]: ").strip())
            altezza_totale = float(input("Altezza totale [mm]: ").strip())
            copriferro = float(input("Copriferro [mm]: ").strip())
            
            self.sezione_corrente = SezioneT(
                larghezza_piattabanda=larghezza_piattabanda,
                spessore_piattabanda=spessore_piattabanda,
                larghezza_anima=larghezza_anima,
                altezza_totale=altezza_totale,
                calcestruzzo=self.calcestruzzo_corrente,
                acciaio=self.acciaio_corrente,
                copriferro=copriferro
            )
            
            print(f"\nSezione a T creata.")
            print(f"Area calcestruzzo: {self.sezione_corrente.area_calcestruzzo():.0f} mm2")
            
        except ValueError as e:
            print(f"\nErrore: {e}")
    
    def visualizza_sezione(self):
        """Visualizza sezione corrente."""
        if not self.sezione_corrente:
            print("\nNessuna sezione definita.")
            return
        
        print("\n" + "="*100)
        print("SEZIONE CORRENTE")
        print("="*100)
        print(f"\nTipo: {type(self.sezione_corrente).__name__}")
        print(f"Area calcestruzzo: {self.sezione_corrente.area_calcestruzzo():.0f} mm2")
        print(f"Copriferro: {self.sezione_corrente.copriferro:.1f} mm")
        
        if hasattr(self.sezione_corrente, 'base'):
            print(f"Dimensioni: {self.sezione_corrente.base} x {self.sezione_corrente.altezza} mm")
        elif hasattr(self.sezione_corrente, 'diametro'):
            print(f"Diametro: {self.sezione_corrente.diametro} mm")
    
    # ======================================================================================
    # MENU VERIFICHE
    # ======================================================================================
    
    def menu_verifiche(self):
        """Menu verifiche strutturali."""
        while True:
            self.mostra_intestazione()
            print("\nVERIFICHE STRUTTURALI:")
            print("  1. Verifica a FLESSIONE")
            print("  2. Verifica a TAGLIO")
            print("  3. Verifica a PRESSOFLESSIONE")
            print("  0. Torna al menu principale")
            print()
            
            scelta = input("Scegli: ").strip()
            
            if scelta == "1":
                self.verifica_flessione()
            elif scelta == "2":
                self.verifica_taglio()
            elif scelta == "3":
                self.verifica_pressoflessione()
            elif scelta == "0":
                break
            else:
                print("\nScelta non valida.")
            
            if scelta != "0":
                input("\nPremere INVIO per continuare...")
    
    def verifica_flessione(self):
        """Verifica a flessione."""
        print("\n" + "="*100)
        print("VERIFICA A FLESSIONE")
        print("="*100)
        
        if not self.sezione_corrente:
            print("\nDefinisci prima una sezione (menu SEZIONI).")
            return
        
        try:
            momento = float(input("\nMomento flettente [kNm]: ").strip())
            
            print("\nARMATURA:")
            n_ferri = int(input("Numero ferri tesi: ").strip())
            diametro = float(input("Diametro ferri [mm]: ").strip())
            
            import math
            area_ferro = math.pi * (diametro/2)**2
            area_armatura = n_ferri * area_ferro
            
            verifica = VerificaFlessione(self.sezione_corrente)
            risultato = verifica.verifica(momento_kNm=momento, area_armatura_tesa=area_armatura)
            
            print("\n" + "-"*100)
            print("RISULTATI VERIFICA:")
            print(f"  Momento applicato: {momento:.2f} kNm")
            print(f"  Armatura: {n_ferri} Ø{diametro} = {area_armatura:.0f} mm2")
            print(f"  Verifica: {'✓ VERIFICATO' if risultato['verificato'] else '✗ NON VERIFICATO'}")
            
            if 'momento_resistente' in risultato:
                print(f"  Momento resistente: {risultato['momento_resistente']:.2f} kNm")
                print(f"  Rapporto M/Mr: {risultato.get('rapporto_sollecitazione', 0):.3f}")
            
            print("-"*100)
            
        except ValueError as e:
            print(f"\nErrore: {e}")
    
    def verifica_taglio(self):
        """Verifica a taglio."""
        print("\n" + "="*100)
        print("VERIFICA A TAGLIO")
        print("="*100)
        
        if not self.sezione_corrente:
            print("\nDefinisci prima una sezione (menu SEZIONI).")
            return
        
        try:
            taglio = float(input("\nTaglio [kN]: ").strip())
            
            print("\nSTAFFE:")
            n_bracci = int(input("Numero bracci: ").strip())
            diametro = float(input("Diametro staffe [mm]: ").strip())
            passo = float(input("Passo staffe [mm]: ").strip())
            
            import math
            area_staffe = n_bracci * math.pi * (diametro/2)**2
            
            verifica = VerificaTaglio(self.sezione_corrente)
            risultato = verifica.verifica(
                taglio_kN=taglio,
                area_staffe=area_staffe,
                passo_staffe=passo
            )
            
            print("\n" + "-"*100)
            print("RISULTATI VERIFICA:")
            print(f"  Taglio applicato: {taglio:.2f} kN")
            print(f"  Staffe: {n_bracci} bracci Ø{diametro} passo {passo} mm")
            print(f"  Verifica: {'✓ VERIFICATO' if risultato['verificato'] else '✗ NON VERIFICATO'}")
            
            if 'taglio_resistente' in risultato:
                print(f"  Taglio resistente: {risultato['taglio_resistente']:.2f} kN")
            
            print("-"*100)
            
        except ValueError as e:
            print(f"\nErrore: {e}")
    
    def verifica_pressoflessione(self):
        """Verifica a pressoflessione."""
        print("\n" + "="*100)
        print("VERIFICA A PRESSOFLESSIONE")
        print("="*100)
        
        if not self.sezione_corrente:
            print("\nDefinisci prima una sezione (menu SEZIONI).")
            return
        
        try:
            normale = float(input("\nSforzo normale [kN] (positivo se compressione): ").strip())
            momento = float(input("Momento flettente [kNm]: ").strip())
            
            print("\nARMATURA:")
            n_ferri = int(input("Numero ferri totali: ").strip())
            diametro = float(input("Diametro ferri [mm]: ").strip())
            
            import math
            area_ferro = math.pi * (diametro/2)**2
            area_armatura_totale = n_ferri * area_ferro
            
            verifica = VerificaPressoflessioneRetta(self.sezione_corrente)
            risultato = verifica.verifica(
                sforzo_normale_kN=normale,
                momento_kNm=momento,
                area_armatura_totale=area_armatura_totale
            )
            
            print("\n" + "-"*100)
            print("RISULTATI VERIFICA:")
            print(f"  Sforzo normale: {normale:.2f} kN")
            print(f"  Momento: {momento:.2f} kNm")
            print(f"  Armatura: {n_ferri} Ø{diametro} = {area_armatura_totale:.0f} mm2")
            print(f"  Verifica: {'✓ VERIFICATO' if risultato['verificato'] else '✗ NON VERIFICATO'}")
            print("-"*100)
            
        except ValueError as e:
            print(f"\nErrore: {e}")
    
    # ======================================================================================
    # MENU TABELLE STORICHE
    # ======================================================================================
    
    def menu_tabelle_storiche(self):
        """Menu tabelle storiche."""
        while True:
            self.mostra_intestazione()
            print("\nTABELLE STORICHE RD 2229/1939:")
            print("  1. Tabella II - Calcestruzzo (resistenze)")
            print("  2. Tabella III - Malta (cemento/sabbia)")
            print("  3. Carichi unitari di sicurezza")
            print("  0. Torna al menu principale")
            print()
            
            scelta = input("Scegli: ").strip()
            
            if scelta == "1":
                self.mostra_tabella_ii()
            elif scelta == "2":
                self.mostra_tabella_iii()
            elif scelta == "3":
                self.mostra_carichi_unitari()
            elif scelta == "0":
                break
            else:
                print("\nScelta non valida.")
            
            if scelta != "0":
                input("\nPremere INVIO per continuare...")
    
    def mostra_tabella_ii(self):
        """Mostra Tabella II."""
        print("\n" + "="*100)
        print("TABELLA II - RESISTENZE CALCESTRUZZO [Kg/cm2]")
        print("="*100)
        print(f"{'A/C':<10} {'Normale':<15} {'Alta Res.':<15} {'Alluminoso':<15}")
        print("-"*100)
        
        ac_disponibili = set()
        for (ac, tipo), valore in TABELLA_II_CALCESTRUZZO.items():
            if tipo == "normale":
                ac_disponibili.add(ac)
        
        for ac_nom in sorted(ac_disponibili, key=lambda x: float(x.replace(',', '.'))):
            sigma_norm = TABELLA_II_CALCESTRUZZO.get((ac_nom, "normale"), "-")
            sigma_alt = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alta_resistenza"), "-")
            sigma_allum = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alluminoso"), "-")
            print(f"{ac_nom:<10} {str(sigma_norm):<15} {str(sigma_alt):<15} {str(sigma_allum):<15}")
    
    def mostra_tabella_iii(self):
        """Mostra Tabella III."""
        from verifiche_dm1939.core.tabella_malta import genera_tabella_malta_testo
        print()
        print(genera_tabella_malta_testo())
    
    def mostra_carichi_unitari(self):
        """Mostra carichi unitari."""
        print("\n" + "="*100)
        print("CARICHI UNITARI DI SICUREZZA [Kg/cm2]")
        print("="*100)
        print("\nCOMPRESSIONE CALCESTRUZZO:")
        print(f"  Sezioni compresse (normale): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_NORM}")
        print(f"  Sezioni compresse (alta res.): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_ALT}")
        print(f"  Sezioni inflesse (normale): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_NORM}")
        print(f"  Sezioni inflesse (alta res.): {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_ALT}")
        print("\nTAGLIO CALCESTRUZZO:")
        print(f"  Normale: {CarichUnitariSicurezza.TAU_TAGLIO_NORMALE}")
        print(f"  Alta resistenza: {CarichUnitariSicurezza.TAU_TAGLIO_ALTA_RESISTENZA}")
        print(f"  Alluminoso: {CarichUnitariSicurezza.TAU_TAGLIO_ALLUMINOSO}")
        print("\nACCIAI:")
        print(f"  Dolce (FeB32k): {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_DOLCE_NORMAL}")
        print(f"  Semiriduro (FeB38k): {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_SEMI}")
        print(f"  Duro (FeB44k): {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_DURO_NORMAL}")
    
    # ======================================================================================
    # MENU REPORT
    # ======================================================================================
    
    def menu_report(self):
        """Menu generazione report."""
        print("\n" + "="*100)
        print("GENERAZIONE REPORT")
        print("="*100)
        print("\nFunzionalità in sviluppo.")
        print("Usa i moduli di reporting esistenti per generare documentazione.")
        input("\nPremere INVIO per continuare...")


# ======================================================================================
# MAIN
# ======================================================================================

if __name__ == "__main__":
    try:
        gui = GUIVerificheComplete()
        gui.menu_principale()
    except KeyboardInterrupt:
        print("\n\nOperazione annullata.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nErrore inaspettato: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
