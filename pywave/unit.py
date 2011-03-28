
class SignalUnit():
    def __init__(self, symbol, description):
        self.symbol = symbol
        self.description = description

    def __repr__(self):
        return self.symbol


s = SignalUnit('s', 'seconds')
Hz = SignalUnit('Hz', 'hertz')

V = SignalUnit('V', 'volts')
A = SignalUnit('A', 'amperes')
degC = SignalUnit('deg C', 'degrees Celcius')
deg = SignalUnit('deg', 'degrees')
rad = SignalUnit('rad', 'radians')
Ohm = SignalUnit('Ohm', 'ohms')
W = SignalUnit('W', 'watts')
none = SignalUnit('', 'no unit')
