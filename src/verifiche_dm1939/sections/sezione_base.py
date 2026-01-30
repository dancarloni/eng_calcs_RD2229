"""
Classe base astratta per tutte le tipologie di sezioni.

Definisce l'interfaccia comune per il calcolo delle proprietà geometriche,
gestione armature, calcolo asse neutro e rappresentazione grafica.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
import numpy as np


@dataclass
class Barra:
    """Rappresenta una barra di armatura."""
    diametro: float  # mm
    n_barre: int
    y_pos: float  # mm - posizione verticale dal lembo superiore
    x_pos: float = 0.0  # mm - posizione orizzontale (default asse)
    
    @property
    def area(self) -> float:
        """Area totale delle barre [mm²]."""
        return self.n_barre * np.pi * (self.diametro / 2) ** 2


@dataclass
class Staffa:
    """Rappresenta una staffa di armatura a taglio."""
    diametro: float  # mm
    n_bracci: int
    passo: float  # mm
    
    @property
    def area_bracci(self) -> float:
        """Area totale dei bracci della staffa [mm²]."""
        return self.n_bracci * np.pi * (self.diametro / 2) ** 2

    @property
    def area_totale(self) -> float:
        """Alias compatibilità: area totale dei bracci [mm²]."""
        return self.area_bracci

    def to_dict(self) -> dict:
        return {
            "diametro": float(self.diametro),
            "n_bracci": int(self.n_bracci),
            "passo": float(self.passo),
            "area_totale": float(self.area_totale)
        }


@dataclass
class ProprietaGeometriche:
    """Proprietà geometriche della sezione."""
    area: float  # mm²
    y_baricentro: float  # mm - dal lembo superiore
    x_baricentro: float = 0.0  # mm - dall'asse di simmetria
    momento_statico_x: float = 0.0  # mm³ - rispetto asse x baricentrico
    momento_statico_y: float = 0.0  # mm³ - rispetto asse y baricentrico
    momento_inerzia_x: float = 0.0  # mm⁴ - rispetto asse x baricentrico
    momento_inerzia_y: float = 0.0  # mm⁴ - rispetto asse y baricentrico
    modulo_resistenza_sup: float = 0.0  # mm³ - W = Ix / ysup
    modulo_resistenza_inf: float = 0.0  # mm³ - W = Ix / yinf
    
    def __str__(self) -> str:
        return (
            f"Area: {self.area:.0f} mm²\n"
            f"Baricentro: y={self.y_baricentro:.1f} mm\n"
            f"Ix: {self.momento_inerzia_x:.0f} mm⁴\n"
            f"Iy: {self.momento_inerzia_y:.0f} mm⁴\n"
            f"Wx,sup: {self.modulo_resistenza_sup:.0f} mm³\n"
            f"Wx,inf: {self.modulo_resistenza_inf:.0f} mm³"
        )


@dataclass
class AsseNeutro:
    """Informazioni sull'asse neutro della sezione."""
    posizione: float  # mm - dal lembo superiore
    tipo_rottura: str  # 'cls', 'acciaio', 'bilanciato'
    epsilon_cls_sup: float = 0.0  # deformazione cls lembo superiore
    epsilon_cls_inf: float = 0.0  # deformazione cls lembo inferiore
    epsilon_acciaio_inf: float = 0.0  # deformazione acciaio inferiore
    epsilon_acciaio_sup: float = 0.0  # deformazione acciaio superiore
    momento_resistente: float = 0.0  # kNm
    sforzo_normale_resistente: float = 0.0  # kN


class SezioneBase(ABC):
    """
    Classe base astratta per tutte le tipologie di sezioni.
    
    Convenzioni:
    - As = armatura inferiore (tesa con M+)
    - As' = armatura superiore (tesa con M-)
    - d = altezza utile inferiore dal lembo superiore
    - d' = altezza utile superiore dal lembo superiore
    - M+ → tende fibre inferiori
    - M- → tende fibre superiori
    - N- → compressione
    - N+ → trazione
    """
    
    def __init__(self, calcestruzzo, acciaio, copriferro: float = 30.0):
        """
        Inizializza la sezione base.
        
        Args:
            calcestruzzo: Materiale calcestruzzo
            acciaio: Materiale acciaio
            copriferro: Copriferro [mm]
        """
        self.calcestruzzo = calcestruzzo
        self.acciaio = acciaio
        self.copriferro = copriferro
        
        # Armature longitudinali
        self.barre_inferiori: List[Barra] = []
        self.barre_superiori: List[Barra] = []
        self.barre_laterali: List[Barra] = []
        
        # Armature a taglio (una sola configurazione di staffa)
        self.staffe: Optional[Staffa] = None
        
        # Coefficiente di omogeneizzazione
        self._coeff_omogeneizzazione: Optional[float] = None
        self._calcola_n_automatico: bool = True
        
        # Rotazione
        self._ruotata_90: bool = False
    
    @property
    def coeff_omogeneizzazione(self) -> float:
        """
        Coefficiente di omogeneizzazione n = Es/Ec.
        
        Returns:
            Coefficiente n [-]
        """
        if self._calcola_n_automatico:
            return self.acciaio.modulo_elastico / self.calcestruzzo.modulo_elastico
        else:
            return self._coeff_omogeneizzazione or 15.0
    
    @coeff_omogeneizzazione.setter
    def coeff_omogeneizzazione(self, valore: Optional[float]):
        """
        Imposta il coefficiente di omogeneizzazione manualmente.
        
        Args:
            valore: Valore di n (None per calcolo automatico)
        """
        if valore is None:
            self._calcola_n_automatico = True
            self._coeff_omogeneizzazione = None
        else:
            self._calcola_n_automatico = False
            self._coeff_omogeneizzazione = valore
    
    @property
    def ruotata_90(self) -> bool:
        """Indica se la sezione è ruotata di 90 gradi."""
        return self._ruotata_90
    
    def ruota_90_gradi(self):
        """Ruota la sezione di 90 gradi."""
        self._ruotata_90 = not self._ruotata_90
    
    @abstractmethod
    def calcola_proprieta_geometriche(self) -> ProprietaGeometriche:
        """
        Calcola le proprietà geometriche della sezione non armata.
        
        Returns:
            Proprietà geometriche della sezione
        """
        pass
    
    @abstractmethod
    def get_contorno(self) -> List[Tuple[float, float]]:
        """
        Restituisce i punti del contorno della sezione.
        
        Returns:
            Lista di coordinate (x, y) in mm
        """
        pass
    
    @abstractmethod
    def get_dimensioni_principali(self) -> Dict[str, float]:
        """
        Restituisce le dimensioni principali della sezione.
        
        Returns:
            Dizionario con dimensioni caratteristiche
        """
        pass
    
    @property
    def As(self) -> float:
        """Area armatura inferiore (tesa con M+) [mm²]."""
        return sum(b.area for b in self.barre_inferiori)
    
    @property
    def As_prime(self) -> float:
        """Area armatura superiore (tesa con M-) [mm²]."""
        return sum(b.area for b in self.barre_superiori)
    
    @property
    def d(self) -> float:
        """Altezza utile inferiore dal lembo superiore [mm]."""
        if not self.barre_inferiori:
            prop = self.calcola_proprieta_geometriche()
            return prop.area ** 0.5 - self.copriferro  # stima
        
        # Media ponderata delle posizioni
        area_tot = sum(b.area for b in self.barre_inferiori)
        if area_tot == 0:
            return 0.0
        
        return sum(b.area * b.y_pos for b in self.barre_inferiori) / area_tot
    
    @property
    def d_prime(self) -> float:
        """Altezza utile superiore dal lembo superiore [mm]."""
        if not self.barre_superiori:
            return self.copriferro + 15.0  # stima
        
        # Media ponderata delle posizioni
        area_tot = sum(b.area for b in self.barre_superiori)
        if area_tot == 0:
            return self.copriferro + 15.0
        
        return sum(b.area * b.y_pos for b in self.barre_superiori) / area_tot
    
    def aggiungi_armatura_inferiore(self, diametro: float, n_barre: int, 
                                   y_pos: Optional[float] = None):
        """
        Aggiunge armatura inferiore (As).
        
        Args:
            diametro: Diametro barre [mm]
            n_barre: Numero di barre
            y_pos: Posizione verticale [mm] (default: auto da dimensioni)
        """
        if y_pos is None:
            dim = self.get_dimensioni_principali()
            h = dim.get('h', dim.get('altezza', 500.0))
            y_pos = h - self.copriferro - diametro / 2
        
        self.barre_inferiori.append(Barra(diametro, n_barre, y_pos))
    
    def aggiungi_armatura_superiore(self, diametro: float, n_barre: int,
                                   y_pos: Optional[float] = None):
        """
        Aggiunge armatura superiore (As').
        
        Args:
            diametro: Diametro barre [mm]
            n_barre: Numero di barre
            y_pos: Posizione verticale [mm] (default: auto da dimensioni)
        """
        if y_pos is None:
            y_pos = self.copriferro + diametro / 2
        
        self.barre_superiori.append(Barra(diametro, n_barre, y_pos))
    
    def aggiungi_staffe(self, diametro: float, passo: float, n_bracci: int = 2, numero_bracci: Optional[int] = None):
        """
        Aggiunge o configura le staffe della sezione.

        Accetta sia il nome `n_bracci` che `numero_bracci` per compatibilità
        con le varie implementazioni delle sottoclassi.

        Args:
            diametro: Diametro staffa [mm]
            passo: Passo staffe [mm]
            n_bracci: Numero bracci (default)
            numero_bracci: Alternativa per nome del parametro
        """
        n = int(numero_bracci) if numero_bracci is not None else int(n_bracci)
        self.staffe = Staffa(diametro=diametro, n_bracci=n, passo=passo)

    
    def calcola_area_ferro_necessaria(self, M: float, N: float = 0.0,
                                      posizione: str = 'inferiore') -> float:
        """
        Calcola l'area di ferro necessaria per resistere a M e N.
        
        Args:
            M: Momento flettente [kNm] (+ → tende inf, - → tende sup)
            N: Sforzo normale [kN] (- → compressione, + → trazione)
            posizione: 'inferiore' o 'superiore'
        
        Returns:
            Area ferro necessaria [mm²]
        """
        prop = self.calcola_proprieta_geometriche()
        
        # Determina altezza utile
        if posizione == 'inferiore':
            d_eff = prop.area ** 0.5 - self.copriferro - 15.0
        else:
            d_eff = self.copriferro + 15.0
        
        h = self.get_dimensioni_principali().get('h', prop.area ** 0.5)
        
        # Verifica segno momento
        if (M > 0 and posizione == 'superiore') or (M < 0 and posizione == 'inferiore'):
            return 0.0  # Fibra compressa
        
        M_abs = abs(M) * 1e6  # Nmm
        N_val = N * 1e3  # N
        
        # Stima posizione asse neutro (prima iterazione)
        x = 0.4 * d_eff if M_abs > 0 else 0.0
        
        # Braccio della coppia interna
        z = d_eff - x / 3
        
        # Forza nell'acciaio
        F_s = M_abs / z - N_val  # Trazione positiva
        
        # Area necessaria
        sigma_amm_acc = self.acciaio.tensione_ammissibile or 140.0
        if F_s > 0:  # Trazione
            As_nec = F_s / sigma_amm_acc
        else:  # Compressione (raro)
            As_nec = abs(F_s) / (sigma_amm_acc / 2)
        
        return max(0.0, As_nec)
    
    def calcola_asse_neutro(self, M: float, N: float = 0.0,
                           metodo: str = 'iterativo') -> AsseNeutro:
        """
        Calcola la posizione dell'asse neutro considerando forma sezione,
        armature e sollecitazioni.
        
        Args:
            M: Momento flettente [kNm] (+ → tende inf, - → tende sup)
            N: Sforzo normale [kN] (- → compressione, + → trazione)
            metodo: 'iterativo' o 'analitico'
        
        Returns:
            Informazioni sull'asse neutro
        """
        prop = self.calcola_proprieta_geometriche()
        n = self.coeff_omogeneizzazione
        
        M_Nmm = M * 1e6  # Nmm
        N_N = N * 1e3  # N
        
        # Parametri sezione
        As = self.As
        As_p = self.As_prime
        d = self.d if self.d > 0 else prop.area ** 0.5 - self.copriferro - 15
        d_p = self.d_prime
        
        # Dimensioni
        dim = self.get_dimensioni_principali()
        b = dim.get('b', dim.get('base', 300.0))
        h = dim.get('h', dim.get('altezza', 500.0))
        
        if metodo == 'analitico' and self.__class__.__name__ == 'SezioneRettangolare':
            # Soluzione analitica per sezione rettangolare
            x = self._calcola_asse_neutro_analitico(b, h, d, d_p, As, As_p, n, N_N, M_Nmm)
        else:
            # Metodo iterativo generale (funziona per tutte le sezioni)
            x = self._calcola_asse_neutro_iterativo(prop, d, d_p, As, As_p, n, N_N, M_Nmm)
        
        # Deformazioni
        eps_c_sup = 0.002  # Deformazione limite cls
        eps_c_inf = eps_c_sup * (h - x) / x if x > 0 else 0.0
        eps_s_inf = eps_c_sup * (d - x) / x if x > 0 else 0.0
        eps_s_sup = eps_c_sup * (x - d_p) / x if x > d_p else -eps_c_sup
        
        # Tipo rottura
        sigma_amm_acc = self.acciaio.tensione_ammissibile or 140.0
        eps_y = sigma_amm_acc / self.acciaio.modulo_elastico
        if abs(eps_s_inf) > eps_y:
            tipo = 'acciaio'
        elif eps_c_sup >= 0.002:
            tipo = 'cls'
        else:
            tipo = 'bilanciato'
        
        return AsseNeutro(
            posizione=x,
            tipo_rottura=tipo,
            epsilon_cls_sup=eps_c_sup,
            epsilon_cls_inf=eps_c_inf,
            epsilon_acciaio_inf=eps_s_inf,
            epsilon_acciaio_sup=eps_s_sup
        )
    
    def _calcola_asse_neutro_analitico(self, b: float, h: float, d: float,
                                      d_p: float, As: float, As_p: float,
                                      n: float, N: float, M: float) -> float:
        """Calcolo analitico asse neutro per sezione rettangolare."""
        # Equazione di equilibrio alla traslazione e rotazione
        # Semplificazione: sezione rettangolare, armatura concentrata
        
        # Coefficienti equazione di secondo grado
        a = b / 2
        b_coeff = n * (As + As_p)
        c = -n * (As * d + As_p * d_p)
        
        # Risoluzione
        delta = b_coeff**2 - 4 * a * c
        if delta < 0:
            return d / 3  # Fallback
        
        x1 = (-b_coeff + np.sqrt(delta)) / (2 * a)
        x2 = (-b_coeff - np.sqrt(delta)) / (2 * a)
        
        # Scegli soluzione fisica (0 < x < h)
        x = x1 if 0 < x1 < h else x2
        x = max(10.0, min(x, h - 10.0))
        
        return x
    
    def _calcola_asse_neutro_iterativo(self, prop: ProprietaGeometriche,
                                       d: float, d_p: float, As: float,
                                       As_p: float, n: float, N: float,
                                       M: float) -> float:
        """Calcolo iterativo asse neutro (generale per tutte le sezioni)."""
        dim = self.get_dimensioni_principali()
        h = dim.get('h', dim.get('altezza', 500.0))
        
        # Stima iniziale
        x = prop.y_baricentro
        
        # Iterazione Newton-Raphson
        for _ in range(20):
            # Calcola risultante compressione cls
            Fc, yc = self._calcola_risultante_cls_compressa(x)
            
            # Forze nelle armature
            eps_s = 0.002 * (d - x) / x if x > 0 else 0.001
            eps_s_p = 0.002 * (x - d_p) / x if x > d_p else -0.001
            
            sigma_amm_acc = self.acciaio.tensione_ammissibile or 140.0
            sigma_s = min(eps_s * self.acciaio.modulo_elastico, sigma_amm_acc)
            sigma_s_p = min(abs(eps_s_p) * self.acciaio.modulo_elastico, sigma_amm_acc)
            sigma_s_p = -sigma_s_p if eps_s_p < 0 else sigma_s_p
            
            Fs = As * sigma_s
            Fs_p = As_p * sigma_s_p
            
            # Equilibrio traslazione
            R = Fc + Fs_p - Fs + N
            
            # Equilibrio rotazione rispetto baricentro
            M_eq = Fc * (yc - prop.y_baricentro) + \
                   Fs * (d - prop.y_baricentro) - \
                   Fs_p * (d_p - prop.y_baricentro)
            
            # Convergenza
            if abs(R) < 100:  # N
                break
            
            # Aggiornamento
            dx = -R / (dim.get('b', 300.0))
            x += dx * 0.5  # Damping
            x = max(10.0, min(x, h - 10.0))
        
        return x
    
    def _calcola_risultante_cls_compressa(self, x: float) -> Tuple[float, float]:
        """
        Calcola risultante compressione nel calcestruzzo.
        
        Args:
            x: Posizione asse neutro [mm]
        
        Returns:
            (Forza risultante [N], Posizione baricentro forza [mm])
        """
        # Semplificazione: distribuzione rettangolare
        dim = self.get_dimensioni_principali()
        b = dim.get('b', dim.get('base', 300.0))
        
        # Area compressa (approssimazione)
        A_cls_compr = b * x
        
        # Risultante
        sigma_amm = self.calcestruzzo.tensione_ammissibile_compressione
        Fc = A_cls_compr * sigma_amm
        yc = x / 3  # Baricentro distribuzione triangolare
        
        return Fc, yc
    
    def get_info_tooltip(self, punto: Tuple[float, float]) -> str:
        """
        Restituisce informazioni contestuali per un punto della sezione.
        
        Args:
            punto: Coordinate (x, y) in mm
        
        Returns:
            Testo tooltip
        """
        x, y = punto
        prop = self.calcola_proprieta_geometriche()
        
        info = [
            f"Posizione: ({x:.0f}, {y:.0f}) mm",
            f"Distanza da baricentro: {abs(y - prop.y_baricentro):.1f} mm",
        ]
        
        # Verifica armature
        for i, barra in enumerate(self.barre_inferiori):
            dist = ((x - barra.x_pos)**2 + (y - barra.y_pos)**2)**0.5
            if dist < barra.diametro:
                info.append(f"Barra inf. {i+1}: ⌀{barra.diametro} ({barra.n_barre}×)")
        
        for i, barra in enumerate(self.barre_superiori):
            dist = ((x - barra.x_pos)**2 + (y - barra.y_pos)**2)**0.5
            if dist < barra.diametro:
                info.append(f"Barra sup. {i+1}: ⌀{barra.diametro} ({barra.n_barre}×)")
        
        return "\n".join(info)
    
    def __str__(self) -> str:
        """Rappresentazione testuale della sezione."""
        prop = self.calcola_proprieta_geometriche()
        dim = self.get_dimensioni_principali()
        
        info = [
            f"{self.__class__.__name__}",
            f"Dimensioni: {dim}",
            f"Proprietà geometriche:",
            f"  {prop}",
            f"Armature:",
            f"  As (inf): {self.As:.0f} mm²",
            f"  As' (sup): {self.As_prime:.0f} mm²",
            f"  d: {self.d:.0f} mm",
            f"  d': {self.d_prime:.0f} mm",
            f"Coeff. omogeneizzazione n: {self.coeff_omogeneizzazione:.2f}",
            f"Ruotata 90°: {'Sì' if self.ruotata_90 else 'No'}"
        ]
        
        return "\n".join(info)
