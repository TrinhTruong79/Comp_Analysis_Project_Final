class Bus:
    _bus_counter = 0
    #This is a class-level attribute, belong to the class itself, not to any individual bus instance, all objects share this one counter
    #The underscore _ has the meaning of "intended for internal use"
    def __init__(self, name, nominal_kv, bus_type):
        #Everything in the parenthesis are the parameters that need to pass in when create a Bus object with the exact order
         valid_type = ["Slack","PQ","PV"]
        #List all bus types
         if bus_type not in valid_type:
             raise ValueError(f"Invalid bus type: {bus_type}")
        #Check if the bus has the available type
         self.name = name
         self.nominal_kv = nominal_kv
         self.bus_type = bus_type
        #All the attributes of a bus object
        #Voltage here is the actual voltage
         self.vpu = 1.0
         self.delta = 0.0
        #vpu is the normalized voltage, as compared to the base voltage of the system
        #Start point for Newton-Raphson solver, every bus starts with 1.0pu in voltage and 0.0pu in angle.
        #The solver will update these iteratively until converged
         self.bus_index = Bus._bus_counter
         Bus._bus_counter += 1
        #Update the index of the bus when each bus bus is created, start from 0, and 1, and 2, and so on....

    def __repr__(self):
        return f"Bus(name={self.name}, nominal_kv={self.nominal_kv}, bus_index={self.bus_index}, bus_type={self.bus_type})"
    #Control what can see when a bus object is printed.
