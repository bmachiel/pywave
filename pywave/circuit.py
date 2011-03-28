import signaltype

import numpy as np

class Circuit(dict):
    def __init__(self, title, data_source):
        dict.__init__(self)
        self.name = title
        self._data_source = data_source
        self._subcircuits = []
        self._signals = []
        self._opened = True
        self.tree_item_id = None
        self.selected = None
        self._sweep_set = None
        self._filter_regex = ''

    def add_subcircuit(self, subcircuit):
        self._subcircuits.append(subcircuit)
        self[subcircuit.name] = subcircuit
        subcircuit._set_parent(self)

    def add_signal(self, signal):
        self._signals.append(signal)
        self[signal.name] = signal
        signal._set_parent(self)

    def get_data_source(self):
        return self._data_source

    def get_subcircuits(self):
        return self._subcircuits

    def get_signal(self, full_name):
        separator = '.'
        levels = full_name.split(".")
        return NotImplementedError

    def get_signals(self):
        return self._signals
    
    def update(self, new_circuit):
        """Update this circuit to the data in new_circuit"""
        old_data_source = self._data_source
        self._data_source = new_datafile
        self._data_source.number = new_circuit._data_source.number
        self.update_sweep_set(new_circuit.get_sweep_set())
        self.update_subcircuit(new_circuit)

    def update_sweep_set(self, new_sweep_set):
        pass
    
    def update_subcircuit(self, new_subcircuit):
        """Update the given circuit with the new data held in new_circuit"""
        for new_subckt in new_circuit.get_subcircuits():
            try:
                subckt = circuit[new_subckt.name]
                self.update_subcircuit(subckt, new_subckt)
            except KeyError:
                circuit.add_subcircuit(new_subckt)
            # TODO: remove subcircuits that have disappeared
        for new_signal in new_circuit.get_signals():
            try:
                signal = circuit[new_signal.name]
                signal._values = {}
            except KeyError:
                circuit.add_signal(new_signal)
            # TODO: remove signals that have disappeared

    def update_clients(self):
        for subcircuit in self.get_subcircuits():
            subcircuit.update_clients()
        for signal in self.get_signals():
            signal.update_clients()

    def is_open(self):
        return self._opened

    def open(self):
        self._opened = True

    def close(self):
        self._opened = False


class Child(object):
    def __init__(self):
        self._parent = None

    def get_circuit(self):
        try:
            return self.get_parent().get_circuit()
        except AttributeError:
            return self.get_parent()

    def get_parent(self):
        return self._parent

    def _set_parent(self, parent):
        self._parent = parent


class Subcircuit(Circuit, Child):
    def __init__(self, name):
        Circuit.__init__(self, name, None)
        Child.__init__(self)
        self._parent = None
        self._opened = False


class Signal(Child):
    """Class representing a dependent or independent signal"""
    def __init__(self, name, full_name, independent_signal,
        signal_type=signaltype.default):
        Child.__init__(self)
        self.name = name
        self.full_name = full_name
        self._indep_signal = independent_signal
        self._values = {}
#        self._waveform = None
        self._traces = []
        self.type = signal_type
        self._data_source_info = {}
            # dict where the DataSource can store information
        self._clients = []
            # list of clients referencing this Signal

    def __repr__(self):
        return "%s %s" % (self.__class__, self.full_name)

    def _load_data(self):
        data_source = self.get_circuit().get_data_source()
        if self.get_circuit()._sweep_set is None:
            sweep_names = data_source.get_sweep_names()
            sweep_data = data_source.get_sweep_data()
            self.get_circuit()._sweep_set = SweepSet(sweep_names)
            for point in sweep_data:
                self.get_circuit()._sweep_set.add_point(point)
        data = data_source.get_data(self)
        for i, row in enumerate(data):
            sweep_point = self.get_circuit()._sweep_set._points[i]
            self._values[sweep_point] = row

    def add_client(self, client):
        """Make this Signal aware of client"""
        self._clients.append(client)
        
    def remove_client(self, client):
        """Remove client from the list of clients this Signal is aware of"""
        self._clients.remove(client)        

    def is_referenced(self):
        return len(self._clients) > 0

    def update_clients(self):
        """Make all clients update this signal"""
        if self._clients:
            self._load_data()
        for client in self._clients:
            client.update_signal(self)

    def get_independent_signal(self):
        """Return the independent signal this signal is a function of"""
        return self._indep_signal

    def get_values(self, sweep_point=None):
        if self.get_circuit()._sweep_set is None:
            self._load_data()
        if sweep_point is None:
            sweep_point = self.get_circuit()._sweep_set._points[0]
        if sweep_point not in self._values:
            self._load_data()
        return self._values[sweep_point]


class SignalClient(object):
    """Class representing objects that reference a Signal"""
    def __init__(self):
        pass
    
    def update_signal(self, signal):
        """Do whatever is needed when a signal has changed"""
        raise NotImplementedError    
    

class SweepSet(object):
    """Class representing a set of sweeped parameters"""
    def __init__(self, names):
        self._names = tuple(names)
        self._points = []

    def add_point(self, values):
        assert len(values) == len(self._names)
        self._points.append(SweepPoint(self, values))

    def find_point(self, values):
        for point in self._points:
            if tuple(point) == values:
                return point
        return None

    def __repr__(self):
        repr = " ".join("%8s" % name for name in self._names) + "\n"
        repr += "+--------+" + ("-" * 8 + "+") * (len(self._names) - 1)
        for point in self._points:
            repr +=  "\n" + " ".join("%8g" % value for value in point)
        return repr


class SweepPoint(tuple):
    """Class representing one sample in a SweepSet"""
    def __new__(cls, sweep_set, *args, **kwargs):
        return tuple.__new__(cls, *args, **kwargs)

    def __init__(self, sweep_set, *args, **kwargs):
        self._sweep_set = sweep_set

    def __eq__(self, other):
        return self._sweep_set == other._sweep_set and tuple.__eq__(self, other)

    def __ne__(self, other):
        return self._sweep_set != other._sweep_set or tuple.__ne__(self, other)

#    def __repr__(self):
#        return "%s %s in %s" % (self.__class__, tuple.__repr__(self), self._sweep_set)

    def __repr__(self):
        repr = " ".join("%8s" % name for name in self._sweep_set._names) + "\n"
        repr += "+--------+" + ("-" * 8 + "+") * (len(self._sweep_set._names) - 1)
        repr +=  "\n" + " ".join("%8g" % value for value in self)
        return repr

#~ class Waveform(self):
    #~ def __init__(self):

