"""
Modulo Verifica Flessione - Verifica a flessione semplice secondo Santarella.

Implementa la verifica di travi in calcestruzzo armato a flessione semplice
secondo il metodo delle tensioni ammissibili (DM 2229/1939).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np

from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.materials.acciaio import Acciaio
from verifiche_dm1939.sections.sezione_rettangolare import SezioneRettangolare


@dataclass
class RisultatoFlessione:
    """
    Risultato della verifica a flessione.
    
    Attributes:
        verificato: True se la verifica è soddisfatta
        momento_resistente: Momento resistente della sezione in kNm
        tensione_calcestruzzo: Tensione nel calcestruzzo in MPa
        tensione_acciaio: Tensione nell'acciaio in MPa
        posizione_asse_neutro: Posizione asse neutro dal lembo compresso in mm
        rapporto_sfruttamento_cls: σc / σc,amm
        rapporto_sfruttamento_acciaio: σs / σs,amm
        coefficiente_sicurezza: Coefficiente di sicurezza globale
        dettagli: Dizionario con ulteriori dettagli
    """
    
    verificato: bool
    momento_resistente: float  # kNm
    tensione_calcestruzzo: float  # MPa
    tensione_acciaio: float  # MPa
    posizione_asse_neutro: float  # mm
    rapporto_sfruttamento_cls: float
    rapporto_sfruttamento_acciaio: float
    coefficiente_sicurezza: float
    dettagli: Dict[str, Any]
    
    def genera_report_breve(self) -> str:
        """Genera un report breve del risultato."""
        stato = "✓ VERIFICATA" if self.verificato else "✗ NON VERIFICATA"
        
        return f"""
{'='*60}
VERIFICA A FLESSIONE - {stato}
{'='*60}
Momento resistente:        {self.momento_resistente:8.2f} kNm
Tensione calcestruzzo:     {self.tensione_calcestruzzo:8.2f} MPa (sfruttamento: {self.rapporto_sfruttamento_cls*100:5.1f}%)
Tensione acciaio:          {self.tensione_acciaio:8.2f} MPa (sfruttamento: {self.rapporto_sfruttamento_acciaio*100:5.1f}%)
Asse neutro:               {self.posizione_asse_neutro:8.2f} mm
Coefficiente sicurezza:    {self.coefficiente_sicurezza:8.2f}
{'='*60}
"""


class VerificaFlessione:
    """
    Verifica a flessione semplice secondo il metodo di Santarella.
    
    Implementa la verifica alle tensioni ammissibili per sezioni rettangolari
    in calcestruzzo armato soggette a flessione semplice.
    """
    
    def __init__(
        self,
        sezione: SezioneRettangolare,
        calcestruzzo: Calcestruzzo,
        acciaio: Acciaio,
        momento_flettente: float,  # kNm
    ):
        """
        Inizializza la verifica a flessione.
        
        Args:
            sezione: Sezione da verificare
            calcestruzzo: Proprietà del calcestruzzo
            acciaio: Proprietà dell'acciaio
            momento_flettente: Momento flettente di calcolo in kNm
        """
        self.sezione = sezione
        self.calcestruzzo = calcestruzzo
        self.acciaio = acciaio
        self.momento_flettente = abs(momento_flettente)  # kNm
        
        if self.sezione.area_armatura_inferiore == 0:
            raise ValueError("La sezione deve avere armatura tesa (inferiore)")
    
    def calcola_posizione_asse_neutro(self) -> float:
        """
        Calcola la posizione dell'asse neutro in regime fessurato.
        
        Returns:
            Posizione asse neutro dal lembo compresso in mm
        """
        n = self.calcestruzzo.coefficiente_omogeneizzazione
        return self.sezione.posizione_asse_neutro(n)
    
    def calcola_momento_resistente(self) -> float:
        """
        Calcola il momento resistente della sezione.
        
        Il momento resistente è il minore tra:
        - Momento resistente lato calcestruzzo
        - Momento resistente lato acciaio
        
        Returns:
            Momento resistente in kNm
        """
        b = self.sezione.base
        d = self.sezione.altezza_utile
        x = self.calcola_posizione_asse_neutro()
        
        # Momento resistente lato calcestruzzo
        sigma_c_amm = self.calcestruzzo.tensione_ammissibile_compressione
        if sigma_c_amm is None:
            raise ValueError("Tensione ammissibile calcestruzzo non definita")
        
        # M = σc * b * x * (d - x/3) secondo Santarella
        Mr_cls = sigma_c_amm * b * x * (d - x / 3.0) / 1e6  # kNm
        
        # Momento resistente lato acciaio
        sigma_s_amm = self.acciaio.tensione_ammissibile
        if sigma_s_amm is None:
            raise ValueError("Tensione ammissibile acciaio non definita")
        
        As = self.sezione.area_armatura_inferiore
        # M = σs * As * (d - x/3)
        Mr_acciaio = sigma_s_amm * As * (d - x / 3.0) / 1e6  # kNm
        
        return min(Mr_cls, Mr_acciaio)
    
    def calcola_tensioni(self) -> tuple[float, float]:
        """
        Calcola le tensioni effettive nel calcestruzzo e nell'acciaio.
        
        Returns:
            Tupla (tensione_calcestruzzo, tensione_acciaio) in MPa
        """
        M = self.momento_flettente * 1e6  # Nmm
        b = self.sezione.base
        d = self.sezione.altezza_utile
        x = self.calcola_posizione_asse_neutro()
        n = self.calcestruzzo.coefficiente_omogeneizzazione
        
        # Momento d'inerzia sezione fessurata
        I = self.sezione.momento_inerzia_fessurato(n)
        
        # Tensione nel calcestruzzo al lembo compresso
        sigma_c = M * x / I
        
        # Tensione nell'acciaio
        sigma_s = n * M * (d - x) / I
        
        return sigma_c, sigma_s
    
    def verifica(self) -> RisultatoFlessione:
        """
        Esegue la verifica a flessione.
        
        Returns:
            Risultato della verifica
        """
        # Calcola momento resistente
        Mr = self.calcola_momento_resistente()
        
        # Calcola tensioni effettive
        sigma_c, sigma_s = self.calcola_tensioni()
        
        # Tensioni ammissibili
        sigma_c_amm = self.calcestruzzo.tensione_ammissibile_compressione
        sigma_s_amm = self.acciaio.tensione_ammissibile
        
        if sigma_c_amm is None or sigma_s_amm is None:
            raise ValueError("Tensioni ammissibili non definite")
        
        # Rapporti di sfruttamento
        rapporto_cls = sigma_c / sigma_c_amm
        rapporto_acciaio = sigma_s / sigma_s_amm
        
        # Verifica soddisfatta se M ≤ Mr
        verificato = self.momento_flettente <= Mr
        
        # Coefficiente di sicurezza
        coeff_sicurezza = Mr / self.momento_flettente if self.momento_flettente > 0 else np.inf
        
        # Posizione asse neutro
        x = self.calcola_posizione_asse_neutro()
        
        # Dettagli aggiuntivi
        dettagli = {
            "momento_sollecitante": self.momento_flettente,
            "momento_resistente_cls": sigma_c_amm * self.sezione.base * x * 
                                      (self.sezione.altezza_utile - x/3.0) / 1e6,
            "momento_resistente_acciaio": sigma_s_amm * self.sezione.area_armatura_inferiore * 
                                          (self.sezione.altezza_utile - x/3.0) / 1e6,
            "altezza_utile": self.sezione.altezza_utile,
            "area_armatura": self.sezione.area_armatura_inferiore,
            "percentuale_armatura": self.sezione.percentuale_armatura_meccanica,
        }
        
        return RisultatoFlessione(
            verificato=verificato,
            momento_resistente=Mr,
            tensione_calcestruzzo=sigma_c,
            tensione_acciaio=sigma_s,
            posizione_asse_neutro=x,
            rapporto_sfruttamento_cls=rapporto_cls,
            rapporto_sfruttamento_acciaio=rapporto_acciaio,
            coefficiente_sicurezza=coeff_sicurezza,
            dettagli=dettagli,
        )
    
    def dimensiona_armatura(self, target_sfruttamento: float = 0.95) -> float:
        """
        Dimensiona l'armatura necessaria per un dato momento.
        
        Args:
            target_sfruttamento: Sfruttamento target dell'acciaio (0-1)
            
        Returns:
            Area armatura necessaria in mm²
        """
        M = self.momento_flettente * 1e6  # Nmm
        d = self.sezione.altezza_utile
        
        # Ipotesi: asse neutro a x = d/3 (valore tipico)
        x_ipotesi = d / 3.0
        
        sigma_s_amm = self.acciaio.tensione_ammissibile
        if sigma_s_amm is None:
            raise ValueError("Tensione ammissibile acciaio non definita")
        
        # Area necessaria
        As_necessaria = M / (target_sfruttamento * sigma_s_amm * (d - x_ipotesi / 3.0))
        
        return As_necessaria
