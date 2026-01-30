"""
Modulo Verifica Taglio - Verifica a taglio con staffe e ferri piegati.

Implementa la verifica a taglio secondo il DM 2229/1939 e le teorie
di Santarella e Giangreco.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np

from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.materials.acciaio import Acciaio
from verifiche_dm1939.sections.sezione_rettangolare import SezioneRettangolare


@dataclass
class RisultatoTaglio:
    """
    Risultato della verifica a taglio.
    
    Attributes:
        verificato: True se la verifica è soddisfatta
        taglio_resistente: Taglio resistente in kN
        contributo_calcestruzzo: Contributo del calcestruzzo in kN
        contributo_staffe: Contributo delle staffe in kN
        contributo_ferri_piegati: Contributo dei ferri piegati in kN
        tensione_tangenziale: Tensione tangenziale media in MPa
        rapporto_sfruttamento: V / Vr
        coefficiente_sicurezza: Vr / V
        dettagli: Dizionario con ulteriori dettagli
    """
    
    verificato: bool
    taglio_resistente: float  # kN
    contributo_calcestruzzo: float  # kN
    contributo_staffe: float  # kN
    contributo_ferri_piegati: float  # kN
    tensione_tangenziale: float  # MPa
    rapporto_sfruttamento: float
    coefficiente_sicurezza: float
    dettagli: Dict[str, Any]
    
    def genera_report_breve(self) -> str:
        """Genera un report breve del risultato."""
        stato = "✓ VERIFICATA" if self.verificato else "✗ NON VERIFICATA"
        
        return f"""
{'='*60}
VERIFICA A TAGLIO - {stato}
{'='*60}
Taglio resistente:         {self.taglio_resistente:8.2f} kN
  - Calcestruzzo:          {self.contributo_calcestruzzo:8.2f} kN
  - Staffe:                {self.contributo_staffe:8.2f} kN
  - Ferri piegati:         {self.contributo_ferri_piegati:8.2f} kN
Tensione tangenziale:      {self.tensione_tangenziale:8.3f} MPa
Sfruttamento:              {self.rapporto_sfruttamento*100:8.1f}%
Coefficiente sicurezza:    {self.coefficiente_sicurezza:8.2f}
{'='*60}
"""


class VerificaTaglio:
    """
    Verifica a taglio secondo Santarella e Giangreco.
    
    Implementa la verifica considerando:
    - Resistenza del calcestruzzo
    - Contributo delle staffe
    - Contributo dei ferri piegati
    """
    
    def __init__(
        self,
        sezione: SezioneRettangolare,
        calcestruzzo: Calcestruzzo,
        acciaio: Acciaio,
        taglio: float,  # kN
        considera_calcestruzzo: bool = True,
        metodo: str = "santarella",
    ):
        """
        Inizializza la verifica a taglio.
        
        Args:
            sezione: Sezione da verificare
            calcestruzzo: Proprietà del calcestruzzo
            acciaio: Proprietà dell'acciaio
            taglio: Taglio sollecitante in kN
            considera_calcestruzzo: Se True include il contributo del cls
            metodo: "santarella" o "giangreco"
        """
        self.sezione = sezione
        self.calcestruzzo = calcestruzzo
        self.acciaio = acciaio
        self.taglio = abs(taglio)
        self.considera_calcestruzzo = considera_calcestruzzo
        self.metodo = metodo.lower()
    
    def calcola_tensione_tangenziale_media(self) -> float:
        """
        Calcola la tensione tangenziale media.
        
        Returns:
            Tensione tangenziale in MPa
        """
        V = self.taglio * 1000  # N
        b = self.sezione.base  # mm
        d = self.sezione.altezza_utile  # mm
        
        # τ = V / (b * d)
        tau = V / (b * d)
        
        return tau
    
    def calcola_contributo_calcestruzzo(self) -> float:
        """
        Calcola il contributo del calcestruzzo alla resistenza a taglio.
        
        Secondo Santarella, il calcestruzzo può resistere a una tensione
        tangenziale ammissibile che dipende dalla resistenza caratteristica.
        
        Returns:
            Contributo in kN
        """
        if not self.considera_calcestruzzo:
            return 0.0
        
        tau_c_amm = self.calcestruzzo.tensione_ammissibile_taglio
        if tau_c_amm is None:
            raise ValueError("Tensione ammissibile taglio calcestruzzo non definita")
        
        b = self.sezione.base
        d = self.sezione.altezza_utile
        
        # Fattore di incremento in funzione della percentuale di armatura
        percentuale_arm = self.sezione.percentuale_armatura_meccanica
        fattore = self.calcestruzzo.coefficiente_riduzione_taglio(percentuale_arm)
        
        # Vc = τc,amm * b * d * fattore
        Vc = tau_c_amm * b * d * fattore / 1000  # kN
        
        return Vc
    
    def calcola_contributo_staffe(self) -> float:
        """
        Calcola il contributo delle staffe alla resistenza a taglio.
        
        Secondo DM 2229/1939:
        Vs = (Asw / s) * σs,amm * d
        
        Returns:
            Contributo in kN
        """
        if self.sezione.staffe is None:
            return 0.0
        
        Asw = self.sezione.staffe.area_totale  # mm² (area totale bracci)
        s = self.sezione.staffe.passo  # mm
        d = self.sezione.altezza_utile  # mm
        
        sigma_s_amm = self.acciaio.tensione_ammissibile
        if sigma_s_amm is None:
            raise ValueError("Tensione ammissibile acciaio non definita")
        
        # Vs = (Asw / s) * σs,amm * d
        Vs = (Asw / s) * sigma_s_amm * d / 1000  # kN
        
        return Vs
    
    def calcola_contributo_ferri_piegati(self) -> float:
        """
        Calcola il contributo dei ferri piegati alla resistenza a taglio.
        
        Secondo Santarella:
        Vf = Asf * σs,amm * sin(α)
        
        Returns:
            Contributo in kN
        """
        if self.sezione.ferri_piegati is None:
            return 0.0
        
        Asf = self.sezione.ferri_piegati.area_totale  # mm²
        alpha = np.radians(self.sezione.ferri_piegati.inclinazione)  # radianti
        
        sigma_s_amm = self.acciaio.tensione_ammissibile
        if sigma_s_amm is None:
            raise ValueError("Tensione ammissibile acciaio non definita")
        
        # Vf = Asf * σs,amm * sin(α)
        Vf = Asf * sigma_s_amm * np.sin(alpha) / 1000  # kN
        
        return Vf
    
    def calcola_taglio_resistente(self) -> tuple[float, float, float, float]:
        """
        Calcola il taglio resistente totale.
        
        Returns:
            Tupla (Vr_totale, Vc, Vs, Vf) in kN
        """
        Vc = self.calcola_contributo_calcestruzzo()
        Vs = self.calcola_contributo_staffe()
        Vf = self.calcola_contributo_ferri_piegati()
        
        if self.metodo == "santarella":
            # Santarella: Vr = Vc + Vs + Vf (somma contributi)
            Vr = Vc + Vs + Vf
        elif self.metodo == "giangreco":
            # Giangreco: approccio più conservativo
            # Vr = min(Vc + Vs, Vc + Vf, Vs + Vf)
            Vr = max(Vc + Vs, Vc + Vf, Vs + Vf)
        else:
            raise ValueError(f"Metodo non riconosciuto: {self.metodo}")
        
        return Vr, Vc, Vs, Vf
    
    def verifica(self) -> RisultatoTaglio:
        """
        Esegue la verifica a taglio.
        
        Returns:
            Risultato della verifica
        """
        Vr, Vc, Vs, Vf = self.calcola_taglio_resistente()
        tau = self.calcola_tensione_tangenziale_media()
        
        # Verifica
        verificato = self.taglio <= Vr
        
        # Rapporti
        rapporto_sfruttamento = self.taglio / Vr if Vr > 0 else np.inf
        coeff_sicurezza = Vr / self.taglio if self.taglio > 0 else np.inf
        
        # Dettagli
        dettagli = {
            "taglio_sollecitante": self.taglio,
            "base": self.sezione.base,
            "altezza_utile": self.sezione.altezza_utile,
            "metodo": self.metodo,
            "tensione_ammissibile_cls": self.calcestruzzo.tensione_ammissibile_taglio,
            "staffe": {
                "presenti": self.sezione.staffe is not None,
                "diametro": self.sezione.staffe.diametro if self.sezione.staffe else None,
                "passo": self.sezione.staffe.passo if self.sezione.staffe else None,
            },
            "ferri_piegati": {
                "presenti": self.sezione.ferri_piegati is not None,
                "numero": self.sezione.ferri_piegati.numero if self.sezione.ferri_piegati else None,
                "inclinazione": self.sezione.ferri_piegati.inclinazione if self.sezione.ferri_piegati else None,
            },
        }
        
        return RisultatoTaglio(
            verificato=verificato,
            taglio_resistente=Vr,
            contributo_calcestruzzo=Vc,
            contributo_staffe=Vs,
            contributo_ferri_piegati=Vf,
            tensione_tangenziale=tau,
            rapporto_sfruttamento=rapporto_sfruttamento,
            coefficiente_sicurezza=coeff_sicurezza,
            dettagli=dettagli,
        )
    
    def dimensiona_staffe(
        self,
        diametro_staffa: float = 8.0,
        numero_bracci: int = 2,
        target_sfruttamento: float = 0.90,
    ) -> float:
        """
        Dimensiona il passo delle staffe necessario.
        
        Args:
            diametro_staffa: Diametro staffa in mm
            numero_bracci: Numero di bracci
            target_sfruttamento: Sfruttamento target (0-1)
            
        Returns:
            Passo staffe necessario in mm
        """
        # Taglio da assorbire con le staffe
        Vc = self.calcola_contributo_calcestruzzo()
        Vf = self.calcola_contributo_ferri_piegati()
        V_staffe = self.taglio - Vc - Vf
        
        if V_staffe <= 0:
            return np.inf  # Staffe non necessarie
        
        # Area staffe
        Asw = numero_bracci * np.pi * (diametro_staffa / 2.0) ** 2
        
        sigma_s_amm = self.acciaio.tensione_ammissibile
        if sigma_s_amm is None:
            raise ValueError("Tensione ammissibile acciaio non definita")
        
        d = self.sezione.altezza_utile
        
        # s = (Asw * σs,amm * d) / V_staffe
        passo = (Asw * target_sfruttamento * sigma_s_amm * d) / (V_staffe * 1000)
        
        # Limitazioni normative
        passo_max = min(d / 2, 300)  # mm
        
        return min(passo, passo_max)
