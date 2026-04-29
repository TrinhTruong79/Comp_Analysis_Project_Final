import pandas as pd

class TransmissionLine:
    def __init__(self, name, bus1_name, bus2_name, r, x, g, b):
        if not isinstance(name, str) or not name.strip()or not isinstance(bus1_name, str) or not bus1_name.strip() or not isinstance(bus2_name, str) or not bus2_name.strip():
            raise ValueError(f"Name must be a valid or non-empty string")
        #Check transmission lines' names again
        self.name = name.strip()
        self.bus1_name = bus1_name.strip()
        self.bus2_name = bus2_name.strip()
        self.r = float(r)
        self.x = float(x)
        self.g = float(g)
        self.b = float(b)
        #Store all attributes

        z = complex(self.r, self.x)
        if z == 0:
            raise ValueError(f"Z cannot be zero")

        self.yseries = 1/z
        self.yshunt = complex(self.g, self.b)
        #Appear Yshunt since the transmission lines have shunt admittance, represent the leakage to ground along the lines

    def calc_yprim(self):
        y = self.yseries
        ys = self.yshunt
        b1 = self.bus1_name
        b2 = self.bus2_name

        data = [
            [y+ys/2, -y],
            [-y, y+ys/2]
        ]
        #ys/2 represents half the shunt admittance sitting at the end of the line (pi - model)
        return pd.DataFrame(data, index=[b1, b2], columns=[b1, b2])

    def __repr__(self):
        return f"TransmissionLine(name={self.name}, bus1={self.bus1_name}, bus2={self.bus2_name}, r={self.r}, x={self.x}, g={self.g}, b={self.b})"
