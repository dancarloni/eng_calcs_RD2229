"""
GUI WINDOWS - VERIFICHE STRUTTURALI RD 2229/1939
Interfaccia grafica per Windows con tkinter

Sistema completo: Materiali storici Santarella + Verifiche strutturali
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import math
import json

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
    genera_tabella_malta_testo,
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


class LibreriaMateriali:
    """Gestisce la libreria dei materiali."""
    
    def __init__(self, file_path="libreria_materiali.json"):
        self.file_path = Path(file_path)
        self.materiali = {}
        self.carica()
    
    def carica(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.materiali = json.load(f)
            except:
                self.materiali = {}
    
    def salva(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.materiali, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare: {e}")
    
    def aggiungi_calcestruzzo(self, nome, cls, note=""):
        self.materiali[nome] = {
            'tipo': 'calcestruzzo',
            'rck': cls.resistenza_caratteristica,
            'ec': cls.modulo_elastico,
            'sigma_amm': cls.tensione_ammissibile_compressione,
            'tau_amm': cls.tensione_ammissibile_taglio,
            'n': cls.coefficiente_omogeneizzazione,
            'note': note
        }
        self.salva()
    
    def aggiungi_acciaio(self, nome, acc, note=""):
        self.materiali[nome] = {
            'tipo': 'acciaio',
            'tipo_acc': acc.tipo,
            'fyk': acc.tensione_snervamento,
            'sigma_amm': acc.tensione_ammissibile,
            'es': acc.modulo_elastico,
            'aderenza': acc.aderenza_migliorata,
            'note': note
        }
        self.salva()
    
    def elenca_calcestruzzi(self):
        return [k for k, v in self.materiali.items() if v.get('tipo') == 'calcestruzzo']
    
    def elenca_acciai(self):
        return [k for k, v in self.materiali.items() if v.get('tipo') == 'acciaio']


class GUIVerificheWindows:
    """Interfaccia grafica Windows principale."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Verifiche Strutturali RD 2229/1939 - Prontuario Santarella")
        self.root.geometry("1000x700")
        
        self.libreria = LibreriaMateriali()
        self.calcestruzzo_corrente = None
        self.acciaio_corrente = None
        self.sezione_corrente = None
        
        self.crea_interfaccia()
    
    def crea_interfaccia(self):
        """Crea l'interfaccia principale."""
        # Barra superiore - Stato
        self.frame_stato = ttk.Frame(self.root, relief=tk.RIDGE, borderwidth=2)
        self.frame_stato.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.frame_stato, text="STATO:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=3)
        
        self.lbl_cls = ttk.Label(self.frame_stato, text="Calcestruzzo: Nessuno", foreground="red")
        self.lbl_cls.grid(row=0, column=1, padx=10, pady=3)
        
        self.lbl_acc = ttk.Label(self.frame_stato, text="Acciaio: Nessuno", foreground="red")
        self.lbl_acc.grid(row=0, column=2, padx=10, pady=3)
        
        self.lbl_sez = ttk.Label(self.frame_stato, text="Sezione: Nessuna", foreground="red")
        self.lbl_sez.grid(row=0, column=3, padx=10, pady=3)
        
        # Notebook con tab
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Materiali
        self.tab_materiali = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_materiali, text="📦 MATERIALI")
        self.crea_tab_materiali()
        
        # Tab 2: Sezioni
        self.tab_sezioni = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sezioni, text="📐 SEZIONI")
        self.crea_tab_sezioni()
        
        # Tab 3: Verifiche
        self.tab_verifiche = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_verifiche, text="✓ VERIFICHE")
        self.crea_tab_verifiche()
        
        # Tab 4: Tabelle Storiche
        self.tab_tabelle = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tabelle, text="📊 TABELLE")
        self.crea_tab_tabelle()
        
        self.aggiorna_stato()
    
    # ==================================================================================
    # TAB MATERIALI
    # ==================================================================================
    
    def crea_tab_materiali(self):
        """Crea il tab materiali."""
        # Frame sinistra - Calcolo
        frame_calc = ttk.LabelFrame(self.tab_materiali, text="Calcolo Materiali Storici", padding=10)
        frame_calc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Calcestruzzo
        ttk.Label(frame_calc, text="CALCESTRUZZO SANTARELLA", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame_calc, text="Resistenza [Kg/cm²]:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_sigma_cls = ttk.Entry(frame_calc, width=15)
        self.entry_sigma_cls.grid(row=1, column=1, pady=5)
        self.entry_sigma_cls.insert(0, "280")
        
        ttk.Label(frame_calc, text="Tipo cemento:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.combo_tipo_cemento = ttk.Combobox(frame_calc, width=13, state='readonly')
        self.combo_tipo_cemento['values'] = ('Normale', 'Alta resistenza', 'Alluminoso')
        self.combo_tipo_cemento.current(0)
        self.combo_tipo_cemento.grid(row=2, column=1, pady=5)
        
        ttk.Button(frame_calc, text="Calcola Calcestruzzo", command=self.calcola_calcestruzzo).grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Separator(frame_calc, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, sticky='ew', pady=15)
        
        # Acciaio
        ttk.Label(frame_calc, text="ACCIAIO STORICO", font=('Arial', 10, 'bold')).grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame_calc, text="Resistenza [Kg/cm²]:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.entry_sigma_acc = ttk.Entry(frame_calc, width=15)
        self.entry_sigma_acc.grid(row=6, column=1, pady=5)
        self.entry_sigma_acc.insert(0, "1400")
        
        ttk.Label(frame_calc, text="Tipo acciaio:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.combo_tipo_acciaio = ttk.Combobox(frame_calc, width=13, state='readonly')
        self.combo_tipo_acciaio['values'] = ('Dolce (FeB32k)', 'Semiriduro (FeB38k)', 'Duro (FeB44k)')
        self.combo_tipo_acciaio.current(0)
        self.combo_tipo_acciaio.grid(row=7, column=1, pady=5)
        
        ttk.Button(frame_calc, text="Calcola Acciaio", command=self.calcola_acciaio).grid(row=8, column=0, columnspan=2, pady=10)
        
        # Frame destra - Libreria
        frame_lib = ttk.LabelFrame(self.tab_materiali, text="Libreria Materiali", padding=10)
        frame_lib.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Listbox materiali
        self.listbox_materiali = tk.Listbox(frame_lib, height=20)
        self.listbox_materiali.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Pulsanti libreria
        frame_btn_lib = ttk.Frame(frame_lib)
        frame_btn_lib.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_btn_lib, text="Aggiorna", command=self.aggiorna_libreria).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_btn_lib, text="Usa selezionato", command=self.usa_materiale_selezionato).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_btn_lib, text="Elimina", command=self.elimina_materiale_selezionato).pack(side=tk.LEFT, padx=2)
        
        self.aggiorna_libreria()
    
    def calcola_calcestruzzo(self):
        """Calcola calcestruzzo da Santarella."""
        try:
            sigma_kgcm2 = float(self.entry_sigma_cls.get())
            tipo_map = {'Normale': 'normale', 'Alta resistenza': 'alta_resistenza', 'Alluminoso': 'alluminoso'}
            tipo_cemento = tipo_map[self.combo_tipo_cemento.get()]
            
            cls = Calcestruzzo.da_tabella_storica(sigma_kgcm2, tipo_cemento)
            
            # Mostra risultati
            msg = f"CALCESTRUZZO CALCOLATO:\n\n"
            msg += f"Resistenza input: {sigma_kgcm2:.0f} Kg/cm²\n\n"
            msg += f"Rck = {cls.resistenza_caratteristica:.2f} MPa ({mpa_to_kgcm2(cls.resistenza_caratteristica):.1f} Kg/cm²)\n"
            msg += f"σc,amm = {cls.tensione_ammissibile_compressione:.3f} MPa ({mpa_to_kgcm2(cls.tensione_ammissibile_compressione):.1f} Kg/cm²)\n"
            msg += f"τc,amm = {cls.tensione_ammissibile_taglio:.3f} MPa ({mpa_to_kgcm2(cls.tensione_ammissibile_taglio):.1f} Kg/cm²)\n"
            msg += f"Ec (Santarella) = {cls.modulo_elastico:.0f} MPa\n"
            msg += f"n = {cls.coefficiente_omogeneizzazione:.2f}\n\n"
            msg += f"Salvare in libreria?"
            
            if messagebox.askyesno("Risultati Calcestruzzo", msg):
                nome = simpledialog.askstring("Salva", "Nome identificativo:")
                if nome:
                    self.libreria.aggiungi_calcestruzzo(nome, cls)
                    self.calcestruzzo_corrente = cls
                    self.aggiorna_libreria()
                    self.aggiorna_stato()
                    messagebox.showinfo("Successo", f"Calcestruzzo '{nome}' salvato e impostato come attivo.")
            
        except ValueError as e:
            messagebox.showerror("Errore", f"Valore non valido: {e}")
    
    def calcola_acciaio(self):
        """Calcola acciaio storico."""
        try:
            sigma_kgcm2 = float(self.entry_sigma_acc.get())
            tipo_map = {'Dolce (FeB32k)': 'dolce', 'Semiriduro (FeB38k)': 'semiriduro', 'Duro (FeB44k)': 'duro'}
            tipo_acciaio = tipo_map[self.combo_tipo_acciaio.get()]
            
            acc = Acciaio.da_tabella_storica(sigma_kgcm2, tipo_acciaio)
            
            # Mostra risultati
            msg = f"ACCIAIO CALCOLATO:\n\n"
            msg += f"Tipo: {acc.tipo}\n"
            msg += f"fyk = {acc.tensione_snervamento:.0f} MPa ({mpa_to_kgcm2(acc.tensione_snervamento):.0f} Kg/cm²)\n"
            msg += f"σs,amm = {acc.tensione_ammissibile:.1f} MPa ({mpa_to_kgcm2(acc.tensione_ammissibile):.0f} Kg/cm²)\n"
            msg += f"Aderenza: {'Migliorata' if acc.aderenza_migliorata else 'Liscia'}\n\n"
            msg += f"Salvare in libreria?"
            
            if messagebox.askyesno("Risultati Acciaio", msg):
                nome = simpledialog.askstring("Salva", "Nome identificativo:")
                if nome:
                    self.libreria.aggiungi_acciaio(nome, acc)
                    self.acciaio_corrente = acc
                    self.aggiorna_libreria()
                    self.aggiorna_stato()
                    messagebox.showinfo("Successo", f"Acciaio '{nome}' salvato e impostato come attivo.")
            
        except ValueError as e:
            messagebox.showerror("Errore", f"Valore non valido: {e}")
    
    def aggiorna_libreria(self):
        """Aggiorna la listbox della libreria."""
        self.listbox_materiali.delete(0, tk.END)
        for nome, mat in self.libreria.materiali.items():
            if mat['tipo'] == 'calcestruzzo':
                self.listbox_materiali.insert(tk.END, f"🔲 {nome} - Rck={mat['rck']:.1f} MPa")
            else:
                self.listbox_materiali.insert(tk.END, f"🔧 {nome} - {mat['tipo_acc']}, fyk={mat['fyk']:.0f} MPa")
    
    def usa_materiale_selezionato(self):
        """Usa il materiale selezionato dalla libreria."""
        sel = self.listbox_materiali.curselection()
        if not sel:
            messagebox.showwarning("Attenzione", "Seleziona un materiale.")
            return
        
        idx = sel[0]
        nome = list(self.libreria.materiali.keys())[idx]
        mat = self.libreria.materiali[nome]
        
        if mat['tipo'] == 'calcestruzzo':
            self.calcestruzzo_corrente = Calcestruzzo(
                resistenza_caratteristica=mat['rck'],
                modulo_elastico=mat['ec'],
                tensione_ammissibile_compressione=mat['sigma_amm'],
                tensione_ammissibile_taglio=mat['tau_amm'],
                coefficiente_omogeneizzazione=mat['n']
            )
            messagebox.showinfo("Successo", f"Calcestruzzo '{nome}' impostato come attivo.")
        else:
            self.acciaio_corrente = Acciaio(
                tipo=mat['tipo_acc'],
                tensione_snervamento=mat['fyk'],
                tensione_ammissibile=mat['sigma_amm'],
                modulo_elastico=mat['es'],
                aderenza_migliorata=mat['aderenza']
            )
            messagebox.showinfo("Successo", f"Acciaio '{nome}' impostato come attivo.")
        
        self.aggiorna_stato()
    
    def elimina_materiale_selezionato(self):
        """Elimina materiale selezionato."""
        sel = self.listbox_materiali.curselection()
        if not sel:
            messagebox.showwarning("Attenzione", "Seleziona un materiale.")
            return
        
        idx = sel[0]
        nome = list(self.libreria.materiali.keys())[idx]
        
        if messagebox.askyesno("Conferma", f"Eliminare '{nome}'?"):
            del self.libreria.materiali[nome]
            self.libreria.salva()
            self.aggiorna_libreria()
    
    # ==================================================================================
    # TAB SEZIONI
    # ==================================================================================
    
    def crea_tab_sezioni(self):
        """Crea il tab sezioni."""
        # Frame calcolo
        frame_calc = ttk.LabelFrame(self.tab_sezioni, text="Definizione Sezione", padding=10)
        frame_calc.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(frame_calc, text="Tipo sezione:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.combo_tipo_sezione = ttk.Combobox(frame_calc, width=20, state='readonly')
        self.combo_tipo_sezione['values'] = ('Rettangolare', 'Circolare', 'T')
        self.combo_tipo_sezione.current(0)
        self.combo_tipo_sezione.grid(row=0, column=1, pady=5)
        self.combo_tipo_sezione.bind('<<ComboboxSelected>>', self.cambia_tipo_sezione)
        
        # Frame parametri sezione (cambia in base al tipo)
        self.frame_param_sez = ttk.Frame(frame_calc)
        self.frame_param_sez.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.cambia_tipo_sezione()
        
        ttk.Button(frame_calc, text="Crea Sezione", command=self.crea_sezione, width=30).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Info sezione corrente
        self.text_info_sez = scrolledtext.ScrolledText(frame_calc, height=15, width=70)
        self.text_info_sez.grid(row=3, column=0, columnspan=2, pady=10)
    
    def cambia_tipo_sezione(self, event=None):
        """Cambia i parametri in base al tipo di sezione."""
        for widget in self.frame_param_sez.winfo_children():
            widget.destroy()
        
        tipo = self.combo_tipo_sezione.get()
        
        if tipo == 'Rettangolare':
            ttk.Label(self.frame_param_sez, text="Base [mm]:").grid(row=0, column=0, sticky=tk.W, pady=3)
            self.entry_base = ttk.Entry(self.frame_param_sez, width=15)
            self.entry_base.grid(row=0, column=1, pady=3)
            self.entry_base.insert(0, "300")
            
            ttk.Label(self.frame_param_sez, text="Altezza [mm]:").grid(row=1, column=0, sticky=tk.W, pady=3)
            self.entry_altezza = ttk.Entry(self.frame_param_sez, width=15)
            self.entry_altezza.grid(row=1, column=1, pady=3)
            self.entry_altezza.insert(0, "500")
            
            ttk.Label(self.frame_param_sez, text="Copriferro [mm]:").grid(row=2, column=0, sticky=tk.W, pady=3)
            self.entry_copriferro = ttk.Entry(self.frame_param_sez, width=15)
            self.entry_copriferro.grid(row=2, column=1, pady=3)
            self.entry_copriferro.insert(0, "30")
            
        elif tipo == 'Circolare':
            ttk.Label(self.frame_param_sez, text="Diametro [mm]:").grid(row=0, column=0, sticky=tk.W, pady=3)
            self.entry_diametro = ttk.Entry(self.frame_param_sez, width=15)
            self.entry_diametro.grid(row=0, column=1, pady=3)
            self.entry_diametro.insert(0, "400")
            
            ttk.Label(self.frame_param_sez, text="Copriferro [mm]:").grid(row=1, column=0, sticky=tk.W, pady=3)
            self.entry_copriferro = ttk.Entry(self.frame_param_sez, width=15)
            self.entry_copriferro.grid(row=1, column=1, pady=3)
            self.entry_copriferro.insert(0, "30")
            
        elif tipo == 'T':
            ttk.Label(self.frame_param_sez, text="Largh. piattabanda [mm]:").grid(row=0, column=0, sticky=tk.W, pady=3)
            self.entry_larg_piat = ttk.Entry(self.frame_param_sez, width=15)
            self.entry_larg_piat.grid(row=0, column=1, pady=3)
            self.entry_larg_piat.insert(0, "600")
            
            ttk.Label(self.frame_param_sez, text="Spes. piattabanda [mm]:").grid(row=1, column=0, sticky=tk.W, pady=3)
            self.entry_spes_piat = ttk.Entry(self.frame_param_sez, width=15)
            self.entry_spes_piat.grid(row=1, column=1, pady=3)
            self.entry_spes_piat.insert(0, "100")
            
            ttk.Label(self.frame_param_sez, text="Larghezza anima [mm]:").grid(row=2, column=0, sticky=tk.W, pady=3)
            self.entry_larg_anima = ttk.Entry(self.frame_param_sez, width=15)
            self.entry_larg_anima.grid(row=2, column=1, pady=3)
            self.entry_larg_anima.insert(0, "300")
            
            ttk.Label(self.frame_param_sez, text="Altezza totale [mm]:").grid(row=3, column=0, sticky=tk.W, pady=3)
            self.entry_alt_tot = ttk.Entry(self.frame_param_sez, width=15)
            self.entry_alt_tot.grid(row=3, column=1, pady=3)
            self.entry_alt_tot.insert(0, "500")
            
            ttk.Label(self.frame_param_sez, text="Copriferro [mm]:").grid(row=4, column=0, sticky=tk.W, pady=3)
            self.entry_copriferro = ttk.Entry(self.frame_param_sez, width=15)
            self.entry_copriferro.grid(row=4, column=1, pady=3)
            self.entry_copriferro.insert(0, "30")
    
    def crea_sezione(self):
        """Crea la sezione selezionata."""
        if not self.calcestruzzo_corrente or not self.acciaio_corrente:
            messagebox.showerror("Errore", "Seleziona prima calcestruzzo e acciaio dal tab MATERIALI.")
            return
        
        try:
            tipo = self.combo_tipo_sezione.get()
            copriferro = float(self.entry_copriferro.get())
            
            if tipo == 'Rettangolare':
                base = float(self.entry_base.get())
                altezza = float(self.entry_altezza.get())
                self.sezione_corrente = SezioneRettangolare(
                    base=base,
                    altezza=altezza,
                    calcestruzzo=self.calcestruzzo_corrente,
                    acciaio=self.acciaio_corrente,
                    copriferro=copriferro
                )
                info = f"SEZIONE RETTANGOLARE\n"
                info += f"Base: {base} mm\n"
                info += f"Altezza: {altezza} mm\n"
                
            elif tipo == 'Circolare':
                diametro = float(self.entry_diametro.get())
                self.sezione_corrente = SezioneCircolare(
                    diametro=diametro,
                    calcestruzzo=self.calcestruzzo_corrente,
                    acciaio=self.acciaio_corrente,
                    copriferro=copriferro
                )
                info = f"SEZIONE CIRCOLARE\n"
                info += f"Diametro: {diametro} mm\n"
                
            elif tipo == 'T':
                larg_piat = float(self.entry_larg_piat.get())
                spes_piat = float(self.entry_spes_piat.get())
                larg_anima = float(self.entry_larg_anima.get())
                alt_tot = float(self.entry_alt_tot.get())
                self.sezione_corrente = SezioneT(
                    larghezza_piattabanda=larg_piat,
                    spessore_piattabanda=spes_piat,
                    larghezza_anima=larg_anima,
                    altezza_totale=alt_tot,
                    calcestruzzo=self.calcestruzzo_corrente,
                    acciaio=self.acciaio_corrente,
                    copriferro=copriferro
                )
                info = f"SEZIONE A T\n"
                info += f"Larghezza piattabanda: {larg_piat} mm\n"
                info += f"Spessore piattabanda: {spes_piat} mm\n"
                info += f"Larghezza anima: {larg_anima} mm\n"
                info += f"Altezza totale: {alt_tot} mm\n"
            
            info += f"Copriferro: {copriferro} mm\n"
            info += f"Area calcestruzzo: {self.sezione_corrente.area_calcestruzzo():.0f} mm²\n"
            
            self.text_info_sez.delete(1.0, tk.END)
            self.text_info_sez.insert(1.0, info)
            
            self.aggiorna_stato()
            messagebox.showinfo("Successo", "Sezione creata correttamente.")
            
        except ValueError as e:
            messagebox.showerror("Errore", f"Valori non validi: {e}")
    
    # ==================================================================================
    # TAB VERIFICHE
    # ==================================================================================
    
    def crea_tab_verifiche(self):
        """Crea il tab verifiche."""
        # Notebook interno per i tipi di verifica
        nb_verifiche = ttk.Notebook(self.tab_verifiche)
        nb_verifiche.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tab Flessione
        self.tab_fless = ttk.Frame(nb_verifiche)
        nb_verifiche.add(self.tab_fless, text="Flessione")
        self.crea_verifica_flessione()
        
        # Sub-tab Taglio
        self.tab_tagl = ttk.Frame(nb_verifiche)
        nb_verifiche.add(self.tab_tagl, text="Taglio")
        self.crea_verifica_taglio()
        
        # Sub-tab Pressoflessione
        self.tab_press = ttk.Frame(nb_verifiche)
        nb_verifiche.add(self.tab_press, text="Pressoflessione")
        self.crea_verifica_pressoflessione()
    
    def crea_verifica_flessione(self):
        """Crea interfaccia verifica flessione."""
        frame = ttk.LabelFrame(self.tab_fless, text="Verifica a Flessione", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(frame, text="Momento [kNm]:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_momento = ttk.Entry(frame, width=15)
        self.entry_momento.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Numero ferri tesi:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_n_ferri_fless = ttk.Entry(frame, width=15)
        self.entry_n_ferri_fless.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Diametro ferri [mm]:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_diam_ferri_fless = ttk.Entry(frame, width=15)
        self.entry_diam_ferri_fless.grid(row=2, column=1, pady=5)
        
        ttk.Button(frame, text="VERIFICA", command=self.esegui_verifica_flessione).grid(row=3, column=0, columnspan=2, pady=10)
        
        self.text_ris_fless = scrolledtext.ScrolledText(frame, height=15, width=80)
        self.text_ris_fless.grid(row=4, column=0, columnspan=2, pady=10)
    
    def esegui_verifica_flessione(self):
        """Esegue verifica a flessione."""
        if not self.sezione_corrente:
            messagebox.showerror("Errore", "Definisci prima una sezione nel tab SEZIONI.")
            return
        
        try:
            momento = float(self.entry_momento.get())
            n_ferri = int(self.entry_n_ferri_fless.get())
            diametro = float(self.entry_diam_ferri_fless.get())
            
            area_ferro = math.pi * (diametro/2)**2
            area_armatura = n_ferri * area_ferro
            
            verifica = VerificaFlessione(self.sezione_corrente)
            risultato = verifica.verifica(momento_kNm=momento, area_armatura_tesa=area_armatura)
            
            ris = f"VERIFICA A FLESSIONE\n{'='*60}\n\n"
            ris += f"Momento applicato: {momento:.2f} kNm\n"
            ris += f"Armatura: {n_ferri} Ø{diametro} = {area_armatura:.0f} mm²\n\n"
            ris += f"RISULTATO: {'✓ VERIFICATO' if risultato['verificato'] else '✗ NON VERIFICATO'}\n\n"
            
            if 'momento_resistente' in risultato:
                ris += f"Momento resistente: {risultato['momento_resistente']:.2f} kNm\n"
                ris += f"Rapporto M/Mr: {risultato.get('rapporto_sollecitazione', 0):.3f}\n"
            
            if 'messaggio' in risultato:
                ris += f"\n{risultato['messaggio']}\n"
            
            self.text_ris_fless.delete(1.0, tk.END)
            self.text_ris_fless.insert(1.0, ris)
            
        except ValueError as e:
            messagebox.showerror("Errore", f"Valori non validi: {e}")
    
    def crea_verifica_taglio(self):
        """Crea interfaccia verifica taglio."""
        frame = ttk.LabelFrame(self.tab_tagl, text="Verifica a Taglio", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(frame, text="Taglio [kN]:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_taglio = ttk.Entry(frame, width=15)
        self.entry_taglio.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Numero bracci staffe:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_n_bracci = ttk.Entry(frame, width=15)
        self.entry_n_bracci.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Diametro staffe [mm]:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_diam_staffe = ttk.Entry(frame, width=15)
        self.entry_diam_staffe.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Passo staffe [mm]:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_passo = ttk.Entry(frame, width=15)
        self.entry_passo.grid(row=3, column=1, pady=5)
        
        ttk.Button(frame, text="VERIFICA", command=self.esegui_verifica_taglio).grid(row=4, column=0, columnspan=2, pady=10)
        
        self.text_ris_tagl = scrolledtext.ScrolledText(frame, height=15, width=80)
        self.text_ris_tagl.grid(row=5, column=0, columnspan=2, pady=10)
    
    def esegui_verifica_taglio(self):
        """Esegue verifica a taglio."""
        if not self.sezione_corrente:
            messagebox.showerror("Errore", "Definisci prima una sezione nel tab SEZIONI.")
            return
        
        try:
            taglio = float(self.entry_taglio.get())
            n_bracci = int(self.entry_n_bracci.get())
            diametro = float(self.entry_diam_staffe.get())
            passo = float(self.entry_passo.get())
            
            area_staffe = n_bracci * math.pi * (diametro/2)**2
            
            verifica = VerificaTaglio(self.sezione_corrente)
            risultato = verifica.verifica(
                taglio_kN=taglio,
                area_staffe=area_staffe,
                passo_staffe=passo
            )
            
            ris = f"VERIFICA A TAGLIO\n{'='*60}\n\n"
            ris += f"Taglio applicato: {taglio:.2f} kN\n"
            ris += f"Staffe: {n_bracci} bracci Ø{diametro} passo {passo} mm\n"
            ris += f"Area staffe: {area_staffe:.0f} mm²\n\n"
            ris += f"RISULTATO: {'✓ VERIFICATO' if risultato['verificato'] else '✗ NON VERIFICATO'}\n\n"
            
            if 'taglio_resistente' in risultato:
                ris += f"Taglio resistente: {risultato['taglio_resistente']:.2f} kN\n"
            
            if 'messaggio' in risultato:
                ris += f"\n{risultato['messaggio']}\n"
            
            self.text_ris_tagl.delete(1.0, tk.END)
            self.text_ris_tagl.insert(1.0, ris)
            
        except ValueError as e:
            messagebox.showerror("Errore", f"Valori non validi: {e}")
    
    def crea_verifica_pressoflessione(self):
        """Crea interfaccia verifica pressoflessione."""
        frame = ttk.LabelFrame(self.tab_press, text="Verifica a Pressoflessione", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(frame, text="Sforzo normale [kN]:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text="(positivo se compressione)").grid(row=0, column=2, sticky=tk.W)
        self.entry_normale = ttk.Entry(frame, width=15)
        self.entry_normale.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Momento [kNm]:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_momento_press = ttk.Entry(frame, width=15)
        self.entry_momento_press.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Numero ferri totali:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_n_ferri_press = ttk.Entry(frame, width=15)
        self.entry_n_ferri_press.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Diametro ferri [mm]:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_diam_ferri_press = ttk.Entry(frame, width=15)
        self.entry_diam_ferri_press.grid(row=3, column=1, pady=5)
        
        ttk.Button(frame, text="VERIFICA", command=self.esegui_verifica_pressoflessione).grid(row=4, column=0, columnspan=2, pady=10)
        
        self.text_ris_press = scrolledtext.ScrolledText(frame, height=15, width=80)
        self.text_ris_press.grid(row=5, column=0, columnspan=3, pady=10)
    
    def esegui_verifica_pressoflessione(self):
        """Esegue verifica a pressoflessione."""
        if not self.sezione_corrente:
            messagebox.showerror("Errore", "Definisci prima una sezione nel tab SEZIONI.")
            return
        
        try:
            normale = float(self.entry_normale.get())
            momento = float(self.entry_momento_press.get())
            n_ferri = int(self.entry_n_ferri_press.get())
            diametro = float(self.entry_diam_ferri_press.get())
            
            area_ferro = math.pi * (diametro/2)**2
            area_armatura = n_ferri * area_ferro
            
            verifica = VerificaPressoflessioneRetta(self.sezione_corrente)
            risultato = verifica.verifica(
                sforzo_normale_kN=normale,
                momento_kNm=momento,
                area_armatura_totale=area_armatura
            )
            
            ris = f"VERIFICA A PRESSOFLESSIONE\n{'='*60}\n\n"
            ris += f"Sforzo normale: {normale:.2f} kN\n"
            ris += f"Momento: {momento:.2f} kNm\n"
            ris += f"Armatura: {n_ferri} Ø{diametro} = {area_armatura:.0f} mm²\n\n"
            ris += f"RISULTATO: {'✓ VERIFICATO' if risultato['verificato'] else '✗ NON VERIFICATO'}\n\n"
            
            if 'messaggio' in risultato:
                ris += f"{risultato['messaggio']}\n"
            
            self.text_ris_press.delete(1.0, tk.END)
            self.text_ris_press.insert(1.0, ris)
            
        except ValueError as e:
            messagebox.showerror("Errore", f"Valori non validi: {e}")
    
    # ==================================================================================
    # TAB TABELLE
    # ==================================================================================
    
    def crea_tab_tabelle(self):
        """Crea il tab tabelle storiche."""
        nb_tabelle = ttk.Notebook(self.tab_tabelle)
        nb_tabelle.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tabella II
        tab_tab2 = ttk.Frame(nb_tabelle)
        nb_tabelle.add(tab_tab2, text="Tabella II - Calcestruzzo")
        
        text_tab2 = scrolledtext.ScrolledText(tab_tab2, font=('Courier', 9))
        text_tab2.pack(fill=tk.BOTH, expand=True)
        
        contenuto = "TABELLA II - RESISTENZE CALCESTRUZZO [Kg/cm²]\n"
        contenuto += "="*80 + "\n"
        contenuto += f"{'A/C':<10} {'Normale':<15} {'Alta Res.':<15} {'Alluminoso':<15}\n"
        contenuto += "-"*80 + "\n"
        
        ac_disponibili = set()
        for (ac, tipo), valore in TABELLA_II_CALCESTRUZZO.items():
            if tipo == "normale":
                ac_disponibili.add(ac)
        
        for ac_nom in sorted(ac_disponibili, key=lambda x: float(x.replace(',', '.'))):
            sigma_norm = TABELLA_II_CALCESTRUZZO.get((ac_nom, "normale"), "-")
            sigma_alt = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alta_resistenza"), "-")
            sigma_allum = TABELLA_II_CALCESTRUZZO.get((ac_nom, "alluminoso"), "-")
            contenuto += f"{ac_nom:<10} {str(sigma_norm):<15} {str(sigma_alt):<15} {str(sigma_allum):<15}\n"
        
        text_tab2.insert(1.0, contenuto)
        text_tab2.config(state=tk.DISABLED)
        
        # Tabella III
        tab_tab3 = ttk.Frame(nb_tabelle)
        nb_tabelle.add(tab_tab3, text="Tabella III - Malta")
        
        text_tab3 = scrolledtext.ScrolledText(tab_tab3, font=('Courier', 9))
        text_tab3.pack(fill=tk.BOTH, expand=True)
        text_tab3.insert(1.0, genera_tabella_malta_testo())
        text_tab3.config(state=tk.DISABLED)
        
        # Carichi Unitari
        tab_carichi = ttk.Frame(nb_tabelle)
        nb_tabelle.add(tab_carichi, text="Carichi Unitari")
        
        text_carichi = scrolledtext.ScrolledText(tab_carichi, font=('Courier', 9))
        text_carichi.pack(fill=tk.BOTH, expand=True)
        
        contenuto_car = "CARICHI UNITARI DI SICUREZZA [Kg/cm²]\n"
        contenuto_car += "="*80 + "\n\n"
        contenuto_car += "COMPRESSIONE CALCESTRUZZO:\n"
        contenuto_car += f"  Sezioni compresse (normale):     {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_NORM}\n"
        contenuto_car += f"  Sezioni compresse (alta res.):   {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_SEMPLICE_ALT}\n"
        contenuto_car += f"  Sezioni inflesse (normale):      {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_NORM}\n"
        contenuto_car += f"  Sezioni inflesse (alta res.):    {CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_ALT}\n\n"
        contenuto_car += "TAGLIO CALCESTRUZZO:\n"
        contenuto_car += f"  Normale:          {CarichUnitariSicurezza.TAU_TAGLIO_NORMALE}\n"
        contenuto_car += f"  Alta resistenza:  {CarichUnitariSicurezza.TAU_TAGLIO_ALTA_RESISTENZA}\n"
        contenuto_car += f"  Alluminoso:       {CarichUnitariSicurezza.TAU_TAGLIO_ALLUMINOSO}\n\n"
        contenuto_car += "ACCIAI:\n"
        contenuto_car += f"  Dolce (FeB32k):      {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_DOLCE_NORMAL}\n"
        contenuto_car += f"  Semiriduro (FeB38k): {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_SEMI}\n"
        contenuto_car += f"  Duro (FeB44k):       {CarichUnitariSicurezza.SIGMA_S_MAX_ACCIAIO_DURO_NORMAL}\n"
        
        text_carichi.insert(1.0, contenuto_car)
        text_carichi.config(state=tk.DISABLED)
    
    # ==================================================================================
    # UTILITIES
    # ==================================================================================
    
    def aggiorna_stato(self):
        """Aggiorna la barra di stato."""
        if self.calcestruzzo_corrente:
            self.lbl_cls.config(
                text=f"Calcestruzzo: Rck={self.calcestruzzo_corrente.resistenza_caratteristica:.1f} MPa",
                foreground="green"
            )
        else:
            self.lbl_cls.config(text="Calcestruzzo: Nessuno", foreground="red")
        
        if self.acciaio_corrente:
            self.lbl_acc.config(
                text=f"Acciaio: {self.acciaio_corrente.tipo}, fyk={self.acciaio_corrente.tensione_snervamento:.0f} MPa",
                foreground="green"
            )
        else:
            self.lbl_acc.config(text="Acciaio: Nessuno", foreground="red")
        
        if self.sezione_corrente:
            self.lbl_sez.config(
                text=f"Sezione: {type(self.sezione_corrente).__name__}",
                foreground="green"
            )
        else:
            self.lbl_sez.config(text="Sezione: Nessuna", foreground="red")


# ======================================================================================
# MAIN
# ======================================================================================

def main():
    root = tk.Tk()
    app = GUIVerificheWindows(root)
    root.mainloop()


if __name__ == "__main__":
    main()
