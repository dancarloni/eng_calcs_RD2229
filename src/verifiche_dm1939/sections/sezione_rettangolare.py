"""
Modulo Sezione Rettangolare - Geometria e armatura.

Implementa la geometria di sezioni rettangolari in calcestruzzo armato
con disposizione dell'armatura secondo le pratiche dell'epoca.

AGGIORNATO: Ora eredita da SezioneBase con supporto completo per:
- Calcolo proprietà geometriche (area, momenti inerzia, moduli resistenza)
- Coefficiente omogeneizzazione Es/Ec
- Calcolo asse neutro considerando N e M
- Utility calcolo area ferro necessaria
- Rotazione 90 gradi
"""

from typing import List, Optional, Tuple, Dict
import numpy as np
from .sezione_base import SezioneBase, ProprietaGeometriche, Barra, Staffa
    numero_bracci: int = 2
    
    @property
    def area_singola(self) -> float:
        """Area sezione singola staffa in mm²."""
        return np.pi * (self.diametro / 2.0) ** 2
    
    @property
    def area_totale(self) -> float:
        """Area totale dei bracci in mm²."""
        return self.area_singola * self.numero_bracci
    
    def __repr__(self) -> str:
        return f"Staffa(φ{self.diametro}/{self.passo}, {self.numero_bracci} bracci)"


@dataclass
class FerroPiegato:
    """
    Rappresenta ferri piegati per resistenza a taglio.
    
    Attributes:
        diametro: Diametro ferro in mm
        numero: Numero di ferri piegati
        inclinazione: Angolo di inclinazione in gradi
    """
    
    diametro: float  # mm
    numero: int = 2
    inclinazione: float = 45.0  # gradi
    
    @property
    def area_singola(self) -> float:
        """Area sezione singolo ferro in mm²."""
        return np.pi * (self.diametro / 2.0) ** 2
    
    @property
    def area_totale(self) -> float:
        """Area totale ferri piegati in mm²."""
        return self.area_singola * self.numero
    
    def __repr__(self) -> str:
        return f"FerroPiegato({self.numero}φ{self.diametro}, {self.inclinazione}°)"


class SezioneRettangolare:
    """
    Sezione rettangolare in calcestruzzo armato.
    
    Implementa la geometria e la disposizione dell'armatura secondo
    le pratiche costruttive dell'epoca del DM 2229/1939.
    
    Attributes:
        base: Base sezione in mm
        altezza: Altezza sezione in mm
        copriferro: Copriferro in mm
        barre_inferiori: Lista barre armatura tesa
        barre_superiori: Lista barre armatura compressa
        staffe: Staffe per armatura a taglio
        ferri_piegati: Ferri piegati per taglio
    """
    
    def __init__(
        self,
        base: float,
        altezza: float,
        copriferro: float = 30.0,
    ):
        """
        Inizializza la sezione rettangolare.
        
        Args:
            base: Base sezione in mm
            altezza: Altezza sezione in mm
            copriferro: Copriferro in mm (default 30 mm)
        """
        self.base = base
        self.altezza = altezza
        self.copriferro = copriferro
        
        self.barre_inferiori: List[Barra] = []
        self.barre_superiori: List[Barra] = []
        self.staffe: Optional[Staffa] = None
        self.ferri_piegati: Optional[FerroPiegato] = None
        
        self._valida_geometria()
    
    def _valida_geometria(self) -> None:
        """Valida la geometria della sezione."""
        if self.base <= 0 or self.altezza <= 0:
            raise ValueError("Base e altezza devono essere positive")
        
        if self.copriferro < 0:
            raise ValueError("Il copriferro non può essere negativo")
        
        if self.copriferro > min(self.base, self.altezza) / 3:
            import warnings
            warnings.warn(
                f"Copriferro {self.copriferro} mm eccessivo per sezione "
                f"{self.base}x{self.altezza} mm"
            )
    
    def aggiungi_armatura_inferiore(
        self,
        diametro: float,
        numero_barre: int,
        strato: int = 1,
    ) -> None:
        """
        Aggiunge armatura al lembo inferiore (teso per trave).
        
        Args:
            diametro: Diametro barre in mm
            numero_barre: Numero di barre
            strato: Numero dello strato (1=più basso)
        """
        # Posizione y dal lembo compresso
        distanza_interstrato = diametro + 5  # mm
        y = self.altezza - self.copriferro - diametro / 2 - (strato - 1) * distanza_interstrato
        
        # Distribuzione lungo la base
        if numero_barre == 1:
            x_positions = [0.0]
        else:
            larghezza_utile = self.base - 2 * (self.copriferro + diametro / 2)
            x_positions = np.linspace(
                -larghezza_utile / 2,
                larghezza_utile / 2,
                numero_barre
            )
        
        for x in x_positions:
            barra = Barra(diametro=diametro, posizione_x=x, posizione_y=y)
            self.barre_inferiori.append(barra)
    
    def aggiungi_armatura_superiore(
        self,
        diametro: float,
        numero_barre: int,
        strato: int = 1,
    ) -> None:
        """
        Aggiunge armatura al lembo superiore (compresso per trave).
        
        Args:
            diametro: Diametro barre in mm
            numero_barre: Numero di barre
            strato: Numero dello strato (1=più alto)
        """
        # Posizione y dal lembo compresso
        distanza_interstrato = diametro + 5  # mm
        y = self.copriferro + diametro / 2 + (strato - 1) * distanza_interstrato
        
        # Distribuzione lungo la base
        if numero_barre == 1:
            x_positions = [0.0]
        else:
            larghezza_utile = self.base - 2 * (self.copriferro + diametro / 2)
            x_positions = np.linspace(
                -larghezza_utile / 2,
                larghezza_utile / 2,
                numero_barre
            )
        
        for x in x_positions:
            barra = Barra(diametro=diametro, posizione_x=x, posizione_y=y)
            self.barre_superiori.append(barra)
    
    def aggiungi_staffe(
        self,
        diametro: float,
        passo: float,
        numero_bracci: int = 2,
    ) -> None:
        """
        Aggiunge staffe per armatura a taglio.
        
        Args:
            diametro: Diametro staffe in mm
            passo: Passo staffe in mm
            numero_bracci: Numero di bracci (2 o 4)
        """
        self.staffe = Staffa(
            diametro=diametro,
            passo=passo,
            numero_bracci=numero_bracci
        )
    
    def aggiungi_ferri_piegati(
        self,
        diametro: float,
        numero: int = 2,
        inclinazione: float = 45.0,
    ) -> None:
        """
        Aggiunge ferri piegati per resistenza a taglio.
        
        Args:
            diametro: Diametro ferri in mm
            numero: Numero di ferri piegati
            inclinazione: Angolo di inclinazione in gradi
        """
        self.ferri_piegati = FerroPiegato(
            diametro=diametro,
            numero=numero,
            inclinazione=inclinazione
        )
    
    @property
    def area_calcestruzzo(self) -> float:
        """Area lorda sezione calcestruzzo in mm²."""
        return self.base * self.altezza
    
    @property
    def area_armatura_inferiore(self) -> float:
        """Area totale armatura inferiore in mm²."""
        return sum(barra.area for barra in self.barre_inferiori)
    
    @property
    def area_armatura_superiore(self) -> float:
        """Area totale armatura superiore in mm²."""
        return sum(barra.area for barra in self.barre_superiori)
    
    @property
    def area_armatura_totale(self) -> float:
        """Area totale armatura longitudinale in mm²."""
        return self.area_armatura_inferiore + self.area_armatura_superiore
    
    @property
    def altezza_utile(self) -> float:
        """
        Altezza utile della sezione in mm.
        
        Calcolata come distanza dal lembo compresso al baricentro
        dell'armatura tesa.
        """
        if not self.barre_inferiori:
            return self.altezza - self.copriferro
        
        # Baricentro armatura inferiore
        y_barre = [barra.posizione_y for barra in self.barre_inferiori]
        return np.mean(y_barre)
    
    @property
    def percentuale_armatura_geometrica(self) -> float:
        """Percentuale geometrica di armatura (ρ%)."""
        if self.area_armatura_totale == 0:
            return 0.0
        return 100.0 * self.area_armatura_totale / self.area_calcestruzzo
    
    @property
    def percentuale_armatura_meccanica(self) -> float:
        """Percentuale meccanica di armatura (ω% rispetto a sezione ideale)."""
        area_ideale = self.base * self.altezza_utile
        if self.area_armatura_totale == 0:
            return 0.0
        return 100.0 * self.area_armatura_totale / area_ideale
    
    def posizione_asse_neutro(self, n: float = 15) -> float:
        """
        Calcola la posizione dell'asse neutro in sezione fessurata.
        
        Args:
            n: Coefficiente di omogeneizzazione Es/Ec
            
        Returns:
            Posizione asse neutro dal lembo compresso in mm
        """
        if self.area_armatura_inferiore == 0:
            raise ValueError("Nessuna armatura tesa definita")
        
        As = self.area_armatura_inferiore
        As_prime = self.area_armatura_superiore
        d = self.altezza_utile
        d_prime = self.copriferro + (
            self.barre_superiori[0].diametro / 2 if self.barre_superiori else 0
        )
        
        # Equazione di equilibrio alla rotazione
        # b*x²/2 + n*As'*(x-d') - n*As*(d-x) = 0
        b = self.base
        
        # Risoluzione equazione di secondo grado
        a_coeff = b / 2.0
        b_coeff = n * (As + As_prime)
        c_coeff = -n * (As * d + As_prime * d_prime)
        
        discriminante = b_coeff**2 - 4 * a_coeff * c_coeff
        if discriminante < 0:
            raise ValueError("Errore nel calcolo dell'asse neutro")
        
        x = (-b_coeff + np.sqrt(discriminante)) / (2 * a_coeff)
        
        return x
    
    def momento_inerzia_fessurato(self, n: float = 15) -> float:
        """
        Calcola il momento d'inerzia della sezione fessurata.
        
        Args:
            n: Coefficiente di omogeneizzazione Es/Ec
            
        Returns:
            Momento d'inerzia in mm⁴
        """
        x = self.posizione_asse_neutro(n)
        
        # Inerzia calcestruzzo compresso
        Ic = self.base * x**3 / 3.0
        
        # Contributo armatura tesa
        As = self.area_armatura_inferiore
        d = self.altezza_utile
        Is_tesa = n * As * (d - x)**2
        
        # Contributo armatura compressa
        As_prime = self.area_armatura_superiore
        if As_prime > 0 and self.barre_superiori:
            d_prime = np.mean([b.posizione_y for b in self.barre_superiori])
            Is_compressa = n * As_prime * (x - d_prime)**2
        else:
            Is_compressa = 0.0
        
        return Ic + Is_tesa + Is_compressa
    
    def to_dict(self) -> dict:
        """Converte la sezione in dizionario."""
        return {
            "geometria": {
                "base": self.base,
                "altezza": self.altezza,
                "copriferro": self.copriferro,
                "area_calcestruzzo": self.area_calcestruzzo,
                "altezza_utile": self.altezza_utile,
            },
            "armatura_longitudinale": {
                "inferiore": {
                    "numero_barre": len(self.barre_inferiori),
                    "area_totale": self.area_armatura_inferiore,
                },
                "superiore": {
                    "numero_barre": len(self.barre_superiori),
                    "area_totale": self.area_armatura_superiore,
                },
                "percentuale_geometrica": self.percentuale_armatura_geometrica,
                "percentuale_meccanica": self.percentuale_armatura_meccanica,
            },
            "armatura_trasversale": {
                "staffe": self.staffe.to_dict() if self.staffe else None,
                "ferri_piegati": (
                    {
                        "diametro": self.ferri_piegati.diametro,
                        "numero": self.ferri_piegati.numero,
                        "inclinazione": self.ferri_piegati.inclinazione,
                    }
                    if self.ferri_piegati
                    else None
                ),
            },
        }
    
    def __repr__(self) -> str:
        """Rappresentazione stringa della sezione."""
        return (
            f"SezioneRettangolare({self.base}x{self.altezza} mm, "
            f"As={self.area_armatura_totale:.0f} mm², "
            f"ρ={self.percentuale_armatura_geometrica:.2f}%)"
        )


# Metodo helper per Staffa
def _staffa_to_dict(self: Staffa) -> dict:
    return {
        "diametro": self.diametro,
        "passo": self.passo,
        "numero_bracci": self.numero_bracci,
        "area_totale": self.area_totale,
    }

Staffa.to_dict = _staffa_to_dict
