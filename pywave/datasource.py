import os

class DataSource(object):
    """Base class for sources that hold waveform data"""

    def __init__(self):
        self.circuit = None
        self.name = None
        self.number = None

    def get_sweep_names(self):
        """Return a list of the names of the sweep variables"""
        return []

    def get_sweep_data(self):
        """Return all combinations of sweep variables"""
        return [[]]

    def get_data(self, name):
        """Return an ..."""
        raise NotImplementedError

    def get_circuit(self):
        """Return the top level circuit"""
        return self.circuit


class DataFile(DataSource):
    """Base class for files that hold waveform data"""

    @staticmethod
    def extensions():
        """Return a regex that matches the filename extensions supported by this class"""
        raise NotImplementedError

    @staticmethod
    def test(filename):
        """Test whether the given file is supported by this class"""
        raise NotImplementedError

    def __init__(self, file_path):
        DataSource.__init__(self)
        self.file_path = os.path.abspath(file_path)
        self.file_date = os.path.getmtime(self.file_path)
        self.name = os.path.basename(file_path)
        
    def changed(self):
        """Test whether the file has changed since it was last loaded"""
        return os.path.getmtime(self.file_path) != self.file_date

    def reload(self):
        """Reload the file from disk and update all plots"""
        new_datafile = type(self)(self.file_path)
        new_circuit = new_datafile.get_circuit()
        self.circuit.update(new_circuit)
        self.file_date = os.path.getmtime(self.file_path)
        self.circuit.update_clients()
