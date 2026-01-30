"""Sezioni circolari (piene e cave) per pilastri in calcestruzzo armato."""

from typing import List, Tuple, Dict
import numpy as np
from .sezione_base import SezioneBase, ProprietaGeometriche


class SezioneCircolare(SezioneBase):
    """
    Sezione circolare piena.
    
    Geometria:
         ___
        /   \\
       |  ·  | ← D (diametro)
        \\___/
    """
    
    def __init__(self, D: float, calcestruzzo, acciaio, copriferro: float = 30.0):
        """
        Inizializza sezione circolare.
        
        Args:
            D: Diametro [mm]
            calcestruzzo: Materiale calcestruzzo
            acciaio: Materiale acciaio
            copriferro: Copriferro [mm]
        """
        super().__init__(calcestruzzo, acciaio, copriferro)
        self.D = D
    
    def get_dimensioni_principali(self) -> Dict[str, float]:
        """Restituisce dimensioni principali."""
        return {
            'D': self.D,
            'diametro': self.D,
            'tipo': 'circolare'
        }
    
    def calcola_proprieta_geometriche(self) -> ProprietaGeometriche:
        """Calcola proprietà geometriche della sezione circolare."""
        # Area
        A = np.pi * (self.D / 2)**2
        
        # Baricentro
        y_G = self.D / 2
        
        # Momento d'inerzia
        I = np.pi * self.D**4 / 64
        
        # Modulo resistenza
        W = I / (self.D / 2)
        
        return ProprietaGeometriche(
            area=A,
            y_baricentro=y_G,
            momento_inerzia_x=I,
            momento_inerzia_y=I,
            modulo_resistenza_sup=W,
            modulo_resistenza_inf=W
        )
    
    def get_contorno(self) -> List[Tuple[float, float]]:
        """Restituisce punti del contorno."""
        n_punti = 64
        theta = np.linspace(0, 2*np.pi, n_punti)
        r = self.D / 2
        y_center = self.D / 2
        
        return [(r * np.cos(t), y_center + r * np.sin(t)) for t in theta]
    
    def _calcola_risultante_cls_compressa(self, x: float) -> Tuple[float, float]:
        """Calcola risultante compressione in sezione circolare."""
        r = self.D / 2
        y_center = self.D / 2
        
        sigma_amm = self.calcestruzzo.tensione_ammissibile_compressione
        if x >= self.D:
            # Tutta compressa
            A_compr = np.pi * r**2
            Fc = A_compr * sigma_amm
            yc = y_center
        elif x <= 0:
            # Nulla compressa
            Fc = 0.0
            yc = 0.0
        else:
            # Parzialmente compressa - approssimazione
            # Area segmento circolare
            h_segm = x if x < y_center else self.D - x
            theta = 2 * np.arccos((r - h_segm) / r) if h_segm < r else np.pi
            A_segm = r**2 * (theta - np.sin(theta)) / 2
            
            A_compr = A_segm if x < y_center else np.pi * r**2 - A_segm
            
            # Baricentro segmento (approssimazione)
            if x < y_center:
                yc = x / 2
            else:
                yc = (y_center + x) / 2
            
            Fc = A_compr * sigma_amm
        
        return Fc, yc


class SezioneCircolareCava(SezioneBase):
    """
    Sezione circolare cava (tubo).
    
    Geometria:
         _____
        / ___ \\
       | |   | | ← De (esterno), Di (interno)
        \\_____/
    """
    
    def __init__(self, De: float, Di: float, calcestruzzo, acciaio, 
                 copriferro: float = 30.0):
        """
        Inizializza sezione circolare cava.
        
        Args:
            De: Diametro esterno [mm]
            Di: Diametro interno [mm]
            calcestruzzo: Materiale calcestruzzo
            acciaio: Materiale acciaio
            copriferro: Copriferro [mm]
        """
        super().__init__(calcestruzzo, acciaio, copriferro)
        self.De = De
        self.Di = Di
        
        if Di >= De:
            raise ValueError("Diametro interno deve essere < diametro esterno")
    
    def get_dimensioni_principali(self) -> Dict[str, float]:
        """Restituisce dimensioni principali."""
        return {
            'De': self.De,
            'Di': self.Di,
            'spessore': (self.De - self.Di) / 2,
            'tipo': 'circolare_cava'
        }
    
    def calcola_proprieta_geometriche(self) -> ProprietaGeometriche:
        """Calcola proprietà geometriche della sezione cava."""
        # Area
        A_est = np.pi * (self.De / 2)**2
        A_int = np.pi * (self.Di / 2)**2
        A = A_est - A_int
        
        # Baricentro
        y_G = self.De / 2
        
        # Momento d'inerzia
        I_est = np.pi * self.De**4 / 64
        I_int = np.pi * self.Di**4 / 64
        I = I_est - I_int
        
        # Modulo resistenza
        W = I / (self.De / 2)
        
        return ProprietaGeometriche(
            area=A,
            y_baricentro=y_G,
            momento_inerzia_x=I,
            momento_inerzia_y=I,
            modulo_resistenza_sup=W,
            modulo_resistenza_inf=W
        )
    
    def get_contorno(self) -> List[Tuple[float, float]]:
        """Restituisce punti del contorno."""
        n_punti = 64
        theta = np.linspace(0, 2*np.pi, n_punti)
        
        r_est = self.De / 2
        r_int = self.Di / 2
        y_center = self.De / 2
        
        # Contorno esterno
        ext = [(r_est * np.cos(t), y_center + r_est * np.sin(t)) for t in theta]
        
        # Contorno interno (in senso opposto)
        int_pts = [(r_int * np.cos(t), y_center + r_int * np.sin(t)) 
                   for t in reversed(theta)]
        
        return ext + int_pts
    
    def _calcola_risultante_cls_compressa(self, x: float) -> Tuple[float, float]:
        """Calcola risultante compressione in sezione cava."""
        # Semplificazione: come sezione piena con riduzione area
        r_est = self.De / 2
        r_int = self.Di / 2
        sigma_amm = self.calcestruzzo.tensione_ammissibile_compressione
        
        # Calcolo simile a circolare piena, ma sottraendo parte interna
        A_compr_est = min(np.pi * r_est**2, max(0, np.pi * r_est**2 * x / self.De))
        A_compr_int = min(np.pi * r_int**2, max(0, np.pi * r_int**2 * x / self.De))
        
        A_compr = A_compr_est - A_compr_int
        Fc = A_compr * sigma_amm
        yc = x / 2 if x > 0 else 0
        
        return Fc, yc
