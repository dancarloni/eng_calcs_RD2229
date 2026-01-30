"""Sezione a T per travi in calcestruzzo armato."""

from typing import List, Tuple, Dict
import numpy as np
from .sezione_base import SezioneBase, ProprietaGeometriche


class SezioneT(SezioneBase):
    """
    Sezione a T (trave con soletta collaborante).
    
    Geometria:
         |<---- bf ---->|
         ---------------  ← tf (soletta)
              |   |
              |   | ← h (altezza totale)
              |   |
              -----  ← bw (nervatura)
    """
    
    def __init__(self, bw: float, h: float, bf: float, tf: float,
                 calcestruzzo, acciaio, copriferro: float = 30.0):
        """
        Inizializza sezione a T.
        
        Args:
            bw: Larghezza nervatura [mm]
            h: Altezza totale [mm]
            bf: Larghezza soletta [mm]
            tf: Spessore soletta [mm]
            calcestruzzo: Materiale calcestruzzo
            acciaio: Materiale acciaio
            copriferro: Copriferro [mm]
        """
        super().__init__(calcestruzzo, acciaio, copriferro)
        self.bw = bw
        self.h = h
        self.bf = bf
        self.tf = tf
    
    def get_dimensioni_principali(self) -> Dict[str, float]:
        """Restituisce dimensioni principali."""
        return {
            'bw': self.bw,
            'h': self.h,
            'bf': self.bf,
            'tf': self.tf,
            'tipo': 'T'
        }
    
    def calcola_proprieta_geometriche(self) -> ProprietaGeometriche:
        """Calcola proprietà geometriche della sezione a T."""
        if self._ruotata_90:
            return self._calcola_proprieta_ruotata()
        
        # Area
        A_soletta = self.bf * self.tf
        A_nervatura = self.bw * (self.h - self.tf)
        A_tot = A_soletta + A_nervatura
        
        # Baricentro
        y_soletta = self.tf / 2
        y_nervatura = self.tf + (self.h - self.tf) / 2
        
        y_G = (A_soletta * y_soletta + A_nervatura * y_nervatura) / A_tot
        
        # Momento d'inerzia rispetto asse baricentrico
        # Soletta
        Ix_soletta_proprio = (self.bf * self.tf**3) / 12
        Ix_soletta = Ix_soletta_proprio + A_soletta * (y_G - y_soletta)**2
        
        # Nervatura
        Ix_nerv_proprio = (self.bw * (self.h - self.tf)**3) / 12
        Ix_nervatura = Ix_nerv_proprio + A_nervatura * (y_G - y_nervatura)**2
        
        Ix_tot = Ix_soletta + Ix_nervatura
        
        # Momento d'inerzia rispetto asse y
        Iy_soletta = (self.tf * self.bf**3) / 12
        Iy_nerv = (self.h - self.tf) * self.bw**3 / 12
        Iy_tot = Iy_soletta + Iy_nerv
        
        # Moduli di resistenza
        Wx_sup = Ix_tot / y_G
        Wx_inf = Ix_tot / (self.h - y_G)
        
        return ProprietaGeometriche(
            area=A_tot,
            y_baricentro=y_G,
            x_baricentro=0.0,
            momento_statico_x=0.0,
            momento_statico_y=0.0,
            momento_inerzia_x=Ix_tot,
            momento_inerzia_y=Iy_tot,
            modulo_resistenza_sup=Wx_sup,
            modulo_resistenza_inf=Wx_inf
        )
    
    def _calcola_proprieta_ruotata(self) -> ProprietaGeometriche:
        """Calcola proprietà con sezione ruotata 90°."""
        # Scambia dimensioni
        prop_norm = self.calcola_proprieta_geometriche()
        return ProprietaGeometriche(
            area=prop_norm.area,
            y_baricentro=prop_norm.x_baricentro,
            x_baricentro=prop_norm.y_baricentro,
            momento_inerzia_x=prop_norm.momento_inerzia_y,
            momento_inerzia_y=prop_norm.momento_inerzia_x,
            modulo_resistenza_sup=prop_norm.modulo_resistenza_inf,
            modulo_resistenza_inf=prop_norm.modulo_resistenza_sup
        )
    
    def get_contorno(self) -> List[Tuple[float, float]]:
        """Restituisce punti del contorno."""
        if self._ruotata_90:
            # Ruotata: la soletta diventa laterale
            return [
                (-self.tf/2, 0),
                (-self.tf/2, self.bf/2),
                (-self.h/2, self.bw/2),
                (-self.h/2, -self.bw/2),
                (-self.tf/2, -self.bf/2),
                (-self.tf/2, 0),
                (self.tf/2, 0),
                (self.tf/2, -self.bf/2),
                (self.h/2, -self.bw/2),
                (self.h/2, self.bw/2),
                (self.tf/2, self.bf/2),
                (self.tf/2, 0),
            ]
        else:
            # Normale: soletta superiore
            return [
                (-self.bf/2, 0),
                (self.bf/2, 0),
                (self.bf/2, self.tf),
                (self.bw/2, self.tf),
                (self.bw/2, self.h),
                (-self.bw/2, self.h),
                (-self.bw/2, self.tf),
                (-self.bf/2, self.tf),
                (-self.bf/2, 0)
            ]
    
    def _calcola_risultante_cls_compressa(self, x: float) -> Tuple[float, float]:
        """Calcola risultante compressione considerando forma a T."""
        sigma_amm = self.calcestruzzo.tensione_ammissibile_compressione
        if x <= self.tf:
            # Zona compressa solo nella soletta
            A_compr = self.bf * x
            Fc = A_compr * sigma_amm
            yc = x / 3
        else:
            # Zona compressa in soletta + nervatura
            A_soletta = self.bf * self.tf
            A_nerv = self.bw * (x - self.tf)
            
            Fc_soletta = A_soletta * sigma_amm
            Fc_nerv = A_nerv * sigma_amm
            
            yc_soletta = self.tf / 2
            yc_nerv = self.tf + (x - self.tf) / 3
            
            Fc = Fc_soletta + Fc_nerv
            yc = (Fc_soletta * yc_soletta + Fc_nerv * yc_nerv) / Fc if Fc > 0 else x / 3
        
        return Fc, yc
