"""
Modulo Calcestruzzo - Proprietà e verifiche secondo DM 2229/1939.

Implementa le proprietà del calcestruzzo e i metodi di calcolo
delle tensioni ammissibili secondo la normativa dell'epoca.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class Calcestruzzo:
    """
    Classe per la gestione delle proprietà del calcestruzzo.
    
    Implementa le caratteristiche meccaniche e le tensioni ammissibili
    secondo il DM 2229/1939.
    
    Attributes:
        resistenza_caratteristica: Rck in MPa (es: 15, 20, 25, 30 MPa)
        tensione_ammissibile_compressione: σc,amm in MPa
        tensione_ammissibile_taglio: τc,amm in MPa
        coefficiente_omogeneizzazione: n (rapporto Es/Ec)
        modulo_elastico: Ec in MPa
        calcola_auto: Se True calcola automaticamente i parametri
    """
    
    resistenza_caratteristica: float  # Rck [MPa]
    tensione_ammissibile_compressione: Optional[float] = None  # σc,amm [MPa]
    tensione_ammissibile_taglio: Optional[float] = None  # τc,amm [MPa]
    coefficiente_omogeneizzazione: int = 15  # n = Es/Ec
    modulo_elastico: Optional[float] = None  # Ec [MPa]
    calcola_auto: bool = True
    
    def __post_init__(self) -> None:
        """Inizializza e calcola i parametri se necessario."""
        if self.calcola_auto:
            self._calcola_parametri()
        self._valida_parametri()
    
    def _calcola_parametri(self) -> None:
        """
        Calcola automaticamente i parametri del calcestruzzo.
        
        Secondo DM 2229/1939 e teoria di Santarella:
        - Tensione ammissibile compressione: σc,amm = Rck / 3
        - Tensione ammissibile taglio: τc,amm = 0.054 * Rck
        - Modulo elastico: formula empirica Ec = 5700 * sqrt(Rck) [MPa]
        """
        # Tensione ammissibile a compressione secondo DM 2229/1939
        if self.tensione_ammissibile_compressione is None:
            self.tensione_ammissibile_compressione = self.resistenza_caratteristica / 3.0
        
        # Tensione tangenziale ammissibile secondo Santarella
        if self.tensione_ammissibile_taglio is None:
            # Formula empirica: τc,amm = 0.054 * Rck
            self.tensione_ammissibile_taglio = 0.054 * self.resistenza_caratteristica
        
        # Modulo elastico secondo formula empirica dell'epoca
        if self.modulo_elastico is None:
            # Ec = 5700 * sqrt(Rck) [MPa] per Rck in MPa
            self.modulo_elastico = 5700.0 * np.sqrt(self.resistenza_caratteristica)
    
    def _valida_parametri(self) -> None:
        """Valida i parametri del calcestruzzo."""
        if self.resistenza_caratteristica <= 0:
            raise ValueError("La resistenza caratteristica deve essere positiva")
        
        if self.resistenza_caratteristica < 10 or self.resistenza_caratteristica > 50:
            import warnings
            warnings.warn(
                f"Rck = {self.resistenza_caratteristica} MPa fuori dal range tipico "
                f"per calcestruzzi dell'epoca (10-30 MPa)"
            )
        
        if self.tensione_ammissibile_compressione is not None:
            if self.tensione_ammissibile_compressione > self.resistenza_caratteristica:
                raise ValueError(
                    "La tensione ammissibile non può superare la resistenza caratteristica"
                )
        
        if self.coefficiente_omogeneizzazione <= 0:
            raise ValueError("Il coefficiente di omogeneizzazione deve essere positivo")
    
    @classmethod
    def da_classe(cls, classe: str, calcola_auto: bool = True) -> "Calcestruzzo":
        """
        Crea un calcestruzzo da classe di resistenza.
        
        Args:
            classe: Classe calcestruzzo (es: "Rck15", "Rck20", "Rck25")
            calcola_auto: Se True calcola automaticamente i parametri
            
        Returns:
            Oggetto Calcestruzzo
            
        Example:
            >>> cls = Calcestruzzo.da_classe("Rck15")
            >>> cls.resistenza_caratteristica
            15.0
        """
        # Estrai il valore numerico dalla classe
        rck_str = classe.replace("Rck", "").replace("rck", "").replace("RCK", "")
        try:
            rck = float(rck_str)
        except ValueError:
            raise ValueError(f"Classe calcestruzzo non valida: {classe}")
        
        return cls(resistenza_caratteristica=rck, calcola_auto=calcola_auto)
    
    def coefficiente_riduzione_taglio(self, percentuale_armatura: float) -> float:
        """
        Calcola il coefficiente di riduzione per il taglio.
        
        Secondo Santarella, la resistenza a taglio del calcestruzzo
        può essere incrementata in presenza di armatura longitudinale.
        
        Args:
            percentuale_armatura: Percentuale di armatura longitudinale (ρ%)
            
        Returns:
            Coefficiente moltiplicativo (tipicamente 1.0-1.3)
        """
        # Formula empirica secondo Santarella
        if percentuale_armatura < 0.5:
            return 1.0
        elif percentuale_armatura <= 1.5:
            return 1.0 + 0.2 * (percentuale_armatura - 0.5)
        else:
            return 1.2
    
    def tensione_ammissibile_flessione(self) -> float:
        """
        Restituisce la tensione ammissibile per la flessione.
        
        Per la flessione si usa la tensione ammissibile a compressione.
        
        Returns:
            Tensione ammissibile in MPa
        """
        if self.tensione_ammissibile_compressione is None:
            raise ValueError("Tensione ammissibile compressione non definita")
        return self.tensione_ammissibile_compressione
    
    def to_dict(self) -> dict:
        """Converte l'oggetto in dizionario."""
        return {
            "resistenza_caratteristica": self.resistenza_caratteristica,
            "tensione_ammissibile_compressione": self.tensione_ammissibile_compressione,
            "tensione_ammissibile_taglio": self.tensione_ammissibile_taglio,
            "coefficiente_omogeneizzazione": self.coefficiente_omogeneizzazione,
            "modulo_elastico": self.modulo_elastico,
        }
    
    def __repr__(self) -> str:
        """Rappresentazione stringa dell'oggetto."""
        return (
            f"Calcestruzzo(Rck={self.resistenza_caratteristica} MPa, "
            f"σc,amm={self.tensione_ammissibile_compressione:.2f} MPa, "
            f"τc,amm={self.tensione_ammissibile_taglio:.3f} MPa)"
        )


# Database calcestruzzi tipici dell'epoca
CALCESTRUZZI_TIPICI = {
    "Rck10": Calcestruzzo(resistenza_caratteristica=10.0),
    "Rck15": Calcestruzzo(resistenza_caratteristica=15.0),
    "Rck20": Calcestruzzo(resistenza_caratteristica=20.0),
    "Rck25": Calcestruzzo(resistenza_caratteristica=25.0),
    "Rck30": Calcestruzzo(resistenza_caratteristica=30.0),
}
