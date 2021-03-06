import logging
from PyQt5.QtCore import pyqtSignal

from pyobs.interfaces import ICooling
from pyobs_gui.basewidget import BaseWidget
from .qt.widgetcooling import Ui_WidgetCooling


log = logging.getLogger(__name__)


class WidgetCooling(BaseWidget, Ui_WidgetCooling):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, parent=None):
        BaseWidget.__init__(self, parent=parent, update_func=self._update)
        self.setupUi(self)
        self.module = module    # type: ICooling
        self.comm = comm        # type: Comm

        # status
        self._status = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonApply.clicked.connect(self.set_cooling)

    def _update(self):
        # get status
        self._status = self.module.get_cooling_status().wait()

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self):
        if self._status is not None:
            # enable myself
            self.setEnabled(True)

            # split values
            enabled, set_point, power = self._status

            # set it
            if enabled:
                self.labelStatus.setText('N/A' if set_point is None else 'Set=%.1f°C' % set_point)
                self.labelPower.setText('N/A' if power is None else '%d%%' % power)
            else:
                self.labelStatus.setText('N/A' if power is None else 'OFF')
                self.labelPower.clear()

    def set_cooling(self):
        # get enabeld and setpoint temperature
        enabled = self.checkEnabled.isChecked()
        temp = self.spinSetPoint.value()

        # send it
        self.module.set_cooling(enabled, temp).wait()
