"""
Entry point principale per l'avvio dell'applicazione desktop DataRecon.
"""

import sys
from pathlib import Path

# Aggiunge la radice del progetto al PYTHONPATH se eseguito direttamente
radice = Path(__file__).resolve().parent.parent
if str(radice) not in sys.path:
    sys.path.insert(0, str(radice))

from PySide6.QtWidgets import QApplication
from CODICE.maschera import FinestraPrincipale


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DataRecon")
    app.setOrganizationName("Simone Mariotti")
    
    finestra = FinestraPrincipale()
    finestra.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
