import os

from pywave.datasource import DataFile
from pywave.circuit import Circuit, Subcircuit, Signal, SweepSet
import pywave.signaltype as type

from pycircuit.post.cds import PSFResultSet

types = {}


class PSFFile(DataFile):
    """Class to represent Cadence PSF files"""

    @staticmethod
    def extensions():
        raise NotImplementedError

    @staticmethod
    def test(file_path):
        dir, file = os.path.split(file_path)
        try:
            prs = PSFResultSet(dir)
            del prs
            return True
        except:
            return False

    def __init__(self, file_path):
        DataFile.__init__(self, file_path)
        dir, file = os.path.split(file_path)
        self.name = dir.split(os.sep)[-1]
        self.prs = PSFResultSet(dir)
        self.rootItem = None

        # build hierarchical signal list
        self.circuit = Circuit(self.name, self)
        self.circuit._sweep_set = SweepSet([])
        self.circuit._sweep_set.add_point([])
        for key in self.prs.keys():
            currentSubckt = Subcircuit(key)
            self.circuit.add_subcircuit(currentSubckt)
            result = self.prs[key]
            top_circuit = currentSubckt
            for name in result.keys():
                currentSubckt = top_circuit
                levels = str(name).split(".")
                if len(levels) > 1:
                    for level in levels[:-1]:
                        try:
                            currentSubckt = currentSubckt[level]
                        except:
                            newSubckt = Subcircuit(level)
                            currentSubckt.add_subcircuit(newSubckt)
                            currentSubckt = newSubckt
                signal_full_name = str(key) + "___" + str(name)
                try:
                    indep_type = types['unknown']
                except KeyError:
                    indep_type = type.default
                indep_name = 'unknown'
                indep_full_name = signal_full_name + "____XValues"
                indep_signal = Signal(indep_name, indep_full_name, None, indep_type)
                indep_signal._set_parent(self.circuit)
                
                try:
                    signal_type = types['unknown']
                except KeyError:
                    signal_type = type.default
                signal = Signal(levels[-1], signal_full_name, indep_signal, signal_type)
                indep_signal._data_source_info['values'] = signal
                signal._data_source_info['set'] = key
                currentSubckt.add_signal(signal)

    def get_sweep_names(self):
        return []

    def get_sweep_data(self):
        return [[]]

    def get_data(self, signal):
        if signal.get_independent_signal() is None:
            values = signal._data_source_info['values']
            dep_signal = values
        else:
            dep_signal = signal
        
        set = dep_signal._data_source_info['set']
        result = self.prs[set]
        waveform = result[dep_signal.name]
        
        if signal.get_independent_signal() is None:
            return waveform.get_x()
        else:
            return waveform.get_y()
