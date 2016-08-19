from kano.webapp import WebApp

from kano_updater.ui.paths import WEBPAGE_URL, ICON_PATH

class ChangesDialog(WebApp):
    def __init__(self):
        super(ChangesDialog, self).__init__()

        self._index = WEBPAGE_URL

        self._title = _("Changes")
        self._app_icon = ICON_PATH

        self._decoration = True
        self._centered = True
        self._maximized = False

        self._width = 800
        self._height = 600

if __name__ == '__main__':
    win = ChangesDialog()
    win.run()
