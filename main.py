"""
Entry point for the Configurator suite. 
Usage:
    python main.py
"""

import os
from tools.configurator.app import RPGConfiguratorApp

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.abspath(__file__))
    app = RPGConfiguratorApp(root_dir)
    app.mainloop()
