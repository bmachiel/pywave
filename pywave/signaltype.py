import unit


class SignalType():
    def __init__(self, symbol, description, unit):
        self.symbol = symbol
        self.description = description
        self.unit = unit
        
    def unit(self):
        return self.unit
    
    def __repr__(self):
        return self.symbol


t = SignalType('t', 'time', unit.s)
f = SignalType('f', 'frequency', unit.Hz)
V = SignalType('V', 'voltage', unit.V)
T = SignalType('C', 'degrees Celcius', unit.degC)
Vm = SignalType('Vm', 'magnitude of voltage', unit.V)
Vr = SignalType('Vr', 'real part of voltage', unit.V)
Vi = SignalType('Vi', 'imaginary part of voltage', unit.V)
Vp = SignalType('Vp', 'phase of voltage', unit.deg)
I = SignalType('I', 'current', unit.A)
Im = SignalType('Im', 'magnitude of current', unit.A)
Ir = SignalType('Ir', 'real part of current', unit.A)
Ii = SignalType('Ii', 'imaginary part of current', unit.A)
Ip = SignalType('Ip', 'phase of current', unit.deg)
Spar = SignalType('S', 'S parameter', unit.none)
#Noise = SignalType('Noise', 'noise', unit.none)
#param = SignalType('param', 'parameter', unit.none)
#Stability = SignalType('Stability', 'stability factor', unit.none)
#NF = SignalType('NF', 'noise figure', unit.none)
#Zin = SignalType('Zin', 'input impedance', unit.Ohm)
Power = SignalType('Power', 'power', unit.W)
#sweep = SignalType('sweep', 'sweep variable', unit.none)

default = SignalType('', 'default', unit.none)
