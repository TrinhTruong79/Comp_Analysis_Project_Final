import numpy as np

class SensAna:
    def __init__(self, circuit, solver):
        self.circuit = circuit
        #create a circuit object from Circuit class
        self.solver = solver
        #create a solver object from NRSolver class

        self.solver.solve()
        #call method solver() from NRSolver class and run base case

        self.J = self.solver.jacobian.calc_jacobian()
        #extract converged Jacobian matrix

        self.P_buses = self.solver.jacobian.P_buses
        self.Q_buses = self.solver.jacobian.Q_buses
        #create bus lists for Jacobian matrix calculation

        self.J_inv = None
        self.dDelta_dP = None
        self.dDelta_dQ = None
        self.dV_dP = None
        self.dV_dQ = None
        #sensitivity matrices - updated later

        self.delta_P = None
        self.delta_Q = None
        # initialize load perturbances

        self.compute_sensitivity()
        #automatically compute sensitivity at initialization

    def compute_sensitivity(self):
        self.J_inv = np.linalg.inv(self.J)
        #compute the inverse J matrix from the converged Jacobian matrix

        nP = len(self.P_buses)
        #define number of non-slack buses

        self.dDelta_dP = self.J_inv[:nP, :nP]
        #same dimension as J1
        self.dDelta_dQ = self.J_inv[:nP, nP:]
        #same dimension as J2
        self.dV_dP = self.J_inv[nP:, :nP]
        #same dimension as J3
        self.dV_dQ = self.J_inv[nP:, nP:]
        #same dimension as J4

        return self.dDelta_dP, self.dDelta_dQ, self.dV_dP, self.dV_dQ

    def perturb_bus(self, bus_name, delta_P = 0.0, delta_Q = 0.0):
        if bus_name not in self.circuit.buses:
            raise ValueError(f"Bus {bus_name} not found in circuit")

        bus = self.circuit.buses[bus_name]
        #get object bus to access bus_type and bus_name attributes

        if bus.bus_type == "Slack":
            raise ValueError(f"Cannot perturb Slack bus: {bus_name}")

        if bus.bus_type == "PV" and delta_Q != 0.0:
            raise ValueError(f"Cannot perturb PV bus: {bus_name} - voltage is fixed")

        self.delta_P = delta_P
        self.delta_Q = delta_Q
        #store perturbation values

        nP = len(self.P_buses)
        nQ = len(self.Q_buses)
        delta_f = np.zeros(nP + nQ)
        #create vector delta_f to store perturbation values

        P_bus_name = [b.name for b in self.P_buses]
        Q_bus_name = [b.name for b in self.Q_buses]
        #find position of bus in P_bus and Q_bus

        if bus_name in P_bus_name:
            i = P_bus_name.index(bus_name)
            delta_f[i] = delta_P
        #stamp delta_P in the correct position in P_bus array

        if bus_name in Q_bus_name:
            j = Q_bus_name.index(bus_name)
            delta_f[nP + j] = delta_Q
        #stamp delta_Q in the correct position in Q_bus array

        delta_x = self.J_inv@delta_f
        #compute delta_x from J inversed and delta_f

        delta_delta = delta_x[:nP]
        delta_v = delta_x[nP:]
        #get the values of voltage angles and magnitudes from delta_x

        results = {}
        #store actual post-perturbation values for all buses

        #slack bus is fixed and never change
        for b in self.circuit.buses.values():
            if b.bus_type == "Slack":
                results[b.name] = {
                    "vpu_new": b.vpu,
                    "delta_new": b.delta
                }

        #for P buses, angles update for all P buses, voltages only update for PQ buses
        for i, b in enumerate(self.P_buses):
            if b.name not in results:
                if b.bus_type == "PQ":
                    q_idx = Q_bus_name.index(b.name)
                    #find index in Q_buses for voltage update since delta_v = delta_x[np:]
                    results[b.name] = {
                        "vpu_new": b.vpu + delta_v[q_idx],
                        "delta_new": b.delta + delta_delta[i]
                    }
                    #PQ buses have new voltage magnitudes and angles
                elif b.bus_type == "PV":
                    results[b.name] = {
                        "vpu_new": b.vpu,
                        "delta_new": b.delta + delta_delta[i]
                    }
                    #PV buses have fixed voltage magnitudes, only update voltage angles
        return results













