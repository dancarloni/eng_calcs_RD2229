"""
Sections module - Geometria sezioni e armature.

AGGIORNATO: Include nuove geometrie complete.
"""

from .sezione_base import (
    SezioneBase, 
    Barra,
    Staffa,
    ProprietaGeometriche, 
    AsseNeutro
)

# Import nuove sezioni
from .sezione_rettangolare_new import SezioneRettangolare
from .sezione_t import SezioneT
from .sezione_i import SezioneI
from .sezioni_speciali import (
    SezioneL,
    SezioneU,
    SezioneRettangolareCava
)
from .sezione_circolare import (
    SezioneCircolare,
    SezioneCircolareCava
)

# Placeholder per compatibilità
FerroPiegato = None

__all__ = [
    'SezioneBase',
    'ProprietaGeometriche',
    'AsseNeutro',
    'Barra',
    'Staffa',
    'FerroPiegato',
    'SezioneRettangolare',
    'SezioneT',
    'SezioneI',
    'SezioneL',
    'SezioneU',
    'SezioneRettangolareCava',
    'SezioneCircolare',
    'SezioneCircolareCava',
]



