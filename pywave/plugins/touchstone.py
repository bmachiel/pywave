from pywave.datasource import DataFile
from pywave.circuit import Circuit, Subcircuit, Signal, SweepSet
from pywave import signaltype

from nport import touchstone


class TouchstoneFile(DataFile):
    """Class to represent Touchstone files"""

    @staticmethod
    def extensions():
        raise NotImplementedError

    @staticmethod
    def test(file_path):
        try:
            tstone = touchstone.read(file_path)
            del tstone
            return True
        except:
            return False

    def __init__(self, file_path):
        DataFile.__init__(self, file_path)
        self._touchstone = touchstone.read(self.file_path, True)
        self.rootItem = None

        # build hierarchical signal list
        self.circuit = Circuit("Touchstone", self)
        indep_name = "frequency"
        indep_type = signaltype.f
        indep_signal = Signal(indep_name, indep_name, None, indep_type)
        indep_signal._set_parent(self.circuit)
        for i in range(self._touchstone.ports):
            for j in range(self._touchstone.ports):
                signal_name = "S(%d,%d)" % (i + 1, j + 1)
                signal_type = signaltype.Spar
                signal = Signal(signal_name, signal_name, indep_signal, signal_type)
                signal._data_source_info['port1'] = i + 1
                signal._data_source_info['port2'] = j + 1
                self.circuit.add_signal(signal)
                
    def get_data(self, signal):
        if signal.get_independent_signal() is None:
            return [self._touchstone.freqs.tolist()]
        else:
            port1 = signal._data_source_info['port1']
            port2 = signal._data_source_info['port2']
            return [self._touchstone.get_parameter(port1, port2).tolist()]
