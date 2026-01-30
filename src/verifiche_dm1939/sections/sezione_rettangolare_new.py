"""
Sezione rettangolare aggiornata con nuova architettura.

Eredita da SezioneBase con tutte le funzionalità avanzate.
"""

from typing import List, Optional, Tuple, Dict
import numpy as np
from .sezione_base import SezioneBase, ProprietaGeometriche, Barra, Staffa


class SezioneRettangolare(SezioneBase):
    """
    Sezione rettangolare in calcestruzzo armato.
    
    Convenzioni DM 2229/1939:
    - As = armatura inferiore (tesa con M+)
    - As' = armatura superiore (tesa con M-)
    - d = altezza utile inferiore dal lembo superiore
    - d' = altezza utile superiore dal lembo superiore
    - M+ → tende fibre inferiori
    - M- → tende fibre superiori
    - N- → compressione, N+ → trazione
    """
    
    def __init__(self, base: float, altezza: float,
                 calcestruzzo, acciaio, copriferro: float = 30.0):
        """
        Inizializza sezione rettangolare.
        
        Args:
            base: Base sezione [mm]
            altezza: Altezza sezione [mm]
            calcestruzzo: Materiale calcestruzzo
            acciaio: Materiale acciaio
            copriferro: Copriferro [mm]
        """
        super().__init__(calcestruzzo, acciaio, copriferro)
        self.base = base
        self.altezza = altezza
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
    
    def get_dimensioni_principali(self) -> Dict[str, float]:
        """Restituisce dimensioni principali."""
        return {
            'b': self.base,
            'h': self.altezza,
            'base': self.base,
            'altezza': self.altezza,
            'tipo': 'rettangolare'
        }
    
    def calcola_proprieta_geometriche(self) -> ProprietaGeometriche:
        """Calcola proprietà geometriche della sezione."""
        if self._ruotata_90:
            b_eff, h_eff = self.altezza, self.base
        else:
            b_eff, h_eff = self.base, self.altezza
        
        A = b_eff * h_eff
        y_G = h_eff / 2
        Ix = (b_eff * h_eff**3) / 12
        Iy = (h_eff * b_eff**3) / 12
        Wx = Ix / (h_eff / 2)
        
        return ProprietaGeometriche(
            area=A,
            y_baricentro=y_G,
            momento_inerzia_x=Ix,
            momento_inerzia_y=Iy,
            modulo_resistenza_sup=Wx,
            modulo_resistenza_inf=Wx
        )
    
    def get_contorno(self) -> List[Tuple[float, float]]:
        """Restituisce punti del contorno."""
        if self._ruotata_90:
            return [
                (-self.altezza/2, -self.base/2),
                (self.altezza/2, -self.base/2),
                (self.altezza/2, self.base/2),
                (-self.altezza/2, self.base/2),
                (-self.altezza/2, -self.base/2)
            ]
        else:
            return [
                (-self.base/2, 0),
                (self.base/2, 0),
                (self.base/2, self.altezza),
                (-self.base/2, self.altezza),
                (-self.base/2, 0)
            ]
    
    # ========== Metodi di compatibilità ==========
    
    @property
    def area_calcestruzzo(self) -> float:
        """Area calcestruzzo [mm²] - compatibilità."""
        return self.base * self.altezza
    
    @property
    def area_armatura_tesa(self) -> float:
        """Area armatura tesa [mm²] - compatibilità."""
        return self.As
    
    @property
    def area_armatura_compressa(self) -> float:
        """Area armatura compressa [mm²] - compatibilità."""
        return self.As_prime
    
    @property
    def altezza_utile(self) -> float:
        """Altezza utile [mm] - compatibilità."""
        return self.d
    
    @property
    def percentuale_armatura(self) -> float:
        """Percentuale geometrica armatura tesa [%]."""
        return 100 * self.As / self.area_calcestruzzo if self.area_calcestruzzo > 0 else 0.0
    
    def posizione_asse_neutro(self, momento: float = 0.0, 
                             sforzo_normale: float = 0.0) -> float:
        """
        Calcola posizione asse neutro [mm dal lembo superiore].
        
        Args:
            momento: Momento flettente [kNm] (default: solo geometria)
            sforzo_normale: Sforzo normale [kN] (default: 0)
        
        Returns:
            Posizione asse neutro [mm]
        """
        if momento == 0.0 and sforzo_normale == 0.0:
            # Solo geometria - caso semplice
            n = self.coeff_omogeneizzazione
            As = self.As
            As_p = self.As_prime
            d = self.d if self.d > 0 else self.altezza - self.copriferro - 15
            d_p = self.d_prime
            
            # Equazione di secondo grado
            a = self.base / 2
            b_coeff = n * (As + As_p)
            c = -n * (As * d + As_p * d_p)
            
            delta = b_coeff**2 - 4 * a * c
            if delta < 0:
                return d / 3  # Fallback
            
            x1 = (-b_coeff + np.sqrt(delta)) / (2 * a)
            x2 = (-b_coeff - np.sqrt(delta)) / (2 * a)
            
            x = x1 if 0 < x1 < self.altezza else x2
            return max(10.0, min(x, self.altezza - 10.0))
        else:
            # Con sollecitazioni
            asse_neutro_obj = self.calcola_asse_neutro(momento, sforzo_normale)
            return asse_neutro_obj.posizione
    
    def momento_inerzia_fessurato(self) -> float:
        """
        Calcola momento d'inerzia della sezione fessurata omogeneizzata [mm⁴].
        
        Returns:
            Momento d'inerzia fessurato
        """
        n = self.coeff_omogeneizzazione
        x = self.posizione_asse_neutro()
        As = self.As
        As_p = self.As_prime
        d = self.d if self.d > 0 else self.altezza - self.copriferro - 15
        d_p = self.d_prime
        
        # Momento d'inerzia della sezione fessurata
        # Calcestruzzo compresso
        Ic = (self.base * x**3) / 3
        
        # Armatura trasformata
        Is_inf = n * As * (d - x)**2
        Is_sup = n * As_p * (x - d_p)**2 if x > d_p else 0.0
        
        return Ic + Is_inf + Is_sup
    
    def aggiungi_staffe(self, diametro: float, passo: float, 
                       numero_bracci: int = 2) -> None:
        """
        Aggiunge staffe.
        
        Args:
            diametro: Diametro staffa [mm]
            passo: Passo staffe [mm]
            numero_bracci: Numero bracci
        """
        # Usa il metodo della classe base
        super().aggiungi_staffe(diametro, passo, numero_bracci)
    
    def __repr__(self) -> str:
        """Rappresentazione stringa."""
        return (
            f"SezioneRettangolare({self.base:.0f}x{self.altezza:.0f} mm, "
            f"As={self.As:.0f} mm², ρ={self.percentuale_armatura:.2f}%)"
        )
