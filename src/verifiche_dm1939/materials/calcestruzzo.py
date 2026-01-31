"""
Modulo Calcestruzzo - Proprietà e verifiche secondo DM 2229/1939.

Implementa le proprietà del calcestruzzo e i metodi di calcolo
delle tensioni ammissibili secondo la normativa dell'epoca.

Fonte: Regio Decreto 2229 del 1939 e prontuari dell'Ing. Santarella.
Tabelle da scansioni storiche RD 2229 (1939).
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np

from verifiche_dm1939.core.dati_storici_rd2229 import (
    modulo_elasticita_calcestruzzo_mpa,
    CarichUnitariSicurezza,
    interpola_resistenza_calcestruzzo,
    MODULO_ELASTICITA_ACCIAIO_MPA,
)


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
        da_tabella_storica: Se True usa formule da tabelle RD 2229
        tipo_cemento: "normale", "alta_resistenza", "alluminoso"
        rapporto_ac: Rapporto acqua/cemento (per calcoli dalla tabella storica)
    """
    
    resistenza_caratteristica: float  # Rck [MPa]
    tensione_ammissibile_compressione: Optional[float] = None  # σc,amm [MPa]
    tensione_ammissibile_taglio: Optional[float] = None  # τc,amm [MPa]
    coefficiente_omogeneizzazione: Optional[float] = None  # n = Es/Ec
    modulo_elastico: Optional[float] = None  # Ec [MPa]
    calcola_auto: bool = True
    da_tabella_storica: bool = False  # Se True usa formule RD 2229 1939
    tipo_cemento: str = "normale"  # "normale", "alta_resistenza", "alluminoso"
    rapporto_ac: Optional[float] = None  # A/C per ricerche in tabella storica
    
    def __post_init__(self) -> None:
        """Inizializza e calcola i parametri se necessario."""
        if self.calcola_auto:
            if self.da_tabella_storica:
                self._calcola_parametri_storici()
            else:
                self._calcola_parametri()
        self._valida_parametri()
    
    def _calcola_parametri_storici(self) -> None:
        """
        Calcola parametri usando formule storiche RD 2229/1939.
        
        Secondo tabelle e prontuari dell'Ing. Santarella:
        - Modulo elastico: Ec = 550000·σc/(σc+200) in Kg/cm²
        - Coefficiente omogeneizzazione: n = Es/Ec (Es=2.000.000 Kg/cm²)
        - Tensione ammissibile compressione: da carico unitario sicurezza
        - Tensione ammissibile taglio: 4 Kg/cm² (normale), 6 (alta resistenza)
        """
        from verifiche_dm1939.core.conversioni_unita import kgcm2_to_mpa, mpa_to_kgcm2
        
        # Converto Rck MPa → Kg/cm² per formule storiche
        rck_kgcm2 = mpa_to_kgcm2(self.resistenza_caratteristica)
        
        # Modulo elastico secondo formula storica
        if self.modulo_elastico is None:
            ec_kgcm2 = modulo_elasticita_calcestruzzo_mpa(self.resistenza_caratteristica)
            self.modulo_elastico = ec_kgcm2
        
        # Coefficiente omogeneizzazione
        if self.coefficiente_omogeneizzazione is None:
            ec_kgcm2 = mpa_to_kgcm2(self.modulo_elastico)
            self.coefficiente_omogeneizzazione = MODULO_ELASTICITA_ACCIAIO_MPA / (self.modulo_elastico or 30000)
        
        # Tensione ammissibile compressione (se non fornita)
        if self.tensione_ammissibile_compressione is None:
            # Usa carico unitario sicurezza da RD 2229
            if self.tipo_cemento == "alta_resistenza":
                sigma_c_amm_kgcm2 = CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_ALT
            else:
                sigma_c_amm_kgcm2 = CarichUnitariSicurezza.SIGMA_C_COMPRESSIONE_INFLESSA_NORM
            self.tensione_ammissibile_compressione = kgcm2_to_mpa(sigma_c_amm_kgcm2)
        
        # Tensione ammissibile taglio
        if self.tensione_ammissibile_taglio is None:
            if self.tipo_cemento in ("alta_resistenza", "alluminoso"):
                tau_c_amm_kgcm2 = CarichUnitariSicurezza.TAU_TAGLIO_ALTA_RESISTENZA
            else:
                tau_c_amm_kgcm2 = CarichUnitariSicurezza.TAU_TAGLIO_NORMALE
            self.tensione_ammissibile_taglio = kgcm2_to_mpa(tau_c_amm_kgcm2)
    
    def _calcola_parametri(self) -> None:
        """
        Calcola automaticamente i parametri del calcestruzzo (metodo moderno).
        
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
        
        # Coefficiente omogeneizzazione (se non fornito)
        if self.coefficiente_omogeneizzazione is None:
            # n = Es / Ec, con Es = 200000 MPa, Ec calcolato
            self.coefficiente_omogeneizzazione = 200000 / self.modulo_elastico
    
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
    
    @classmethod
    def da_tabella_storica(
        cls,
        resistenza_compressione_kgcm2: float,
        tipo_cemento: str = "normale",
        rapporto_ac: Optional[float] = None
    ) -> "Calcestruzzo":
        """
        Crea un calcestruzzo da dati storici RD 2229/1939.
        
        Usa le formule e tabelle dal prontuario storico dell'Ing. Santarella.
        
        Args:
            resistenza_compressione_kgcm2: Resistenza a compressione in Kg/cm²
            tipo_cemento: "normale", "alta_resistenza", "alluminoso"
            rapporto_ac: Rapporto A/C (opzionale, per tracciabilità)
        
        Returns:
            Oggetto Calcestruzzo con parametri da tabella storica
            
        Example:
            >>> cls = Calcestruzzo.da_tabella_storica(resistenza_compressione_kgcm2=280)
            >>> cls.modulo_elastico  # Calcolato da formula storica
        """
        from verifiche_dm1939.core.conversioni_unita import kgcm2_to_mpa
        
        rck_mpa = kgcm2_to_mpa(resistenza_compressione_kgcm2)
        
        return cls(
            resistenza_caratteristica=rck_mpa,
            da_tabella_storica=True,
            tipo_cemento=tipo_cemento,
            rapporto_ac=rapporto_ac,
            calcola_auto=True
        )
    
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
