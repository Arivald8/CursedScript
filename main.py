"""
Entry point for the Configurator suite. 

Creates a single instance of RPGConfiguratorApp, which orchestrates all
editor components (map editor, theme editor, project configurator) within one
interface, then starts the Tkinter event loop to handle user interactions.

Usage:
    python main.py
"""

import os
from tools.configurator.app import RPGConfiguratorApp

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.abspath(__file__))
    app = RPGConfiguratorApp(root_dir)
    app.mainloop()