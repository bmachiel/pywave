from pywave.datasource import DataFile
from pywave.circuit import Circuit, Subcircuit, Signal
import numpy as np

import pywave.signaltype as type

from HSpiceOutput import HSPICEOutput
from HSpiceOutput import type as htype

types = {}

types[htype.t] = type.t
types[htype.f] = type.f
types[htype.V] = type.V
types[htype.C] = type.T
types[htype.Vm] = type.Vm
types[htype.Vr] = type.Vr
types[htype.Vi] = type.Vi
types[htype.Vp] = type.Vp
types[htype.I] = type.I
types[htype.Im] = type.Im
types[htype.Ir] = type.Ir
types[htype.Ii] = type.Ii
types[htype.Ip] = type.Ip
types[htype.I1] = type.I
types[htype.S11] = type.Spar
types[htype.S21] = type.Spar
types[htype.S12] = type.Spar
types[htype.S22] = type.Spar
types[htype.Spar] = type.Spar
types[htype.Noise] = type.default
types[htype.param] = type.default
types[htype.Stability] = type.default
types[htype.NF] = type.default
types[htype.Zin] = type.default
types[htype.Power] = type.Power
types[htype.sweep] = type.default


class HSPICEFile(DataFile):
    """Class to represent binary (post=1) HSPICE output (ac0, tr0, hb0, ss0, ls0, ...)"""

    @staticmethod
    def extensions():
        raise NotImplementedError

    @staticmethod
    def test(file_path):
        try:
            hspo = HSPICEOutput(file_path, True)
            del hspo
            return True
        except:
            return False

    def __init__(self, file_path):
        DataFile.__init__(self, file_path)
        self.hspo = HSPICEOutput(self.file_path, True)

        # build hierarcical signal list
        self.circuit = Circuit(self.hspo.title, self)
        indep_name = self.hspo.signalnames[0]
        indep_type = self.hspo.get_signal_type(0)
        indep_signal = Signal(indep_name, indep_name, None, indep_type)
        indep_signal._set_parent(self.circuit)
        for i in range(len(self.hspo.get_signal_names()[1:])):
            signal_name = self.hspo.get_signal_name(i+1)
            signal_type = types[self.hspo.get_signal_type(i+1)]
            currentSubckt = self.circuit
            if signal_type == type.V:
                node_name = signal_name[2:-1]
                levels = node_name.split(".")
                if len(levels) > 1:
                    for level in levels[:-1]:
                        try:
                            currentSubckt = currentSubckt[level]
                        except:
                            newSubckt = Subcircuit(level)
                            currentSubckt.add_subcircuit(newSubckt)
                            currentSubckt = newSubckt
                signal = Signal("v(" + levels[-1] + ")", signal_name, indep_signal, signal_type)
            else:
                signal = Signal(signal_name, signal_name, indep_signal, signal_type)
            currentSubckt.add_signal(signal)

    def get_sweep_names(self):
        return self.hspo.get_sweep_names()

    def get_sweep_data(self):
        return self.hspo.get_sweep_data()

    def get_data(self, signal):
        signal_index = self.hspo.get_signal_index(signal.full_name)
        return self.hspo.get_signal(signal_index)
    
#    def reload(self):
#        self.hspo = HSPICEOutput(self.file_path, True)
#        indep_name = self.hspo.signalnames[0]
#        indep_type = self.hspo.get_signal_type(0)
#        indep_signal = Signal(indep_name, indep_name, None, indep_type)
#        indep_signal._set_parent(self.circuit)
#        for i in range(len(self.hspo.get_signal_names()[1:])):
#            signal_name = self.hspo.get_signal_name(i+1)
#            signal_type = types[self.hspo.get_signal_type(i+1)]
#            print signal_name

#        self.circuit.update_clients()
