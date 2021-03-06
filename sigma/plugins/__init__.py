# Utilities
from . import utils

# Game Related
from . import games

# Search and Media
from . import searches

# NSFW Modules
from . import nsfw

# Japanese Learning and Specific Modules
from . import nihongo

# Final Order Specific Modules
from . import finalo

# Miscellaneous
from . import misc

# Project Polaris Sonata
from . import polaris


__all__ = [
    'utils',
    'games',
    'searches',
    'nsfw',
    'nihongo',
    'finalo',
    'misc',
    'polaris'
]

pluglist = []
pluglist += utils.pluglist
pluglist += games.pluglist
pluglist += searches.pluglist
pluglist += nsfw.pluglist
pluglist += nihongo.pluglist
pluglist += finalo.pluglist
pluglist += misc.pluglist
pluglist += polaris.pluglist
