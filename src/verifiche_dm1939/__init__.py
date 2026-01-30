"""
Verifiche Strutturali secondo DM 2229/1939
==========================================

Software per verifiche alle tensioni ammissibili di strutture in calcestruzzo armato
secondo il Regio Decreto Legge n. 2229 del 16 novembre 1939.

Teorie di riferimento: Santarella e Giangreco

AGGIORNATO: Supporta 8 geometrie di sezione con calcoli avanzati.
"""

__version__ = "0.2.0"
__author__ = "Daniele Carloni"

from verifiche_dm1939.core.config import Config
from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.materials.acciaio import Acciaio
from verifiche_dm1939.sections import (
    SezioneRettangolare,
    SezioneT,
    SezioneI,
    SezioneL,
    SezioneU,
    SezioneRettangolareCava,
    SezioneCircolare,
    SezioneCircolareCava,
)

__all__ = [
    "Config",
    "Calcestruzzo",
    "Acciaio",
    "SezioneRettangolare",
    "SezioneT",
    "SezioneI",
    "SezioneL",
    "SezioneU",
    "SezioneRettangolareCava",
    "SezioneCircolare",
    "SezioneCircolareCava",
]
