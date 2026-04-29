from Bus import Bus
from Transformer import Transformer
from TransmissionLine import TransmissionLine
from Load import Load
from Generator import Generator

if __name__ == "__main__":
    bus1 = Bus('bus1', 20.0, "Slack")
    print(bus1.name, bus1.nominal_kv, bus1.bus_index, bus1.bus_type)
    bus2 = Bus('bus2', 230.0, "PV")
    print(bus2.name, bus2.nominal_kv, bus2.bus_index, bus2.bus_type)
    T1 = Transformer('T1', 'bus1', 'bus2', 0.01, 0.01)
    print(T1.name, T1.bus1_name, T1.bus2_name, T1.r, T1.x)
    Tr1 = TransmissionLine('Tr1', 'bus1', 'bus2', 0.01, 0.01, 0.02, 0.05)
    print(Tr1.name, Tr1.bus1_name, Tr1.bus2_name, Tr1.r, Tr1.x, Tr1.g, Tr1.b)
    L1  = Load('L1', 'bus1', 50.0, 30.0)
    print(L1.name, L1.bus1_name, L1.mw, L1.mvar)
    Gen1 = Generator('Gen1', 'bus1', 1.04, 50.0)
    print(Gen1.name, Gen1.bus1_name, Gen1.voltage_setpoint, Gen1.mw_setpoint)


