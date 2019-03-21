import threading
import logging

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox


log = logging.getLogger(__name__)


class BaseWidget(QtWidgets.QWidget):
    _show_error = pyqtSignal(str)
    _enable_buttons = pyqtSignal(list, bool)

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        self._show_error.connect(self.show_error)
        self._enable_buttons.connect(self.enable_buttons)

    def run_async(self, method, *args, **kwargs):
        threading.Thread(target=self._async_thread, args=(method, *args), kwargs=kwargs).start()

    def _async_thread(self, method, *args,  disable=None, **kwargs):
        # make disable an empty list or a list of widgets
        disable = [] if disable is None else [disable] if not hasattr(disable, '__iter__') else disable

        # disable widgets
        self._enable_buttons.emit(disable, False)

        # call method
        try:
            method(*args, **kwargs)
        except Exception as e:
            log.exception("error")
            self._show_error.emit(str(e))
        finally:
            # enable widgets
            self._enable_buttons.emit(disable, True)

    def show_error(self, message):
        QMessageBox.warning(self, 'Error', message)

    def enable_buttons(self, widgets, enable):
        [w.setEnabled(enable) for w in widgets]