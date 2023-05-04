import pprint

# import from vocab.ai / baserow

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

# load config
config = mw.addonManager.getConfig(__name__)

def start_vocabai_import() -> None:
    pprint.pprint(config)
    # get the number of cards in the current collection, which is stored in
    # the main window
    cardCount = mw.col.cardCount()
    # show a message box
    showInfo("Card count: %d" % cardCount)

import_action = QAction("Import from Vocab.Ai", mw)
qconnect(import_action.triggered, start_vocabai_import)
mw.form.menuTools.addAction(import_action)