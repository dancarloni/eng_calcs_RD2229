"""
Modulo CSV Handler - Gestione import/export dati da file CSV.

Supporta caricamento bulk di dati per verifiche strutturali
con intestazioni personalizzate.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import csv
import pandas as pd

from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.materials.acciaio import Acciaio
from verifiche_dm1939.sections.sezione_rettangolare import SezioneRettangolare


class CSVHandler:
    """
    Gestore import/export dati da CSV.
    
    Supporta formati CSV con intestazioni per:
    - Dati geometrici sezioni
    - Proprietà materiali
    - Sollecitazioni
    - Armature
    """
    
    # Mapping intestazioni CSV standard
    INTESTAZIONI_STANDARD = {
        # Geometria
        "tipo": ["tipo", "type", "tipologia"],
        "base": ["base", "b", "width", "larghezza"],
        "altezza": ["altezza", "h", "height", "H"],
        "copriferro": ["copriferro", "c", "cover", "copr"],
        
        # Materiali
        "rck": ["rck", "Rck", "RCK", "fck", "resistenza_cls"],
        "classe_cls": ["classe_cls", "classe_calcestruzzo", "cls"],
        "tipo_acciaio": ["tipo_acciaio", "acciaio", "steel", "fyk_tipo"],
        "fyk": ["fyk", "fy", "tensione_snervamento"],
        
        # Sollecitazioni
        "momento": ["momento", "M", "momento_flettente", "Mx"],
        "momento_x": ["momento_x", "Mx", "mx"],
        "momento_y": ["momento_y", "My", "my"],
        "sforzo_normale": ["sforzo_normale", "N", "carico", "sforzo"],
        "taglio": ["taglio", "V", "T", "sforzo_taglio"],
        
        # Armatura longitudinale
        "diametro_inf": ["diametro_inf", "phi_inf", "diam_inf", "diametro_teso"],
        "numero_inf": ["numero_inf", "n_inf", "num_inf", "barre_inf"],
        "diametro_sup": ["diametro_sup", "phi_sup", "diam_sup", "diametro_compresso"],
        "numero_sup": ["numero_sup", "n_sup", "num_sup", "barre_sup"],
        
        # Armatura trasversale
        "diametro_staffe": ["diametro_staffe", "phi_st", "diam_st", "staffe_diam"],
        "passo_staffe": ["passo_staffe", "passo", "s", "interasse_staffe"],
        "bracci_staffe": ["bracci_staffe", "bracci", "n_bracci"],
        
        # Ferri piegati
        "diametro_piegati": ["diametro_piegati", "phi_pieg", "diam_pieg"],
        "numero_piegati": ["numero_piegati", "n_pieg", "num_pieg"],
        "inclinazione_piegati": ["inclinazione_piegati", "alpha", "angolo"],
    }
    
    @staticmethod
    def trova_intestazione(header: str, possibili: List[str]) -> bool:
        """
        Verifica se un'intestazione corrisponde a una delle possibili.
        
        Args:
            header: Intestazione da verificare
            possibili: Lista di possibili intestazioni
            
        Returns:
            True se corrisponde
        """
        header_lower = header.lower().strip()
        return header_lower in [p.lower() for p in possibili]
    
    @staticmethod
    def leggi_csv(
        filepath: Union[str, Path],
        encoding: str = "utf-8",
        delimiter: str = ",",
    ) -> pd.DataFrame:
        """
        Legge un file CSV e restituisce un DataFrame.
        
        Args:
            filepath: Percorso del file CSV
            encoding: Codifica del file
            delimiter: Delimitatore (default: virgola)
            
        Returns:
            DataFrame pandas con i dati
        """
        try:
            df = pd.read_csv(filepath, encoding=encoding, delimiter=delimiter)
        except UnicodeDecodeError:
            # Prova con encoding alternativo
            df = pd.read_csv(filepath, encoding="latin-1", delimiter=delimiter)
        
        # Pulisci nomi colonne
        df.columns = df.columns.str.strip()
        
        return df
    
    @staticmethod
    def mappa_colonne(df: pd.DataFrame) -> Dict[str, str]:
        """
        Mappa le colonne del DataFrame alle intestazioni standard.
        
        Args:
            df: DataFrame da mappare
            
        Returns:
            Dizionario {chiave_standard: nome_colonna_csv}
        """
        mapping = {}
        
        for chiave, possibili in CSVHandler.INTESTAZIONI_STANDARD.items():
            for col in df.columns:
                if CSVHandler.trova_intestazione(col, possibili):
                    mapping[chiave] = col
                    break
        
        return mapping
    
    @classmethod
    def importa_sezioni(
        cls,
        filepath: Union[str, Path],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Importa dati di sezioni da CSV.
        
        Args:
            filepath: Percorso file CSV
            **kwargs: Parametri aggiuntivi per read_csv
            
        Returns:
            Lista di dizionari con dati sezioni
        """
        df = cls.leggi_csv(filepath, **kwargs)
        mapping = cls.mappa_colonne(df)
        
        sezioni = []
        for _, row in df.iterrows():
            dati_sezione = {}
            
            # Geometria
            if "base" in mapping:
                dati_sezione["base"] = float(row[mapping["base"]])
            if "altezza" in mapping:
                dati_sezione["altezza"] = float(row[mapping["altezza"]])
            if "copriferro" in mapping:
                dati_sezione["copriferro"] = float(row[mapping["copriferro"]])
            
            # Materiali
            if "rck" in mapping:
                dati_sezione["rck"] = float(row[mapping["rck"]])
            elif "classe_cls" in mapping:
                dati_sezione["classe_cls"] = str(row[mapping["classe_cls"]])
            
            if "tipo_acciaio" in mapping:
                dati_sezione["tipo_acciaio"] = str(row[mapping["tipo_acciaio"]])
            elif "fyk" in mapping:
                dati_sezione["fyk"] = float(row[mapping["fyk"]])
            
            # Sollecitazioni
            if "momento" in mapping:
                dati_sezione["momento"] = float(row[mapping["momento"]])
            if "momento_x" in mapping:
                dati_sezione["momento_x"] = float(row[mapping["momento_x"]])
            if "momento_y" in mapping:
                dati_sezione["momento_y"] = float(row[mapping["momento_y"]])
            if "sforzo_normale" in mapping:
                dati_sezione["sforzo_normale"] = float(row[mapping["sforzo_normale"]])
            if "taglio" in mapping:
                dati_sezione["taglio"] = float(row[mapping["taglio"]])
            
            # Armatura longitudinale
            if "diametro_inf" in mapping:
                dati_sezione["diametro_inf"] = float(row[mapping["diametro_inf"]])
            if "numero_inf" in mapping:
                dati_sezione["numero_inf"] = int(row[mapping["numero_inf"]])
            if "diametro_sup" in mapping:
                dati_sezione["diametro_sup"] = float(row[mapping["diametro_sup"]])
            if "numero_sup" in mapping:
                dati_sezione["numero_sup"] = int(row[mapping["numero_sup"]])
            
            # Armatura trasversale
            if "diametro_staffe" in mapping:
                dati_sezione["diametro_staffe"] = float(row[mapping["diametro_staffe"]])
            if "passo_staffe" in mapping:
                dati_sezione["passo_staffe"] = float(row[mapping["passo_staffe"]])
            if "bracci_staffe" in mapping:
                dati_sezione["bracci_staffe"] = int(row[mapping["bracci_staffe"]])
            
            # Ferri piegati
            if "diametro_piegati" in mapping:
                dati_sezione["diametro_piegati"] = float(row[mapping["diametro_piegati"]])
            if "numero_piegati" in mapping:
                dati_sezione["numero_piegati"] = int(row[mapping["numero_piegati"]])
            if "inclinazione_piegati" in mapping:
                dati_sezione["inclinazione_piegati"] = float(row[mapping["inclinazione_piegati"]])
            
            # Tipo elemento
            if "tipo" in mapping:
                dati_sezione["tipo"] = str(row[mapping["tipo"]])
            
            sezioni.append(dati_sezione)
        
        return sezioni
    
    @classmethod
    def crea_sezione_da_dati(cls, dati: Dict[str, Any]) -> SezioneRettangolare:
        """
        Crea un oggetto SezioneRettangolare da dizionario dati.
        
        Args:
            dati: Dizionario con parametri sezione
            
        Returns:
            Oggetto SezioneRettangolare configurato
        """
        # Crea sezione base
        sezione = SezioneRettangolare(
            base=dati.get("base", 300),
            altezza=dati.get("altezza", 500),
            copriferro=dati.get("copriferro", 30),
        )
        
        # Aggiungi armatura inferiore
        if "diametro_inf" in dati and "numero_inf" in dati:
            sezione.aggiungi_armatura_inferiore(
                diametro=dati["diametro_inf"],
                numero_barre=dati["numero_inf"],
            )
        
        # Aggiungi armatura superiore
        if "diametro_sup" in dati and "numero_sup" in dati:
            sezione.aggiungi_armatura_superiore(
                diametro=dati["diametro_sup"],
                numero_barre=dati["numero_sup"],
            )
        
        # Aggiungi staffe
        if "diametro_staffe" in dati and "passo_staffe" in dati:
            sezione.aggiungi_staffe(
                diametro=dati["diametro_staffe"],
                passo=dati["passo_staffe"],
                numero_bracci=dati.get("bracci_staffe", 2),
            )
        
        # Aggiungi ferri piegati
        if "diametro_piegati" in dati and "numero_piegati" in dati:
            sezione.aggiungi_ferri_piegati(
                diametro=dati["diametro_piegati"],
                numero=dati["numero_piegati"],
                inclinazione=dati.get("inclinazione_piegati", 45.0),
            )
        
        return sezione
    
    @staticmethod
    def esporta_risultati(
        risultati: List[Dict[str, Any]],
        filepath: Union[str, Path],
        formato: str = "csv",
    ) -> None:
        """
        Esporta risultati delle verifiche su file.
        
        Args:
            risultati: Lista di dizionari con risultati
            filepath: Percorso file output
            formato: "csv" o "excel"
        """
        df = pd.DataFrame(risultati)
        
        if formato.lower() == "csv":
            df.to_csv(filepath, index=False, encoding="utf-8")
        elif formato.lower() in ["excel", "xlsx"]:
            df.to_excel(filepath, index=False, engine="openpyxl")
        else:
            raise ValueError(f"Formato non supportato: {formato}")
    
    @staticmethod
    def genera_template_csv(filepath: Union[str, Path], tipo: str = "trave") -> None:
        """
        Genera un file CSV template con intestazioni standard.
        
        Args:
            filepath: Percorso file output
            tipo: "trave", "pilastro", o "generico"
        """
        if tipo == "trave":
            headers = [
                "base", "altezza", "copriferro",
                "rck", "tipo_acciaio",
                "momento", "taglio",
                "diametro_inf", "numero_inf",
                "diametro_sup", "numero_sup",
                "diametro_staffe", "passo_staffe", "bracci_staffe",
            ]
            esempio = [
                300, 500, 30,
                15, "FeB32k",
                80, 50,
                16, 4,
                12, 2,
                8, 200, 2,
            ]
        elif tipo == "pilastro":
            headers = [
                "base", "altezza", "copriferro",
                "rck", "tipo_acciaio",
                "sforzo_normale", "momento_x", "momento_y",
                "diametro_inf", "numero_inf",
                "diametro_sup", "numero_sup",
                "diametro_staffe", "passo_staffe",
            ]
            esempio = [
                400, 400, 30,
                20, "FeB38k",
                200, 100, 50,
                20, 4,
                20, 4,
                10, 150,
            ]
        else:  # generico
            headers = [
                "tipo", "base", "altezza", "copriferro",
                "rck", "tipo_acciaio",
                "momento", "sforzo_normale", "taglio",
                "diametro_inf", "numero_inf",
            ]
            esempio = [
                "trave", 300, 500, 30,
                15, "FeB32k",
                80, 0, 50,
                16, 4,
            ]
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerow(esempio)
