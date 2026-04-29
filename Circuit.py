from Bus import Bus
from Transformer import Transformer
from TransmissionLine import TransmissionLine
from Load import Load
from Generator import Generator
from Settings import Settings
import numpy as np
import pandas as pd
#import all the necessary classes and libraries
#np used to create zero matrix, invert the matrix, and return the power mismatch as a numpy array
class Circuit:
    def __init__(self, name):
        #only need circuit name as circuit acts as a container
        if not isinstance(name, str) or not name.strip():
            raise ValueError (f"Name must be a valid or non-empty string")
        self.name = name.strip()
        self.buses = {}
        self.transformers = {}
        self.transmission_lines = {}
        self.generators = {}
        self.loads = {}
        #initialize the empty dictionaries for each equipment class.
        #start empty and get populated whenever call the add methods
        self.ybus = None
        #placehoders for ybus matrix
        #start as None because it can't be computed until buses and equipments are added
        #get filled when call calc_ybus() method
        self.settings = Settings()
        #creat a Settings object and give the circuit access to the system base MVA and frequency
        self.zbus = None
        #same idea as ybus matrix.

    @staticmethod
    #doesn't use object (doesn't need anything from self), class, just live inside the class for organizational purposes or the utility functions relate to logic
    #instance method is the method that use 'self' when work with a specific object
    #class method is used when need to access or change class variables
    def _check_duplicate(component_dict, component_name, component_type):
        if component_name in component_dict:
        #if a name already exist in a dictionary -> raise value error
            raise ValueError (f"{component_type} name already exists : {component_name}")
            #print out something like: "Bus name already exists: bus1"
    #created to check name duplicates. Only access to the dictionaries and check the names after adding new objects; raise value error if any name is duplicated

    def add_bus(self, name, nominal_kv, bus_type):
        if not isinstance(name, str) or not name.strip():
            raise ValueError (f"Name must be a valid or non-empty string")
        name = name.strip()
        self._check_duplicate(self.buses, name, "Bus")
        bus = Bus(name, nominal_kv, bus_type)
        self.buses[name] = bus
        return bus
    #All add method follow the same structure: check valid name -> generate name -> check duplicate -> create an object -> store in the dictionary by name
    #"name" will become the key of the dictionary and is used to retrieve that bus
    #return an object so the object can access its attributes immediately without having to look it up in the dictionaries

    def add_transformer(self, name, bus1_name, bus2_name, r, x):
        if not isinstance(name, str) or not name.strip():
            raise ValueError (f"Name must be a valid or non-empty string")
        name = name.strip()
        self._check_duplicate(self.transformers, name, 'Transformer')
        transformer = Transformer(name, bus1_name, bus2_name, r, x)
        self.transformers[name] = transformer
        return transformer

    def add_transmission_line(self, name, bus1_name, bus2_name, r, x, g, b):
        if not isinstance(name,str) or not name.strip():
            raise ValueError (f"Name must be a valid or non-empty string")
        name = name.strip()
        self._check_duplicate(self.transmission_lines, name, 'Transmission_line')
        transmission_line = TransmissionLine(name, bus1_name, bus2_name, r, x, g, b)
        self.transmission_lines[name] = transmission_line
        return transmission_line

    def add_generator(self, name, bus1_name, voltage_setpoint, mw_setpoint, xpp = None, mva = None):
        if not isinstance(name, str) or not name.strip():
            raise ValueError (f"Name must be a valid or non-empty string")
        name = name.strip()
        self._check_duplicate(self.generators, name, 'Generator')
        generator = Generator(name, bus1_name, voltage_setpoint, mw_setpoint, xpp, mva)
        self.generators[name] = generator
        return generator

    def add_load(self, name, bus1_name, mw, mvar):
        if not isinstance(name, str) or not name.strip():
            raise ValueError (f"Name must be a valid or non-empty string")
        name = name.strip()
        self._check_duplicate(self.loads, name, 'Load')
        load = Load(name, bus1_name, mw, mvar)
        self.loads[name] = load
        return load

    def calc_ybus(self):
    #only need self -> use everything already stored in circuit
        bus_names = list(self.buses.keys())
        #get all bus names as a list -> use to label the DataFrame rows and columns
        n = len(self.buses)
        #"len" uses to get the number of the values in a dictionary, here is the number of buses, which defines the matrix size
        if n == 0:
            raise ValueError (f"No buses defined")
        #ensure dictionary is not empty
        y = np.zeros((n, n), dtype=complex)
        #use the numpy library to create a zero matrix with n rows and n columns, where n is the number of buses in buses dictionary
        #dtype=complex allows to store both real and imaginary parts of admittances, otherwise, only float can be stored in the matrix
        bus_map = {name: i for i, name in enumerate (self.buses.keys())}
        #map bus name to bus index; unpack each pair so i gets the number, name gets the bus name -> bus 1: 0; bus 2: 1; bus 3: 2; .....
        #this is called dictionary comprehension: build a new dictionary (bus_map dictionary) where name is the key and i is the value
        #the order of the bus_map dictionary depends on the order of the buses were added to self.buses
        def stamp_2bus_yprim(yprim, b1, b2):
        #b1 and b2 are the bus1_name and bus2_name parameters we pass in when create a transformer/transmission line object
        #in line 122 and 125, we can see what b1 and b2 exactly are (T.bus1_name, T.bus2_name,.....)
            if b1 not in bus_map or b2 not in bus_map:
                raise ValueError (f"Bus {b1} and {b2} are not defined")
            #make sure all the bus names are in bus_map dictionary
            i = bus_map[b1]
            j = bus_map[b2]
            #use dictionary comprehension (bus_map dictionary), where i, j are values (indices) and b1, b2 are the keys (bus names)

            y[i, i] += yprim.loc[b1, b1]
            y[i, j] += yprim.loc[b1, b2]
            y[j, i] += yprim.loc[b2, b1]
            y[j, j] += yprim.loc[b2, b2]
            #land these 4 values in the correct spots with respect to the corresponding bus names
            #loc is a DataFrame accessor that allows to access entries by labels (labels here are bus names - b1, b2) instead of by numbers
            #i -> b1; j -> b2
            #use "+=" to get the full Ybus accumulate contributions from all elements in the network

        for T in self.transformers.values():
            stamp_2bus_yprim(T.calc_yprim(), T.bus1_name, T.bus2_name)
        #stamp transformer's primitive admittance in the right place using the method just defined above
        #note the use of "+=" in the method

        for Tr in self.transmission_lines.values():
            stamp_2bus_yprim(Tr.calc_yprim(), Tr.bus1_name, Tr.bus2_name)
        #stamp transmission line's primitive admittance in the right place using the method just defined above
        #note the use of "+=" in the method
        self.ybus = pd.DataFrame(y, index=bus_names, columns=bus_names)
        #wrap the final ybus matrix (numpy matrix) in a pandas DataFrame, labels with bus names on rows and columns
        #easy to access entries in the matrix, example: circuit.ybus.loc["Bus 1", "Bus 2"] -> y12; or circuit.ybus.loc["Bus 3", "Bus 1"] -> y31

    def calc_ybus_fault(self):
    #calculate the ybus matrix in the fault mode
    #only use self, which means that the computed self.ybus and all the generators stored in self.generators will be used
        ybus_faulted = self.ybus.copy()
        #make a copy of the ybus matrix in the powerflow mode
        for gen in self.generators.values():
        #loop through all the generators in the generators dictionary -> the number of iterations equal to the number of generators
            if gen.xpp is not None and gen.mva is not None:
            #only process if the generator has both xpp and mva
            #get skipped in powerflow mode since both xpp and mva are None initially
                xpp_sys = gen.xpp * (self.settings.sbase / gen.mva)
                #convert xpp from the machine base to the system base
                y_shunt = 1 / (1j * xpp_sys)
                #convert reactance to shunt admittance
                ybus_faulted.loc[gen.bus1_name, gen.bus1_name] += y_shunt
                #stamp the generator's shunt admittance onto the diagonal of the faulted Ybus at the bus where the generator is connected
                #only stamp onto the diagonal since the generator is a shunt element that connect between a bus and ground, not between 2 buses
        return ybus_faulted
        #return the ybus_faulted instead of storing it as self.ybus_faulted because the zbus will use it immediately afterward so no need to store it permanently
    def calc_zbus(self):
    #no parameters require, only use the self.ybus already being computed from calc_ybus()
        ybus_fault = self.calc_ybus_fault()
        #call faulted ybus from calc_ybus_faulted
        zbus = np.linalg.inv(ybus_fault.values)
        #ybus_fault.values removes all the labels (bus names), only preserve the matrix
        #np.linalg.inv() compute the matrix inverse, which transfer from admittance to impedance
        bus_names = list(self.buses.keys())
        #create a list contain all the bus names in self.buses to use the DataFrame with bus names on rows and columns
        self.zbus = pd.DataFrame(zbus, index = bus_names, columns = bus_names)
        # same as self.ybus, easy to access entries in the matrix using "loc" as circuit.zbus.loc["Bus 1", "Bus 2"]
        return self.zbus
        #zbus will be used in calculating fault current and fault voltage so make sense when store it permanently in self.zbus

    def calc_fault_current(self, faulted_bus_name, vf=1.0):
    #vf - pre-fault voltage - at the faulted bus
    #vf = 1.0 by default to assume the voltage at all buses before the fault is 1.0pu
        znn = self.zbus.loc[faulted_bus_name, faulted_bus_name]
        #retrieve the diagonal element of Zbus matrix at the faulted bus using "loc"
        i_fault = vf/znn
        return i_fault

    def calc_bus_voltage_fault(self, faulted_bus_name, vf=1.0):
        znn = self.zbus.loc[faulted_bus_name, faulted_bus_name]
        voltages = {}
        #initialize an empty dictionary to store the post-fault voltage at every bus
        for bus_name in self.buses.keys():
        #loop through all buses (keys) in self.buses -> number of iterations equal to the number of buses
            zkn = self.zbus.loc[bus_name, faulted_bus_name]
            #retrieve the off-diagonal element in the Zbus matrix between bus k (current bus in the loop) and bus n (faulted bus)
            voltages[bus_name] = 1 - (zkn/znn) * vf
            #calculate bus voltages so bus_name is the key and voltage is the value of the voltages dictionary
        return voltages

    def compute_power_injection(self, bus, ybus, voltages):
        G = ybus.values.real #array of conductance (real part)
        B = ybus.values.imag #array of susceptance (imaginary part)
        #extract real and imaginary part of Ybus into 2 separate numpy arrays
        #note that ybus is in DataFrame, but ".values" strip the pandas label to get the raw numpy array first, then ".real" and ".imag" extract the respective parts

        Pi = 0.0
        Qi = 0.0
        #initalize P and Q accumulators; will be built up by the summation loop below

        bus_map = {name: idx for idx, name in enumerate(self.buses.keys())}
        #dictionary comprehension to get all bus indices in buses dictionary (bus name: index)
        i = bus_map[bus.name]
        #get the indices of the buses

        Vi = voltages[bus.name][0]
        delta_i = voltages[bus.name][1]
        #retrieve voltage magnitude and angle for bus i from the voltages dictionary; [0] gets vpu and [1] gets delta
        #it should be noted that voltages dictionary must be created before calling this method: voltages = {bus_name: (bus.vpu, bus.delta) for bus_name, bus in self.buses.items()}

        for j_name in self.buses.keys():
        #with each i bus, loop through every j bus in the system, including i = j
            j = bus_map[j_name]

            Vj = voltages[j_name][0]
            delta_j = voltages[j_name][1]
            #same as above, retrieve vpu and delta of bus j from voltages dictionary
            delta_ij = delta_i - delta_j
            #compute the angle difference
            Pi += abs(Vi)*abs(Vj)*(G[i,j]*np.cos(delta_ij)+B[i,j]*np.sin(delta_ij))
            Qi += abs(Vi)*abs(Vj)*(G[i,j]*np.sin(delta_ij)-B[i,j]*np.cos(delta_ij))
            #each iteration adds one term in the summation
            #use abs() here because Vi and Vj are complex numbers
        if bus.bus_type == "Slack":
            #No mismatch calculation required
            return Pi, Qi

        if bus.bus_type == "PQ":
            return Pi, Qi
        #return calculated Pi, Qi since this is PQ bus

        if bus.bus_type == "PV":
            return Pi, None
        #return only calculated Pi since V is fixed and Q is not specified for PV bus

        return None

    def compute_power_mismatch(self, buses, ybus, voltages):
        mismatch_P = []
        mismatch_Q = []
        #empty list to accumulate delta_P and delta_Q
        for bus_name, bus in buses.items():
        #loop through all buses (items - bus names + bus objects) in buses dictionary
            P_spec = 0.0
            Q_spec = 0.0
            #reset specified P and Q to zero at the start of each iteration, otherwise, they would keep accumulating across buses
            for gen_name, gen in self.generators.items():
            #loop through all the generators in generators dictionary
                if gen.bus1_name == bus.name:
                #if a generator object has bus1_name parameter same as name parameter of a bus -> add; else skip.
                    P_spec += gen.p
                    #note that generator doesn't have "q" attribute in both modes (powerflow and fault)

            for load_name, load in self.loads.items():
                if load.bus1_name == bus.name:
                #same as generator, check bus1_name of loads with name of buses
                    P_spec -= load.p
                    Q_spec -= load.q

            Pi, Qi = self.compute_power_injection(bus, ybus, voltages)
            #call the method comput_power_injection to get the calculated power (real and reactive power)

            if bus.bus_type == "Slack":
                continue
                #for Slack bus, P and Q are not specified, so no need to calculate power mismatch for Slack bus

            elif bus.bus_type == "PQ":
                mismatch_P.append(P_spec - Pi)
                mismatch_Q.append(Q_spec - Qi)
                #calculate the power mismatch with specified PQ and calculated PQ and add to the mismatch list created at the start of this method
                #".append" adds a new element to the end of the list each time it's called

            elif bus.bus_type == "PV":
                mismatch_P.append(P_spec - Pi)

        return np.array(mismatch_P + mismatch_Q)
        #turn to numpy array because the mismatch vector will get passed to np.linalg.solve(J, mismatch) in Newton-Raphson later. A List cannot use math operators.

    def __repr__(self):
        return (f"Circuit({self.name}, "
                f"buses={len(self.buses)}, "
                f"transformers={len(self.transformers)}, "
                f"transmission_lines={len(self.transmission_lines)}, "
                f"generators={len(self.generators)}, "
                f"loads={len(self.loads)})")







