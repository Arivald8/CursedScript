"""
CursedScript Game Dev Kit.

Launch point for the entire app suite. 

Determines the project root dir and inits the main Tkinter app window. By
Ensures all tool modules can find their dependencies regardless of execution context.

The script creates a single instance of RPGConfiguratorApp, which orchestrates all
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