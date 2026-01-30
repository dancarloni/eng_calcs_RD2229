"""
Modulo Acciaio - Proprietà e tipi di acciaio secondo DM 2229/1939.

Implementa le proprietà dell'acciaio da armatura e i metodi di calcolo
delle tensioni ammissibili secondo la normativa dell'epoca.
"""

from dataclasses import dataclass
from typing import Optional, Dict
from enum import Enum


class TipoAcciaio(str, Enum):
    """Tipi di acciaio da armatura secondo normativa epoca."""
    
    FEB24K = "FeB24k"  # Ferro B 24 kg/mm² (235 MPa)
    FEB32K = "FeB32k"  # Ferro B 32 kg/mm² (320 MPa)
    FEB38K = "FeB38k"  # Ferro B 38 kg/mm² (375 MPa)
    FEB44K = "FeB44k"  # Ferro B 44 kg/mm² (430 MPa)
    LISCIO = "Liscio"  # Acciaio liscio
    TONDO = "Tondo"    # Tondo liscio


@dataclass
class Acciaio:
    """
    Classe per la gestione delle proprietà dell'acciaio da armatura.
    
    Implementa le caratteristiche meccaniche e le tensioni ammissibili
    secondo il DM 2229/1939.
    
    Attributes:
        tipo: Tipo di acciaio (FeB24k, FeB32k, FeB38k, FeB44k)
        tensione_snervamento: fyk in MPa
        tensione_ammissibile: σs,amm in MPa
        modulo_elastico: Es in MPa (tipicamente 206000 MPa)
        aderenza_migliorata: True per ferri ad aderenza migliorata
        calcola_auto: Se True calcola automaticamente i parametri
    """
    
    tipo: str  # Tipo di acciaio
    tensione_snervamento: float  # fyk [MPa]
    tensione_ammissibile: Optional[float] = None  # σs,amm [MPa]
    modulo_elastico: float = 206000.0  # Es [MPa]
    aderenza_migliorata: bool = False
    calcola_auto: bool = True
    
    def __post_init__(self) -> None:
        """Inizializza e calcola i parametri se necessario."""
        if self.calcola_auto:
            self._calcola_parametri()
        self._valida_parametri()
    
    def _calcola_parametri(self) -> None:
        """
        Calcola automaticamente i parametri dell'acciaio.
        
        Secondo DM 2229/1939:
        - Per acciai dolci (FeB24k, FeB32k): σs,amm = fyk / 2.3
        - Per acciai duri (FeB38k, FeB44k): σs,amm = fyk / 2.5
        """
        if self.tensione_ammissibile is None:
            # Coefficiente di sicurezza secondo normativa epoca
            if self.tipo in ["FeB24k", "FeB32k", "Liscio", "Tondo"]:
                coefficiente_sicurezza = 2.3
            else:  # FeB38k, FeB44k
                coefficiente_sicurezza = 2.5
            
            self.tensione_ammissibile = self.tensione_snervamento / coefficiente_sicurezza
    
    def _valida_parametri(self) -> None:
        """Valida i parametri dell'acciaio."""
        if self.tensione_snervamento <= 0:
            raise ValueError("La tensione di snervamento deve essere positiva")
        
        if self.tensione_ammissibile is not None:
            if self.tensione_ammissibile > self.tensione_snervamento:
                raise ValueError(
                    "La tensione ammissibile non può superare la tensione di snervamento"
                )
        
        if self.modulo_elastico <= 0:
            raise ValueError("Il modulo elastico deve essere positivo")
    
    @classmethod
    def da_tipo(cls, tipo: str, calcola_auto: bool = True) -> "Acciaio":
        """
        Crea un acciaio da tipo standard.
        
        Args:
            tipo: Tipo di acciaio (es: "FeB32k", "FeB38k")
            calcola_auto: Se True calcola automaticamente i parametri
            
        Returns:
            Oggetto Acciaio
            
        Example:
            >>> acc = Acciaio.da_tipo("FeB32k")
            >>> acc.tensione_snervamento
            320.0
        """
        if tipo not in ACCIAI_TIPICI:
            raise ValueError(f"Tipo di acciaio non riconosciuto: {tipo}")
        
        dati = ACCIAI_TIPICI[tipo]
        return cls(
            tipo=tipo,
            tensione_snervamento=dati["fyk"],
            aderenza_migliorata=dati.get("aderenza_migliorata", False),
            calcola_auto=calcola_auto,
        )
    
    def tensione_aderenza_ammissibile(self, diametro: float) -> float:
        """
        Calcola la tensione di aderenza ammissibile.
        
        Secondo Santarella, la tensione di aderenza dipende dal tipo di acciaio
        e dal diametro della barra.
        
        Args:
            diametro: Diametro barra in mm
            
        Returns:
            Tensione di aderenza in MPa
        """
        if self.aderenza_migliorata:
            # Acciaio ad aderenza migliorata
            tau_adm_base = 1.5  # MPa
        else:
            # Acciaio liscio
            tau_adm_base = 0.5  # MPa
        
        # Riduzione per diametri maggiori
        if diametro > 20:
            fattore_riduzione = 20.0 / diametro
            return tau_adm_base * fattore_riduzione
        
        return tau_adm_base
    
    def lunghezza_ancoraggio_base(self, diametro: float) -> float:
        """
        Calcola la lunghezza di ancoraggio di base.
        
        Args:
            diametro: Diametro barra in mm
            
        Returns:
            Lunghezza di ancoraggio in mm
        """
        if self.tensione_ammissibile is None:
            raise ValueError("Tensione ammissibile non definita")
        
        tau_adm = self.tensione_aderenza_ammissibile(diametro)
        
        # Lunghezza ancoraggio: Lb = (σs,amm * φ) / (4 * τadm)
        lunghezza = (self.tensione_ammissibile * diametro) / (4.0 * tau_adm)
        
        # Lunghezza minima: 20 diametri
        lunghezza_minima = 20 * diametro
        
        return max(lunghezza, lunghezza_minima)
    
    def to_dict(self) -> dict:
        """Converte l'oggetto in dizionario."""
        return {
            "tipo": self.tipo,
            "tensione_snervamento": self.tensione_snervamento,
            "tensione_ammissibile": self.tensione_ammissibile,
            "modulo_elastico": self.modulo_elastico,
            "aderenza_migliorata": self.aderenza_migliorata,
        }
    
    def __repr__(self) -> str:
        """Rappresentazione stringa dell'oggetto."""
        return (
            f"Acciaio({self.tipo}, "
            f"fyk={self.tensione_snervamento} MPa, "
            f"σs,amm={self.tensione_ammissibile:.1f} MPa)"
        )


# Database acciai tipici dell'epoca
ACCIAI_TIPICI: Dict[str, Dict] = {
    "FeB24k": {
        "fyk": 235.0,  # MPa (24 kg/mm² × 9.81)
        "aderenza_migliorata": False,
        "descrizione": "Ferro B 24 kg/mm² - Acciaio dolce liscio",
    },
    "FeB32k": {
        "fyk": 320.0,  # MPa (32 kg/mm² × 10)
        "aderenza_migliorata": False,
        "descrizione": "Ferro B 32 kg/mm² - Acciaio dolce",
    },
    "FeB38k": {
        "fyk": 375.0,  # MPa (38 kg/mm² × ~10)
        "aderenza_migliorata": True,
        "descrizione": "Ferro B 38 kg/mm² - Acciaio ad aderenza migliorata",
    },
    "FeB44k": {
        "fyk": 430.0,  # MPa (44 kg/mm² × ~10)
        "aderenza_migliorata": True,
        "descrizione": "Ferro B 44 kg/mm² - Acciaio ad alta resistenza",
    },
    "Liscio": {
        "fyk": 235.0,  # MPa
        "aderenza_migliorata": False,
        "descrizione": "Tondo liscio generico",
    },
    "Tondo": {
        "fyk": 235.0,  # MPa
        "aderenza_migliorata": False,
        "descrizione": "Tondo liscio",
    },
}
