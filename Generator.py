class Generator:
    def __init__(self, name, bus1_name, voltage_setpoint, mw_setpoint, xpp = None, mva = None):
        if not isinstance(name, str) or not name.strip() or not isinstance(bus1_name, str) or not bus1_name.strip():
            raise ValueError (f"Name must be a valid or non-empty string")
        self.name = name.strip()
        self.bus1_name = bus1_name.strip()
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint
        self.p = None
        #placehoders for per-unit real power
        self.xpp = xpp
        #subtransient reactance, used for fault analysis
        self.mva = mva
        #the MVA of the generator, used for converting the xpp from machine base to system base

    def calc_p(self, settings):
        self.p = self.mw_setpoint/settings.sbase
        #only have real power since a generator can be treated as a PV bus in powerflow mode; no Q (reactive power) is specified

    def __repr__(self):
        return f"Generator(name={self.name}, bus={self.bus1_name}, voltage_setpoint={self.voltage_setpoint}, mw_setpoint={self.mw_setpoint}, p={self.p})"
