"""
Modulo Grafici - Generazione grafici per verifiche strutturali.

Crea grafici dettagliati di:
- Diagrammi di sollecitazione
- Distribuzione tensioni
- Domini di rottura
- Sezioni con armature
"""

from typing import Optional, Tuple, List
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from verifiche_dm1939.sections.sezione_rettangolare import SezioneRettangolare, Barra


class GeneratoreGrafici:
    """
    Generatore di grafici per verifiche strutturali.
    """
    
    # Stile grafico professionale
    STYLE_CONFIG = {
        "figure.figsize": (10, 8),
        "figure.dpi": 100,
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "grid.alpha": 0.3,
    }
    
    def __init__(self, stile: str = "default"):
        """
        Inizializza il generatore.
        
        Args:
            stile: Stile matplotlib ("default", "seaborn", "classic")
        """
        plt.style.use(stile if stile != "default" else "default")
        for key, value in self.STYLE_CONFIG.items():
            plt.rcParams[key] = value
    
    @staticmethod
    def disegna_sezione(
        sezione: SezioneRettangolare,
        asse_neutro: Optional[float] = None,
        mostra_quotature: bool = True,
        titolo: str = "Sezione Trasversale",
    ) -> Figure:
        """
        Disegna la sezione trasversale con armature.
        
        Args:
            sezione: Sezione da disegnare
            asse_neutro: Posizione asse neutro dal lembo compresso (mm)
            mostra_quotature: Se True mostra le quote
            titolo: Titolo del grafico
            
        Returns:
            Figura matplotlib
        """
        fig, ax = plt.subplots(figsize=(8, 10))
        
        b = sezione.base
        h = sezione.altezza
        c = sezione.copriferro
        
        # Contorno sezione calcestruzzo
        rect = patches.Rectangle(
            (-b/2, 0), b, h,
            linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3
        )
        ax.add_patch(rect)
        
        # Asse neutro
        if asse_neutro is not None:
            ax.plot(
                [-b/2, b/2], [asse_neutro, asse_neutro],
                'r--', linewidth=1.5, label=f'Asse neutro (x={asse_neutro:.1f} mm)'
            )
        
        # Disegna barre inferiori
        for barra in sezione.barre_inferiori:
            circle = patches.Circle(
                (barra.posizione_x, barra.posizione_y),
                barra.diametro/2,
                color='red', ec='darkred', linewidth=1.5
            )
            ax.add_patch(circle)
        
        # Disegna barre superiori
        for barra in sezione.barre_superiori:
            circle = patches.Circle(
                (barra.posizione_x, barra.posizione_y),
                barra.diametro/2,
                color='blue', ec='darkblue', linewidth=1.5
            )
            ax.add_patch(circle)
        
        # Staffe (rappresentazione schematica)
        if sezione.staffe:
            # Staffa perimetrale
            staffa_rect = patches.Rectangle(
                (-b/2 + c, c), b - 2*c, h - 2*c,
                linewidth=1, edgecolor='green', facecolor='none',
                linestyle='--', alpha=0.5
            )
            ax.add_patch(staffa_rect)
        
        # Quotature
        if mostra_quotature:
            # Quota base
            ax.annotate('', xy=(b/2, -h*0.1), xytext=(-b/2, -h*0.1),
                       arrowprops=dict(arrowstyle='<->', lw=1))
            ax.text(0, -h*0.15, f'b = {b:.0f} mm', ha='center', fontsize=9)
            
            # Quota altezza
            ax.annotate('', xy=(b/2 + b*0.15, h), xytext=(b/2 + b*0.15, 0),
                       arrowprops=dict(arrowstyle='<->', lw=1))
            ax.text(b/2 + b*0.2, h/2, f'h = {h:.0f} mm', 
                   rotation=90, va='center', fontsize=9)
            
            # Quota altezza utile
            d = sezione.altezza_utile
            ax.plot([b/2 + b*0.05, b/2 + b*0.1], [d, d], 'b-', lw=1)
            ax.text(b/2 + b*0.12, d, f'd = {d:.0f} mm', va='center', fontsize=8)
        
        # Configurazione assi
        margine = max(b, h) * 0.25
        ax.set_xlim(-b/2 - margine, b/2 + margine)
        ax.set_ylim(-h*0.2, h + margine)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2)
        ax.set_xlabel('Larghezza (mm)')
        ax.set_ylabel('Altezza (mm)')
        ax.set_title(titolo, fontweight='bold')
        
        # Legenda
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                  markersize=10, label='Armatura tesa'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
                  markersize=10, label='Armatura compressa'),
        ]
        if sezione.staffe:
            legend_elements.append(
                Line2D([0], [0], color='green', linestyle='--', 
                      label=f'Staffe φ{sezione.staffe.diametro}/{sezione.staffe.passo}')
            )
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def diagramma_tensioni_flessione(
        sezione: SezioneRettangolare,
        sigma_c: float,
        sigma_s: float,
        x: float,
        sigma_c_amm: float,
        sigma_s_amm: float,
    ) -> Figure:
        """
        Disegna il diagramma delle tensioni per flessione.
        
        Args:
            sezione: Sezione
            sigma_c: Tensione nel calcestruzzo (MPa)
            sigma_s: Tensione nell'acciaio (MPa)
            x: Posizione asse neutro (mm)
            sigma_c_amm: Tensione ammissibile calcestruzzo (MPa)
            sigma_s_amm: Tensione ammissibile acciaio (MPa)
            
        Returns:
            Figura matplotlib
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        h = sezione.altezza
        d = sezione.altezza_utile
        b = sezione.base
        
        # GRAFICO 1: Sezione con asse neutro
        # Contorno sezione
        rect = patches.Rectangle(
            (0, 0), b/5, h,
            linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3
        )
        ax1.add_patch(rect)
        
        # Asse neutro
        ax1.plot([0, b/5], [x, x], 'r-', linewidth=2, label=f'Asse neutro (x={x:.1f} mm)')
        
        # Armatura
        for barra in sezione.barre_inferiori:
            ax1.plot(b/10, barra.posizione_y, 'ro', markersize=8)
        for barra in sezione.barre_superiori:
            ax1.plot(b/10, barra.posizione_y, 'bo', markersize=8)
        
        ax1.set_ylim(-h*0.1, h*1.1)
        ax1.set_xlim(-b/10, b/4)
        ax1.set_aspect('equal')
        ax1.set_ylabel('Altezza (mm)')
        ax1.set_title('Sezione')
        ax1.legend()
        ax1.grid(True, alpha=0.2)
        
        # GRAFICO 2: Diagramma tensioni
        # Tensione nel calcestruzzo (triangolare)
        y_cls = [0, x]
        sigma_cls = [sigma_c, 0]
        ax2.fill_betweenx(y_cls, 0, sigma_cls, alpha=0.3, color='blue', 
                         label=f'σc = {sigma_c:.2f} MPa')
        ax2.plot(sigma_cls, y_cls, 'b-', linewidth=2)
        
        # Tensione nell'acciaio
        ax2.plot([0, sigma_s], [d, d], 'r-', linewidth=3, 
                label=f'σs = {sigma_s:.2f} MPa')
        ax2.plot(sigma_s, d, 'ro', markersize=10)
        
        # Tensioni ammissibili (linee di riferimento)
        ax2.axvline(sigma_c_amm, color='blue', linestyle='--', alpha=0.5,
                   label=f'σc,amm = {sigma_c_amm:.2f} MPa')
        ax2.axvline(sigma_s_amm, color='red', linestyle='--', alpha=0.5,
                   label=f'σs,amm = {sigma_s_amm:.2f} MPa')
        
        ax2.set_ylim(-h*0.1, h*1.1)
        ax2.set_xlabel('Tensione (MPa)')
        ax2.set_ylabel('Altezza (mm)')
        ax2.set_title('Diagramma Tensioni')
        ax2.legend()
        ax2.grid(True, alpha=0.2)
        ax2.axhline(x, color='red', linestyle=':', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def dominio_momento_sforzo_normale(
        base: float,
        altezza: float,
        area_armatura_inf: float,
        area_armatura_sup: float,
        sigma_c_amm: float,
        sigma_s_amm: float,
        copriferro: float = 30,
        n_punti: int = 50,
    ) -> Figure:
        """
        Crea il dominio momento-sforzo normale (diagramma di interazione).
        
        Args:
            base: Base sezione (mm)
            altezza: Altezza sezione (mm)
            area_armatura_inf: Area armatura inferiore (mm²)
            area_armatura_sup: Area armatura superiore (mm²)
            sigma_c_amm: Tensione ammissibile calcestruzzo (MPa)
            sigma_s_amm: Tensione ammissibile acciaio (MPa)
            copriferro: Copriferro (mm)
            n_punti: Numero di punti del dominio
            
        Returns:
            Figura matplotlib
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        d = altezza - copriferro - 15  # Altezza utile approssimata
        d_prime = copriferro + 15
        
        momenti = []
        sforzi_normali = []
        
        # Punto 1: Trazione pura
        N1 = -sigma_s_amm * (area_armatura_inf + area_armatura_sup) / 1000
        M1 = 0
        momenti.append(M1)
        sforzi_normali.append(N1)
        
        # Punto 2-4: Flessione semplice e composta
        for x_ratio in np.linspace(0.1, 1.5, n_punti):
            x = altezza * x_ratio / 3  # Posizione asse neutro variabile
            
            if x < altezza:
                # Sezione parzialmente compressa
                N = sigma_c_amm * base * x - sigma_s_amm * area_armatura_inf
                N = N / 1000  # kN
                
                M = sigma_c_amm * base * x * (d - x/3) + \
                    sigma_s_amm * area_armatura_sup * (d - d_prime)
                M = M / 1e6  # kNm
            else:
                # Sezione tutta compressa
                N = sigma_c_amm * base * altezza + \
                    sigma_s_amm * (area_armatura_inf + area_armatura_sup) * 0.5
                N = N / 1000
                
                M = sigma_c_amm * base * altezza * (altezza/2 - altezza/2) + \
                    sigma_s_amm * area_armatura_inf * (d - altezza/2)
                M = M / 1e6
            
            momenti.append(M)
            sforzi_normali.append(N)
        
        # Punto 5: Compressione centrata
        N5 = (sigma_c_amm * base * altezza + 
              sigma_s_amm * (area_armatura_inf + area_armatura_sup)) / 1000
        M5 = 0
        momenti.append(M5)
        sforzi_normali.append(N5)
        
        # Disegna dominio
        ax.plot(momenti, sforzi_normali, 'b-', linewidth=2, label='Dominio di rottura')
        ax.fill(momenti, sforzi_normali, alpha=0.2, color='blue')
        
        # Punti caratteristici
        ax.plot(M1, N1, 'ro', markersize=8, label='Trazione pura')
        ax.plot(M5, N5, 'go', markersize=8, label='Compressione centrata')
        
        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Momento flettente (kNm)', fontweight='bold')
        ax.set_ylabel('Sforzo normale (kN)', fontweight='bold')
        ax.set_title('Dominio Momento-Sforzo Normale\n(Diagramma di Interazione)', 
                    fontweight='bold', fontsize=12)
        ax.legend()
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def salva_grafico(fig: Figure, filepath: Path, dpi: int = 300) -> None:
        """
        Salva un grafico su file.
        
        Args:
            fig: Figura matplotlib
            filepath: Percorso file output
            dpi: Risoluzione in DPI
        """
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
