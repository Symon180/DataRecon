"""
Script di cattura screenshot automatica per la documentazione di DataRecon.

Genera in modalità headless (senza schermo) le anteprime grafiche ad alta risoluzione
della finestra principale sia in Tema Chiaro sia in Tema Scuro, salvandole in `docs/`.
"""

import os
import sys
from pathlib import Path

# Aggiunge la radice del progetto al PYTHONPATH
radice = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(radice))

# Forza Qt a funzionare senza server grafico X11 / Wayland
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from CODICE.maschera import FinestraPrincipale


def cattura():
    app = QApplication(sys.argv)
    cartella_docs = Path("docs")
    cartella_docs.mkdir(parents=True, exist_ok=True)

    # 1. Screenshot Tema Chiaro
    finestra_light = FinestraPrincipale(tema_scuro=False)
    finestra_light.carica_scenario_esempio()
    finestra_light.show()
    app.processEvents()

    pix_light = finestra_light.grab()
    path_light = cartella_docs / "screenshot_light.png"
    pix_light.save(str(path_light), "PNG")
    print(f"Salvato screenshot tema chiaro in: {path_light}")

    # 2. Screenshot Tema Scuro
    finestra_dark = FinestraPrincipale(tema_scuro=True)
    finestra_dark.carica_scenario_esempio()
    finestra_dark.show()
    app.processEvents()

    pix_dark = finestra_dark.grab()
    path_dark = cartella_docs / "screenshot_dark.png"
    pix_dark.save(str(path_dark), "PNG")
    print(f"Salvato screenshot tema scuro in: {path_dark}")

    finestra_light.close()
    finestra_dark.close()
    del finestra_light
    del finestra_dark
    app.processEvents()


if __name__ == "__main__":
    cattura()
