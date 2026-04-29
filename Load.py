class Load:
    def __init__(self, name, bus1_name, mw, mvar):
        if not isinstance(name, str) or not name.strip() or not isinstance(bus1_name, str) or not bus1_name.strip():
            raise ValueError (f"Name must be a valid or non-empty string")
        self.name = name.strip()
        self.bus1_name = bus1_name.strip()
        self.mw = float(mw)
        self.mvar = float(mvar)
        self.p = None
        self.q = None
        #placehoders for per-unit values of real and reactive power
        #Start as None since they cannot be calculated yet, need the system's base MVA from a settings object

    def calc_p(self, settings):
        self.p = self.mw/settings.sbase
        #convert to per-unit

    def calc_q(self, settings):
        self.q = self.mvar/settings.sbase
        #convert to per-unit
        #note that a load bus is a PQ bus

    def __repr__(self):
        return f"Load(name={self.name}, bus={self.bus1_name}, mw={self.mw}, mvar={self.mvar}, p={self.p}, q={self.q})"
