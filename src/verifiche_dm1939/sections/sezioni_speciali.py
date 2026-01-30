"""Sezioni L, U e rettangolare cava."""

from typing import List, Tuple, Dict
import numpy as np
from .sezione_base import SezioneBase, ProprietaGeometriche


class SezioneL(SezioneBase):
    """
    Sezione a L.
    
    Geometria:
         |<- b1 ->|
         ---------  ← t1
         |
         | ← h
         |
         ---------
         |<- b2 ->|
              ↑ t2
    """
    
    def __init__(self, b1: float, t1: float, h: float, b2: float, t2: float,
                 calcestruzzo, acciaio, copriferro: float = 30.0):
        """
        Inizializza sezione a L.
        
        Args:
            b1: Larghezza ala superiore [mm]
            t1: Spessore ala superiore [mm]
            h: Altezza totale [mm]
            b2: Larghezza ala inferiore [mm]
            t2: Spessore ala inferiore [mm]
            calcestruzzo: Materiale calcestruzzo
            acciaio: Materiale acciaio
            copriferro: Copriferro [mm]
        """
        super().__init__(calcestruzzo, acciaio, copriferro)
        self.b1 = b1
        self.t1 = t1
        self.h = h
        self.b2 = b2
        self.t2 = t2
    
    def get_dimensioni_principali(self) -> Dict[str, float]:
        """Restituisce dimensioni principali."""
        return {
            'b1': self.b1,
            't1': self.t1,
            'h': self.h,
            'b2': self.b2,
            't2': self.t2,
            'tipo': 'L'
        }
    
    def calcola_proprieta_geometriche(self) -> ProprietaGeometriche:
        """Calcola proprietà geometriche della sezione a L."""
        # Due rettangoli
        # Ala superiore orizzontale
        A1 = self.b1 * self.t1
        y1 = self.t1 / 2
        
        # Ala verticale
        h_vert = self.h - self.t1 - self.t2
        A2 = self.t2 * h_vert
        y2 = self.t1 + h_vert / 2
        
        # Ala inferiore orizzontale
        A3 = self.b2 * self.t2
        y3 = self.h - self.t2 / 2
        
        A_tot = A1 + A2 + A3
        
        # Baricentro
        y_G = (A1 * y1 + A2 * y2 + A3 * y3) / A_tot
        
        # Momento d'inerzia x
        Ix1 = (self.b1 * self.t1**3) / 12 + A1 * (y_G - y1)**2
        Ix2 = (self.t2 * h_vert**3) / 12 + A2 * (y_G - y2)**2
        Ix3 = (self.b2 * self.t2**3) / 12 + A3 * (y_G - y3)**2
        
        Ix_tot = Ix1 + Ix2 + Ix3
        
        # Momento d'inerzia y (approssimato)
        Iy1 = (self.t1 * self.b1**3) / 12
        Iy2 = (h_vert * self.t2**3) / 12
        Iy3 = (self.t2 * self.b2**3) / 12
        
        Iy_tot = Iy1 + Iy2 + Iy3
        
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
            (0, 0),
            (self.b1, 0),
            (self.b1, self.t1),
            (self.t2, self.t1),
            (self.t2, self.h - self.t2),
            (self.b2, self.h - self.t2),
            (self.b2, self.h),
            (0, self.h),
            (0, 0)
        ]


class SezioneU(SezioneBase):
    """
    Sezione a U (canale).
    
    Geometria:
         |<---- b ---->|
         ---------------  ← tf
         |           |
         | ← h       | ← tw
         |           |
         ---------------  ← tf
    """
    
    def __init__(self, b: float, h: float, tf: float, tw: float,
                 calcestruzzo, acciaio, copriferro: float = 30.0):
        """
        Inizializza sezione a U.
        
        Args:
            b: Larghezza totale [mm]
            h: Altezza totale [mm]
            tf: Spessore ali [mm]
            tw: Spessore anima [mm]
            calcestruzzo: Materiale calcestruzzo
            acciaio: Materiale acciaio
            copriferro: Copriferro [mm]
        """
        super().__init__(calcestruzzo, acciaio, copriferro)
        self.b = b
        self.h = h
        self.tf = tf
        self.tw = tw
    
    def get_dimensioni_principali(self) -> Dict[str, float]:
        """Restituisce dimensioni principali."""
        return {
            'b': self.b,
            'h': self.h,
            'tf': self.tf,
            'tw': self.tw,
            'tipo': 'U'
        }
    
    def calcola_proprieta_geometriche(self) -> ProprietaGeometriche:
        """Calcola proprietà geometriche della sezione a U."""
        # Tre rettangoli
        # Ala superiore
        A1 = self.b * self.tf
        y1 = self.tf / 2
        
        # Anima verticale
        h_anima = self.h - 2 * self.tf
        A2 = self.tw * h_anima
        y2 = self.tf + h_anima / 2
        
        # Ala inferiore
        A3 = self.b * self.tf
        y3 = self.h - self.tf / 2
        
        A_tot = A1 + A2 + A3
        
        # Baricentro
        y_G = (A1 * y1 + A2 * y2 + A3 * y3) / A_tot
        
        # Momento d'inerzia x
        Ix1 = (self.b * self.tf**3) / 12 + A1 * (y_G - y1)**2
        Ix2 = (self.tw * h_anima**3) / 12 + A2 * (y_G - y2)**2
        Ix3 = (self.b * self.tf**3) / 12 + A3 * (y_G - y3)**2
        
        Ix_tot = Ix1 + Ix2 + Ix3
        
        # Momento d'inerzia y
        Iy1 = (self.tf * self.b**3) / 12
        Iy2 = (h_anima * self.tw**3) / 12
        Iy3 = (self.tf * self.b**3) / 12
        
        Iy_tot = Iy1 + Iy2 + Iy3
        
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
            (-self.b/2, 0),
            (self.b/2, 0),
            (self.b/2, self.tf),
            (self.tw/2, self.tf),
            (self.tw/2, self.h - self.tf),
            (self.b/2, self.h - self.tf),
            (self.b/2, self.h),
            (-self.b/2, self.h),
            (-self.b/2, self.h - self.tf),
            (-self.tw/2, self.h - self.tf),
            (-self.tw/2, self.tf),
            (-self.b/2, self.tf),
            (-self.b/2, 0)
        ]


class SezioneRettangolareCava(SezioneBase):
    """
    Sezione rettangolare cava (scatolare).
    
    Geometria:
         |<---- b ---->|
         ---------------  ← ts
         |           |
         | ← h       | ← tw
         |           |
         ---------------  ← ti
         |<---- b ---->|
    """
    
    def __init__(self, b: float, h: float, tw: float, ts: float, ti: float,
                 calcestruzzo, acciaio, copriferro: float = 30.0):
        """
        Inizializza sezione rettangolare cava.
        
        Args:
            b: Larghezza esterna [mm]
            h: Altezza esterna [mm]
            tw: Spessore pareti verticali [mm]
            ts: Spessore parete superiore [mm]
            ti: Spessore parete inferiore [mm]
            calcestruzzo: Materiale calcestruzzo
            acciaio: Materiale acciaio
            copriferro: Copriferro [mm]
        """
        super().__init__(calcestruzzo, acciaio, copriferro)
        self.b = b
        self.h = h
        self.tw = tw
        self.ts = ts
        self.ti = ti
        
        # Verifica validità
        if 2 * tw >= b or (ts + ti) >= h:
            raise ValueError("Spessori eccessivi rispetto alle dimensioni")
    
    def get_dimensioni_principali(self) -> Dict[str, float]:
        """Restituisce dimensioni principali."""
        return {
            'b': self.b,
            'h': self.h,
            'tw': self.tw,
            'ts': self.ts,
            'ti': self.ti,
            'tipo': 'rettangolare_cava'
        }
    
    def calcola_proprieta_geometriche(self) -> ProprietaGeometriche:
        """Calcola proprietà geometriche della sezione cava."""
        # Area esterna - area interna
        A_est = self.b * self.h
        b_int = self.b - 2 * self.tw
        h_int = self.h - self.ts - self.ti
        A_int = b_int * h_int
        
        A_tot = A_est - A_int
        
        # Baricentro (simmetrica)
        y_G = self.h / 2
        
        # Momento d'inerzia
        Ix_est = (self.b * self.h**3) / 12
        Ix_int = (b_int * h_int**3) / 12
        Ix_tot = Ix_est - Ix_int
        
        Iy_est = (self.h * self.b**3) / 12
        Iy_int = (h_int * b_int**3) / 12
        Iy_tot = Iy_est - Iy_int
        
        # Moduli resistenza
        Wx_sup = Ix_tot / (self.h / 2)
        Wx_inf = Wx_sup  # Simmetrica
        
        return ProprietaGeometriche(
            area=A_tot,
            y_baricentro=y_G,
            momento_inerzia_x=Ix_tot,
            momento_inerzia_y=Iy_tot,
            modulo_resistenza_sup=Wx_sup,
            modulo_resistenza_inf=Wx_inf
        )
    
    def get_contorno(self) -> List[Tuple[float, float]]:
        """Restituisce punti del contorno (esterno + interno)."""
        b_int = self.b - 2 * self.tw
        h_int = self.h - self.ts - self.ti
        
        # Contorno esterno
        ext = [
            (-self.b/2, 0),
            (self.b/2, 0),
            (self.b/2, self.h),
            (-self.b/2, self.h),
            (-self.b/2, 0)
        ]
        
        # Contorno interno (foro)
        int_pts = [
            (-b_int/2, self.ts),
            (b_int/2, self.ts),
            (b_int/2, self.ts + h_int),
            (-b_int/2, self.ts + h_int),
            (-b_int/2, self.ts)
        ]
        
        return ext + int_pts
