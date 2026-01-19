# CursedScript
## Curses-Powered Engine for Terminal Based Games
#### !README will be updated as the project progresses!
At the moment, including only a tkinter based editor, and a basic directory strucure. This will be used to configure a game of your choice/making.

main.py is currently the configurator/editor.

## Current Directory Structure

```
CursedScript/
├── engine
├── games
│   └── sample_quest
│       ├── assets
│       ├── maps
│       ├── scripts
│       └── config.json
├── tools
├── .gitignore
├── LICENSE
├── main.py
├── README.md
└── test_editor.py
```

## Editor/Configurator

Editor is using a vertical navigation sidebar with the main content changing on the right. 

For the moment, includes **CoreConfigView** and **MapEditorView**.

* **CoreConfigView** allows to set the game metadate, as well as resolution settings and colour palette.

* **MapEditorView** exposes the tile system, map layers, region definitions and spawn points. 

## Testing Strategy

Using pytest and pytest-mock.

* For setup, the app boots up once before the first test. 
* For execution, test functions run sequentially against that same running app instance.
* For teardown, the app is destroyed only after the last test finishes. 

Tkinter applications are stateful. If we run 5 tests, we don't want the App from Test 1 interfering with Test 2. If we use a default pytest fixture scope (defaults to function) to create a fresh **RPGConfiguratorApp** before every single test function, and destroy it immediatelly, we might run into a `_tkinter.TclError: couldn't read file ... auto.tcl` (I tried...).

On Windows, the Tcl interpreter powering Tkinter often fails to shut down cleanly or re-initialise rapidly in the same process. After a few cycles, it loses track of its internal library paths (init.tcl), causing a crash... For that reason, we're changing the scope of the fixture. Instead of creating a new app for every test, we create one app instance for the entire test file, run all tests against it, and destroy it at the end.

Note that `app.mainloop()` is never used. It creates an infinite loop that waits for user clicks. If we put that in a test, the test will hang forever. Using `app.update()` in the fixture instead, which processes any pending "draw" events (creating window, calculating geometry etc.) so that widgets exist in memory for us to inspect.

**test_editor.py** covers three layers of reliability:

* L1: Just checking that the app doesn't crash on startup:
    * Using test_app_initialisation, checking app.title() and isinstance(app, tk.Tk) to confirm that the Tcl interpreter loaded, the window manager accepted the window, and the constructor finished without throwing an exception. 

* L2: Verifying that the UI elements exist in memory:
    * Using test_page_layout_content, we crawl the Tkinter widget tree with winfo_children(). To check: Go to Map Editor obj, list its children, filter for LabelFrames, check if there are x entries, and check if the first one says "Tile System". If `.pack()` or `.grid()` was missed, this will catch it. 

* L3: Ensuring that user actions trigger the correct internal logic:
    * Simulating the event rather than the hardware click. Instead of checking click at coordinates (x, x), we call `app.nav_tree.selection_set("map")` and trigger the handler `on_nav_select`. We then asser the internal state, e.g. `app.nav_tree.selection() == "map".

Since we share one app instance, we follow these rules to avoid flaky tests:

* Reset state. If a test replies on the app being in a specific state (e.g. being one the "Core" tab), set that state explicitly at the start of the test. Do not assume the previous test left it there.

```
def test_something_on_core_tab(app):
    # FORCE the state you need
    app.nav_tree.selection_set("core")
    app.on_nav_select(None)

    # Now run assertions
    assert
```

* Call `.update()`. Tkinter is lazy. If you tell it to create a widget, it often waits until the next "idle" moment to actually calculate the geometry/pixel. In the fixture, we called root.update(). If we add complex tests later, we may need to call app.update() inside of the test function immediatelly after making a change. 

* Testing look and feel. It's hard to test "is this button red" using pytest login. Checking if the style configuration object contains `foreground="red"` is good. Checking if a pixel at (10, 10) is red is bad. 

## Tests

```
platform win32 -- Python 3.12.4, pytest-9.0.2, pluggy-1.6.0
rootdir: \CursedScript
plugins: anyio-4.6.2.post1, mock-3.15.1
collected 6 items

test_editor.py 
......                                                                                           
[100%]

=== 6 passed in 0.55s ===
```






