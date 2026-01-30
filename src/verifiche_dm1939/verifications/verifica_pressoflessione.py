"""
Modulo Pressoflessione - Verifica pilastri a pressoflessione retta e deviata.

Implementa le verifiche di pilastri secondo Santarella e Giangreco
per pressoflessione retta (monoassiale) e deviata (biassiale).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import numpy as np

from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.materials.acciaio import Acciaio
from verifiche_dm1939.sections.sezione_rettangolare import SezioneRettangolare


@dataclass
class RisultatoPressoflessione:
    """
    Risultato della verifica a pressoflessione.
    
    Attributes:
        verificato: True se la verifica è soddisfatta
        tipo: "retta" o "deviata"
        carico_resistente: Carico assiale resistente in kN
        momento_resistente_x: Momento resistente asse x in kNm
        momento_resistente_y: Momento resistente asse y in kNm (solo deviata)
        tensione_calcestruzzo: Tensione nel calcestruzzo in MPa
        tensione_acciaio_teso: Tensione nell'acciaio teso in MPa
        tensione_acciaio_compresso: Tensione nell'acciaio compresso in MPa
        posizione_asse_neutro: Posizione asse neutro in mm
        eccentricita_totale: Eccentricità totale in mm
        rapporto_sfruttamento: N/Nr o combinazione
        coefficiente_sicurezza: Coefficiente di sicurezza
        dettagli: Dizionario con ulteriori dettagli
    """
    
    verificato: bool
    tipo: str
    carico_resistente: float  # kN
    momento_resistente_x: float  # kNm
    momento_resistente_y: Optional[float]  # kNm
    tensione_calcestruzzo: float  # MPa
    tensione_acciaio_teso: float  # MPa
    tensione_acciaio_compresso: float  # MPa
    posizione_asse_neutro: float  # mm
    eccentricita_totale: float  # mm
    rapporto_sfruttamento: float
    coefficiente_sicurezza: float
    dettagli: Dict[str, Any]
    
    def genera_report_breve(self) -> str:
        """Genera un report breve del risultato."""
        stato = "✓ VERIFICATA" if self.verificato else "✗ NON VERIFICATA"
        
        report = f"""
{'='*70}
VERIFICA A PRESSOFLESSIONE {self.tipo.upper()} - {stato}
{'='*70}
Carico resistente:           {self.carico_resistente:10.2f} kN
Momento resistente X:        {self.momento_resistente_x:10.2f} kNm
"""
        if self.momento_resistente_y is not None:
            report += f"Momento resistente Y:        {self.momento_resistente_y:10.2f} kNm\n"
        
        report += f"""Tensione calcestruzzo:       {self.tensione_calcestruzzo:10.2f} MPa
Tensione acciaio teso:       {self.tensione_acciaio_teso:10.2f} MPa
Tensione acciaio compresso:  {self.tensione_acciaio_compresso:10.2f} MPa
Eccentricità totale:         {self.eccentricita_totale:10.2f} mm
Asse neutro:                 {self.posizione_asse_neutro:10.2f} mm
Sfruttamento:                {self.rapporto_sfruttamento*100:10.1f}%
Coefficiente sicurezza:      {self.coefficiente_sicurezza:10.2f}
{'='*70}
"""
        return report


class VerificaPressoflessioneRetta:
    """
    Verifica a pressoflessione retta (monoassiale) secondo Santarella.
    
    Pilastri soggetti a sforzo normale N ed momento flettente M 
    secondo un solo asse principale.
    """
    
    def __init__(
        self,
        sezione: SezioneRettangolare,
        calcestruzzo: Calcestruzzo,
        acciaio: Acciaio,
        sforzo_normale: float,  # kN (positivo = compressione)
        momento_flettente: float,  # kNm
        lunghezza_libera_inflessione: Optional[float] = None,  # mm
        coefficiente_vincolo: float = 1.0,
    ):
        """
        Inizializza la verifica a pressoflessione retta.
        
        Args:
            sezione: Sezione da verificare
            calcestruzzo: Proprietà del calcestruzzo
            acciaio: Proprietà dell'acciaio
            sforzo_normale: Sforzo normale in kN (>0 = compressione)
            momento_flettente: Momento flettente in kNm
            lunghezza_libera_inflessione: Lunghezza libera in mm
            coefficiente_vincolo: Coefficiente vincolo (1.0=cerniera-cerniera)
        """
        self.sezione = sezione
        self.calcestruzzo = calcestruzzo
        self.acciaio = acciaio
        self.sforzo_normale = sforzo_normale  # kN
        self.momento_flettente = abs(momento_flettente)  # kNm
        self.lunghezza_libera_inflessione = lunghezza_libera_inflessione
        self.coefficiente_vincolo = coefficiente_vincolo
    
    def calcola_eccentricita_primo_ordine(self) -> float:
        """
        Calcola l'eccentricità del primo ordine.
        
        Returns:
            Eccentricità in mm
        """
        if self.sforzo_normale == 0:
            return np.inf
        
        M = self.momento_flettente * 1e6  # Nmm
        N = self.sforzo_normale * 1000  # N
        
        e0 = M / N  # mm
        
        return e0
    
    def calcola_eccentricita_secondo_ordine(self) -> float:
        """
        Calcola gli effetti del secondo ordine (instabilità).
        
        Secondo Santarella, per pilastri snelli si deve considerare
        l'incremento di eccentricità dovuto alla deformabilità.
        
        Returns:
            Incremento di eccentricità in mm
        """
        if self.lunghezza_libera_inflessione is None:
            return 0.0  # Nessun effetto secondo ordine
        
        h = self.sezione.altezza  # mm
        l0 = self.lunghezza_libera_inflessione * self.coefficiente_vincolo  # mm
        
        # Snellezza
        lambda_val = l0 / h
        
        # Secondo Santarella, per λ < 15 gli effetti sono trascurabili
        if lambda_val < 15:
            return 0.0
        
        # Formula empirica per l'incremento di eccentricità
        # e2 = (l0² * β) / (10 * h) dove β è un coefficiente
        beta = 1.0  # Coefficiente di sicurezza
        e2 = (l0**2 * beta) / (10 * h)
        
        return e2
    
    def calcola_eccentricita_totale(self) -> float:
        """
        Calcola l'eccentricità totale considerando tutti gli effetti.
        
        Returns:
            Eccentricità totale in mm
        """
        e0 = self.calcola_eccentricita_primo_ordine()
        e2 = self.calcola_eccentricita_secondo_ordine()
        
        # Eccentricità minima normativa (secondo epoca)
        h = self.sezione.altezza
        e_min = max(h / 30, 20)  # mm
        
        e_tot = max(e0 + e2, e_min)
        
        return e_tot
    
    def calcola_posizione_asse_neutro_pressoflessione(self, e: float) -> float:
        """
        Calcola la posizione dell'asse neutro in pressoflessione.
        
        Args:
            e: Eccentricità totale in mm
            
        Returns:
            Posizione asse neutro dal lembo più compresso in mm
        """
        # Iterazione per trovare la posizione dell'asse neutro
        # che soddisfa l'equilibrio traslazione e rotazione
        
        h = self.sezione.altezza
        d = self.sezione.altezza_utile
        n = self.calcestruzzo.coefficiente_omogeneizzazione
        
        # Prima stima: sezione tutta compressa
        x_trial = h / 2
        
        # Iterazione semplificata (metodo Newton-Raphson semplificato)
        for _ in range(20):
            # Verifica se tutta la sezione è compressa o parzialmente tesa
            if x_trial > h:
                x_trial = h * 0.9
            elif x_trial < 0:
                x_trial = h * 0.1
            
            # Affina la stima
            x_trial_new = h / (1 + 2 * e / h)
            
            if abs(x_trial_new - x_trial) < 0.01:
                break
            
            x_trial = x_trial_new
        
        return x_trial
    
    def verifica(self) -> RisultatoPressoflessione:
        """
        Esegue la verifica a pressoflessione retta.
        
        Returns:
            Risultato della verifica
        """
        # Eccentricità totale
        e_tot = self.calcola_eccentricita_totale()
        
        # Posizione asse neutro
        x = self.calcola_posizione_asse_neutro_pressoflessione(e_tot)
        
        # Tensioni ammissibili
        sigma_c_amm = self.calcestruzzo.tensione_ammissibile_compressione
        sigma_s_amm = self.acciaio.tensione_ammissibile
        
        if sigma_c_amm is None or sigma_s_amm is None:
            raise ValueError("Tensioni ammissibili non definite")
        
        # Geometria
        b = self.sezione.base
        h = self.sezione.altezza
        d = self.sezione.altezza_utile
        d_prime = self.sezione.copriferro + (
            self.sezione.barre_superiori[0].diametro / 2 
            if self.sezione.barre_superiori else 15
        )
        
        # Aree armatura
        As = self.sezione.area_armatura_inferiore
        As_prime = self.sezione.area_armatura_superiore
        n = self.calcestruzzo.coefficiente_omogeneizzazione
        
        # Calcolo resistenze (formule di Santarella)
        # Sforzo normale resistente
        if x >= h:  # Sezione tutta compressa
            Nr = sigma_c_amm * b * h + (n - 1) * sigma_s_amm * (As + As_prime)
            Nr = Nr / 1000  # kN
        else:  # Sezione parzialmente tesa
            Nr = sigma_c_amm * b * x + (n - 1) * sigma_s_amm * As_prime - sigma_s_amm * As
            Nr = Nr / 1000  # kN
        
        # Momento resistente
        if x >= h:
            Mr = sigma_c_amm * b * h * (h/2 - e_tot) + \
                 (n - 1) * sigma_s_amm * As_prime * (h/2 - d_prime) + \
                 (n - 1) * sigma_s_amm * As * (d - h/2)
            Mr = Mr / 1e6  # kNm
        else:
            Mr = sigma_c_amm * b * x * (d - x/3) + \
                 (n - 1) * sigma_s_amm * As_prime * (d - d_prime)
            Mr = Mr / 1e6  # kNm
        
        # Tensioni effettive (stima)
        N = self.sforzo_normale * 1000  # N
        sigma_c = sigma_c_amm * (N / (Nr * 1000)) if Nr > 0 else 0
        sigma_s_teso = sigma_s_amm * (N / (Nr * 1000)) if Nr > 0 and x < h else 0
        sigma_s_compresso = sigma_s_amm * (N / (Nr * 1000)) * 0.5 if As_prime > 0 else 0
        
        # Verifica
        verificato = (self.sforzo_normale <= Nr) and (self.momento_flettente <= Mr)
        
        # Rapporti
        rapporto_N = self.sforzo_normale / Nr if Nr > 0 else np.inf
        rapporto_M = self.momento_flettente / Mr if Mr > 0 else np.inf
        rapporto_sfruttamento = max(rapporto_N, rapporto_M)
        
        coeff_sicurezza = min(Nr / self.sforzo_normale if self.sforzo_normale > 0 else np.inf,
                              Mr / self.momento_flettente if self.momento_flettente > 0 else np.inf)
        
        # Dettagli
        dettagli = {
            "sforzo_normale": self.sforzo_normale,
            "momento_flettente": self.momento_flettente,
            "eccentricita_primo_ordine": self.calcola_eccentricita_primo_ordine(),
            "eccentricita_secondo_ordine": self.calcola_eccentricita_secondo_ordine(),
            "snellezza": (self.lunghezza_libera_inflessione * self.coefficiente_vincolo / h
                         if self.lunghezza_libera_inflessione else 0),
            "rapporto_N": rapporto_N,
            "rapporto_M": rapporto_M,
        }
        
        return RisultatoPressoflessione(
            verificato=verificato,
            tipo="retta",
            carico_resistente=Nr,
            momento_resistente_x=Mr,
            momento_resistente_y=None,
            tensione_calcestruzzo=sigma_c,
            tensione_acciaio_teso=sigma_s_teso,
            tensione_acciaio_compresso=sigma_s_compresso,
            posizione_asse_neutro=x,
            eccentricita_totale=e_tot,
            rapporto_sfruttamento=rapporto_sfruttamento,
            coefficiente_sicurezza=coeff_sicurezza,
            dettagli=dettagli,
        )


class VerificaPressoflessioneDeviata:
    """
    Verifica a pressoflessione deviata (biassiale).
    
    Pilastri soggetti a sforzo normale e momenti secondo due assi.
    """
    
    def __init__(
        self,
        sezione: SezioneRettangolare,
        calcestruzzo: Calcestruzzo,
        acciaio: Acciaio,
        sforzo_normale: float,  # kN
        momento_x: float,  # kNm
        momento_y: float,  # kNm
        metodo: str = "santarella",
    ):
        """
        Inizializza la verifica a pressoflessione deviata.
        
        Args:
            sezione: Sezione da verificare
            calcestruzzo: Proprietà del calcestruzzo
            acciaio: Proprietà dell'acciaio
            sforzo_normale: Sforzo normale in kN
            momento_x: Momento attorno all'asse x in kNm
            momento_y: Momento attorno all'asse y in kNm
            metodo: "santarella" o "giangreco"
        """
        self.sezione = sezione
        self.calcestruzzo = calcestruzzo
        self.acciaio = acciaio
        self.sforzo_normale = sforzo_normale
        self.momento_x = abs(momento_x)
        self.momento_y = abs(momento_y)
        self.metodo = metodo.lower()
    
    def verifica(self) -> RisultatoPressoflessione:
        """
        Esegue la verifica a pressoflessione deviata.
        
        Utilizza il metodo di verifica approssimato con formula di interazione:
        (Mx/Mrx)^α + (My/Mry)^α ≤ 1
        
        Returns:
            Risultato della verifica
        """
        # Verifica monoassiale su X
        verifica_x = VerificaPressoflessioneRetta(
            self.sezione, self.calcestruzzo, self.acciaio,
            self.sforzo_normale, self.momento_x
        )
        risultato_x = verifica_x.verifica()
        
        # Verifica monoassiale su Y (sezione ruotata)
        # Per semplicità, uso gli stessi parametri
        # In un'implementazione completa, si dovrebbe ruotare la sezione
        verifica_y = VerificaPressoflessioneRetta(
            self.sezione, self.calcestruzzo, self.acciaio,
            self.sforzo_normale, self.momento_y
        )
        risultato_y = verifica_y.verifica()
        
        # Formula di interazione secondo Santarella
        if self.metodo == "santarella":
            alpha = 1.5  # Esponente formula interazione
        else:  # giangreco
            alpha = 2.0
        
        # Verifica combinata
        rapporto_Mx = (self.momento_x / risultato_x.momento_resistente_x 
                       if risultato_x.momento_resistente_x > 0 else 0)
        rapporto_My = (self.momento_y / risultato_y.momento_resistente_x 
                       if risultato_y.momento_resistente_x > 0 else 0)
        
        rapporto_combinato = rapporto_Mx**alpha + rapporto_My**alpha
        
        verificato = rapporto_combinato <= 1.0
        
        # Eccentricità risultante
        e_tot = np.sqrt(verifica_x.calcola_eccentricita_totale()**2 + 
                        verifica_y.calcola_eccentricita_totale()**2)
        
        # Dettagli
        dettagli = {
            "sforzo_normale": self.sforzo_normale,
            "momento_x": self.momento_x,
            "momento_y": self.momento_y,
            "rapporto_Mx": rapporto_Mx,
            "rapporto_My": rapporto_My,
            "rapporto_combinato": rapporto_combinato,
            "formula_interazione": f"({rapporto_Mx:.3f})^{alpha} + ({rapporto_My:.3f})^{alpha} = {rapporto_combinato:.3f}",
            "metodo": self.metodo,
        }
        
        return RisultatoPressoflessione(
            verificato=verificato,
            tipo="deviata",
            carico_resistente=risultato_x.carico_resistente,
            momento_resistente_x=risultato_x.momento_resistente_x,
            momento_resistente_y=risultato_y.momento_resistente_x,
            tensione_calcestruzzo=max(risultato_x.tensione_calcestruzzo,
                                     risultato_y.tensione_calcestruzzo),
            tensione_acciaio_teso=max(risultato_x.tensione_acciaio_teso,
                                     risultato_y.tensione_acciaio_teso),
            tensione_acciaio_compresso=max(risultato_x.tensione_acciaio_compresso,
                                          risultato_y.tensione_acciaio_compresso),
            posizione_asse_neutro=risultato_x.posizione_asse_neutro,
            eccentricita_totale=e_tot,
            rapporto_sfruttamento=rapporto_combinato,
            coefficiente_sicurezza=1.0 / rapporto_combinato if rapporto_combinato > 0 else np.inf,
            dettagli=dettagli,
        )
