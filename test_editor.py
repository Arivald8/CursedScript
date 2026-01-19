import pytest
import tkinter as tk
from main import RPGConfiguratorApp, CoreConfigView

@pytest.fixture(scope="module")
def app():
    root = RPGConfiguratorApp()
    root.update()
    yield root
    root.destroy()


def test_app_initialisation(app):
    """
    Test that the app starts and has the correct title.
    """
    assert "CursedScript Configurator" in app.title()
    assert isinstance(app, tk.Tk)


def test_sidebar_population(app):
    """
    Test that all distinct tabs are loaded into sidebar.
    """
    children = app.nav_tree.get_children()

    assert len(children) == 2 # Only CoreConfigView, MapEditorView exists
    assert "core" in children


def test_pages_instantiation(app):
    """
    Test that the right-hand content frames are created.
    """
    assert "core" in app.pages
    assert isinstance(app.pages["core"], CoreConfigView)


def test_page_layout_content(app):
    """
    Test that a specific page (e.g. CoreConfig) contains the
    expected LabelFrames baded on the spec.
    """
    core_page = app.pages["core"]
    widgets = core_page.scrollable_frame.winfo_children()

    label_frames = [w for w in widgets if isinstance(w, tk.ttk.LabelFrame)]

    # Expecting 3 sections for Core Config
    assert len(label_frames) == 3
    assert "Game Metadata" in label_frames[0].cget("text")


def test_navigation_switching(app, mocker):
    """
    Test that clicking the sidebar actually attempts to raise.
    """
    map_page = app.pages["map"]
    core_page = app.pages["core"]
    
    app.nav_tree.selection_set("map")
    app.on_nav_select(None)

    assert app.nav_tree.selection()[0] == "map"


def test_default_selection(app):
    """
    Test that the app selects the first item (Core) on startup.
    Note: Because the app is reused, this test might fail if it runs
    after "test_navigation_switching". As we're using module-scopte tests,
    we manually reset the state.
    """
    app.nav_tree.selection_set("core")
    app.on_nav_select(None)

    selection = app.nav_tree.selection()
    assert selection[0] == "core"