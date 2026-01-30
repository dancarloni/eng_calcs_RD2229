"""Sezione a doppia T (I) per travi in calcestruzzo armato."""

from typing import List, Tuple, Dict
import numpy as np
from .sezione_base import SezioneBase, ProprietaGeometriche


class SezioneI(SezioneBase):
    """
    Sezione a doppia T (I).
    
    Geometria:
         |<---- bf_sup ---->|
         -------------------  ← tf_sup
              |     |
              |     | ← h
              |     |
         -------------------  ← tf_inf
         |<---- bf_inf ---->|
    """
    
    def __init__(self, bw: float, h: float, 
                 bf_sup: float, tf_sup: float,
                 bf_inf: float, tf_inf: float,
                 calcestruzzo, acciaio, copriferro: float = 30.0):
        """
        Inizializza sezione a I.
        
        Args:
            bw: Larghezza anima [mm]
            h: Altezza totale [mm]
            bf_sup: Larghezza soletta superiore [mm]
            tf_sup: Spessore soletta superiore [mm]
            bf_inf: Larghezza soletta inferiore [mm]
            tf_inf: Spessore soletta inferiore [mm]
            calcestruzzo: Materiale calcestruzzo
            acciaio: Materiale acciaio
            copriferro: Copriferro [mm]
        """
        super().__init__(calcestruzzo, acciaio, copriferro)
        self.bw = bw
        self.h = h
        self.bf_sup = bf_sup
        self.tf_sup = tf_sup
        self.bf_inf = bf_inf
        self.tf_inf = tf_inf
    
    def get_dimensioni_principali(self) -> Dict[str, float]:
        """Restituisce dimensioni principali."""
        return {
            'bw': self.bw,
            'h': self.h,
            'bf_sup': self.bf_sup,
            'tf_sup': self.tf_sup,
            'bf_inf': self.bf_inf,
            'tf_inf': self.tf_inf,
            'tipo': 'I'
        }
    
    def calcola_proprieta_geometriche(self) -> ProprietaGeometriche:
        """Calcola proprietà geometriche della sezione a I."""
        # Area componenti
        A_sup = self.bf_sup * self.tf_sup
        A_anima = self.bw * (self.h - self.tf_sup - self.tf_inf)
        A_inf = self.bf_inf * self.tf_inf
        A_tot = A_sup + A_anima + A_inf
        
        # Baricentri componenti
        y_sup = self.tf_sup / 2
        y_anima = self.tf_sup + (self.h - self.tf_sup - self.tf_inf) / 2
        y_inf = self.h - self.tf_inf / 2
        
        # Baricentro sezione
        y_G = (A_sup * y_sup + A_anima * y_anima + A_inf * y_inf) / A_tot
        
        # Momento d'inerzia
        # Soletta superiore
        Ix_sup_proprio = (self.bf_sup * self.tf_sup**3) / 12
        Ix_sup = Ix_sup_proprio + A_sup * (y_G - y_sup)**2
        
        # Anima
        Ix_anima_proprio = (self.bw * (self.h - self.tf_sup - self.tf_inf)**3) / 12
        Ix_anima = Ix_anima_proprio + A_anima * (y_G - y_anima)**2
        
        # Soletta inferiore
        Ix_inf_proprio = (self.bf_inf * self.tf_inf**3) / 12
        Ix_inf = Ix_inf_proprio + A_inf * (y_G - y_inf)**2
        
        Ix_tot = Ix_sup + Ix_anima + Ix_inf
        
        # Momento d'inerzia y
        Iy_sup = (self.tf_sup * self.bf_sup**3) / 12
        Iy_anima = ((self.h - self.tf_sup - self.tf_inf) * self.bw**3) / 12
        Iy_inf = (self.tf_inf * self.bf_inf**3) / 12
        Iy_tot = Iy_sup + Iy_anima + Iy_inf
        
        # Moduli resistenza
        Wx_sup = Ix_tot / y_G
        Wx_inf = Ix_tot / (self.h - y_G)
        
        return ProprietaGeometriche(
            area=A_tot,
            y_baricentro=y_G,
            momento_inerzia_x=Ix_tot,
            momento_inerzia_y=Iy_tot,
            modulo_resistenza_sup=Wx_sup,
            modulo_resistenza_inf=Wx_inf
        )
    
    def get_contorno(self) -> List[Tuple[float, float]]:
        """Restituisce punti del contorno."""
        return [
            # Soletta superiore
            (-self.bf_sup/2, 0),
            (self.bf_sup/2, 0),
            (self.bf_sup/2, self.tf_sup),
            # Anima destra
            (self.bw/2, self.tf_sup),
            (self.bw/2, self.h - self.tf_inf),
            # Soletta inferiore
            (self.bf_inf/2, self.h - self.tf_inf),
            (self.bf_inf/2, self.h),
            (-self.bf_inf/2, self.h),
            (-self.bf_inf/2, self.h - self.tf_inf),
            # Anima sinistra
            (-self.bw/2, self.h - self.tf_inf),
            (-self.bw/2, self.tf_sup),
            (-self.bf_sup/2, self.tf_sup),
            (-self.bf_sup/2, 0)
        ]
