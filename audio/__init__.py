# Audio package

import os
import sys

# Garantir que o diretório raiz do projeto está no sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)