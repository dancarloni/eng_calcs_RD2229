"""
Modulo di configurazione globale del software.

Gestisce il caricamento e la validazione delle configurazioni da file YAML/JSON.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
import json
from enum import Enum


class MetodoCalcolo(str, Enum):
    """Metodi di calcolo supportati."""
    
    SANTARELLA = "santarella"
    GIANGRECO = "giangreco"


class FormatoOutput(str, Enum):
    """Formati di output supportati."""
    
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    MARKDOWN = "markdown"


@dataclass
class MaterialeConfig:
    """Configurazione materiale."""
    
    calcola_auto: bool = True
    """Se True, calcola automaticamente i parametri; se False usa valori manuali."""
    
    parametri: Dict[str, float] = field(default_factory=dict)
    """Parametri specifici del materiale."""


@dataclass
class CalcestruzzoConfig(MaterialeConfig):
    """Configurazione calcestruzzo."""
    
    rck: float = 15.0  # MPa
    tensione_ammissibile_compressione: Optional[float] = None  # MPa
    tensione_ammissibile_taglio: Optional[float] = None  # MPa
    coefficiente_omogeneizzazione: int = 15
    
    def __post_init__(self) -> None:
        """Calcola tensioni ammissibili se necessario."""
        if self.calcola_auto:
            # Secondo DM 2229/1939
            self.tensione_ammissibile_compressione = self.rck / 3.0
            # Tensione tangenziale ammissibile secondo Santarella
            self.tensione_ammissibile_taglio = 0.054 * self.rck


@dataclass
class AcciaioConfig(MaterialeConfig):
    """Configurazione acciaio."""
    
    tipo: str = "FeB32k"
    tensione_snervamento: float = 320.0  # MPa (Fe B 32k)
    tensione_ammissibile: Optional[float] = None  # MPa
    modulo_elastico: float = 206000.0  # MPa
    
    def __post_init__(self) -> None:
        """Calcola tensione ammissibile se necessario."""
        if self.calcola_auto and self.tensione_ammissibile is None:
            # Tensione ammissibile = fyk / 1.8 per FeB32k secondo normativa
            self.tensione_ammissibile = self.tensione_snervamento / 2.3


@dataclass
class SezioneConfig:
    """Configurazione sezione."""
    
    tipo: str = "rettangolare"
    base: float = 300.0  # mm
    altezza: float = 500.0  # mm
    copriferro: float = 30.0  # mm


@dataclass
class ArmaturaConfig:
    """Configurazione armatura."""
    
    longitudinale: Dict[str, Any] = field(default_factory=dict)
    trasversale: Dict[str, Any] = field(default_factory=dict)
    ferri_piegati: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SollecitazioniConfig:
    """Configurazione sollecitazioni."""
    
    momento_flettente: float = 0.0  # kNm
    sforzo_normale: float = 0.0  # kN (positivo = compressione)
    taglio: float = 0.0  # kN


@dataclass
class OpzioniCalcoloConfig:
    """Opzioni di calcolo."""
    
    metodo: MetodoCalcolo = MetodoCalcolo.SANTARELLA
    genera_grafici: bool = True
    formato_output: FormatoOutput = FormatoOutput.PDF
    decimali: int = 3
    unita_misura: str = "SI"  # SI o TECH


@dataclass
class Config:
    """
    Configurazione globale del software.
    
    Attributes:
        materiali: Configurazioni materiali
        sezione: Configurazione sezione
        armatura: Configurazione armatura
        sollecitazioni: Sollecitazioni applicate
        opzioni_calcolo: Opzioni di calcolo
    """
    
    calcestruzzo: CalcestruzzoConfig = field(default_factory=CalcestruzzoConfig)
    acciaio: AcciaioConfig = field(default_factory=AcciaioConfig)
    sezione: SezioneConfig = field(default_factory=SezioneConfig)
    armatura: ArmaturaConfig = field(default_factory=ArmaturaConfig)
    sollecitazioni: SollecitazioniConfig = field(default_factory=SollecitazioniConfig)
    opzioni_calcolo: OpzioniCalcoloConfig = field(default_factory=OpzioniCalcoloConfig)
    
    @classmethod
    def from_yaml(cls, filepath: Union[str, Path]) -> "Config":
        """
        Carica configurazione da file YAML.
        
        Args:
            filepath: Percorso del file YAML
            
        Returns:
            Oggetto Config
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)
    
    @classmethod
    def from_json(cls, filepath: Union[str, Path]) -> "Config":
        """
        Carica configurazione da file JSON.
        
        Args:
            filepath: Percorso del file JSON
            
        Returns:
            Oggetto Config
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """
        Crea configurazione da dizionario.
        
        Args:
            data: Dizionario con i dati di configurazione
            
        Returns:
            Oggetto Config
        """
        calcestruzzo_data = data.get("materiali", {}).get("calcestruzzo", {})
        acciaio_data = data.get("materiali", {}).get("acciaio", {})
        
        return cls(
            calcestruzzo=CalcestruzzoConfig(**calcestruzzo_data),
            acciaio=AcciaioConfig(**acciaio_data),
            sezione=SezioneConfig(**data.get("sezione", {})),
            armatura=ArmaturaConfig(**data.get("armatura", {})),
            sollecitazioni=SollecitazioniConfig(**data.get("sollecitazioni", {})),
            opzioni_calcolo=OpzioniCalcoloConfig(
                **{k: v for k, v in data.get("opzioni_calcolo", {}).items() 
                   if k in OpzioniCalcoloConfig.__annotations__}
            ),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte configurazione in dizionario.
        
        Returns:
            Dizionario con i dati di configurazione
        """
        return {
            "materiali": {
                "calcestruzzo": self.calcestruzzo.__dict__,
                "acciaio": self.acciaio.__dict__,
            },
            "sezione": self.sezione.__dict__,
            "armatura": self.armatura.__dict__,
            "sollecitazioni": self.sollecitazioni.__dict__,
            "opzioni_calcolo": {
                "metodo": self.opzioni_calcolo.metodo.value,
                "genera_grafici": self.opzioni_calcolo.genera_grafici,
                "formato_output": self.opzioni_calcolo.formato_output.value,
                "decimali": self.opzioni_calcolo.decimali,
                "unita_misura": self.opzioni_calcolo.unita_misura,
            },
        }
    
    def save_yaml(self, filepath: Union[str, Path]) -> None:
        """
        Salva configurazione su file YAML.
        
        Args:
            filepath: Percorso del file YAML
        """
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
    
    def save_json(self, filepath: Union[str, Path]) -> None:
        """
        Salva configurazione su file JSON.
        
        Args:
            filepath: Percorso del file JSON
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
