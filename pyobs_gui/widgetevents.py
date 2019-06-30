from PyQt5 import QtWidgets, QtCore
import inspect

import pyobs.events
from pyobs.comm import RemoteException
from pyobs_gui.qt.widgetevents import Ui_WidgetEvents


class WidgetEvents(QtWidgets.QWidget, Ui_WidgetEvents):
    def __init__(self, comm, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.comm = comm

        # loop all event types
        for name, cls in pyobs.events.__dict__.items():
            if isinstance(cls, type):
                # register event
                self.comm.register_event(cls, self._handle_event)

                # get c'tor
                ctor = getattr(cls, '__init__')
                sig = inspect.signature(ctor)
                params = [] if len(sig.parameters) < 2 else \
                    [p.name for p in sig.parameters.values() if str(p) != 'self']

                # build name
                name = '%s (%s)' % (cls.__name__, ', '.join(params))

                # add to combo
                self.comboEvent.addItem(name, cls)

    def _handle_event(self, event: pyobs.events.Event, sender: str):
        """Handle any incoming event.

        Args:
            event: Event itself.
            sender: Sender of event.
        """
        print("received event", event)

    @QtCore.pyqtSlot()
    def on_buttonSend_clicked(self):
        # get event class
        cls = self.comboEvent.itemData(self.comboEvent.currentIndex())

        # open dialog
        dlg = SendEventDialog(self.comm, cls)
        dlg.exec_()


class SendEventDialog(QtWidgets.QDialog):
    def __init__(self, comm, event: type, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)

        # save event type
        self._event = event
        self._comm = comm

        # add layout
        layout = QtWidgets.QFormLayout()
        self.setLayout(layout)

        # add label with event name
        title = QtWidgets.QLabel(event.__name__)
        layout.addWidget(title)

        # get c'tor and its params
        ctor = getattr(event, '__init__')
        sig = inspect.signature(ctor)

        # add input for every param
        self._widgets = {}
        for p in sig.parameters:
            if p != 'self':
                # create widget
                if sig.parameters[p].annotation == int:
                    widget = QtWidgets.QSpinBox()
                    widget.setMinimum(-1e5)
                    widget.setMaximum(1e5)
                elif sig.parameters[p].annotation == float:
                    widget = QtWidgets.QDoubleSpinBox()
                    widget.setMinimum(-1e5)
                    widget.setMaximum(1e5)
                else:
                    widget = QtWidgets.QLineEdit()

                # store widget
                self._widgets[p] = widget

                # add to layout
                layout.addRow(p, widget)

        # add dialog button box
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._send_event)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _send_event(self):
        """Actually send event."""

        # collect values
        values = {}
        for name, widget in self._widgets.items():
            if isinstance(widget, QtWidgets.QLineEdit):
                values[name] = widget.text()
            else:
                values[name] = widget.value()

        # create event and send it
        event = self._event(**values)
        self._comm.send_event(event)

        # accept dialog
        self.accept()