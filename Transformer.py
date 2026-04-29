import pandas as pd
#import pandas library to use DataFrame function
class Transformer:
    def __init__(self, name, bus1_name, bus2_name, r, x):
        if not isinstance(name, str) or not name.strip() or not isinstance(bus1_name, str) or not bus1_name.strip() or not isinstance(bus2_name, str) or not bus2_name.strip():
            raise ValueError (f"Name must be a valid or non-empty string")
        #Check if name of buses or transformers are str type or not; or if the names only contain space character after removing the white space (strip())

        self.name = name.strip()
        self.bus1_name = bus1_name.strip()
        self.bus2_name = bus2_name.strip()
        #.strip() removes any accidental leading/trailing (the beginning/the end) spaces from names
        self.x = float(x)
        self.r = float(r)
        #Automatically transfer other types of x and r to float type

        z = complex(self.r, self.x)
        if z==0:
            raise ValueError (f"Z cannot be 0")
        #Check if z value is 0 or not
        self.yseries = 1/z
        #The series impedance of the transformer, used to stamp into Ybus later
    def calc_yprim(self):
        #method to calculate the primary admittance matrix for the transformer
        y = self.yseries
        b1 = self.bus1_name
        b2 = self.bus2_name
        data = [
            [y, -y],
            [-y, y]
        ]
        #The diagonals are +yseries, the off-diagonals are -yseires; don't have yshunt
        return pd.DataFrame(data, index=[b1, b2], columns=[b1, b2])
        #DataFrame labels the rows and columns with bus name -> which bus corresponds to which row/column


    def __repr__(self):
        return f"Transformer(name={self.name},bus1_name={self.bus1_name}, bus2_name={self.bus2_name}, r={self.r}, x={self.x})"
    