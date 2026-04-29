import numpy as np
from Jacobian import Jacobian
#no need to import circuit since circuit object is passed in as a parameter
class NRSolver:
    def __init__(self, circuit, mode = 'powerflow'):
        self.circuit = circuit
        #store the circuit reference
        self.jacobian = Jacobian(circuit)
        self.tol = 0.001
        self.max_iter = 50
        self.iter_count = 0
        self.mode = mode

    def initialize(self):
        #set the PV bus voltage from generator voltage setpoints
        for gen in self.circuit.generators.values():
            if gen.bus1_name in self.circuit.buses:
                bus = self.circuit.buses[gen.bus1_name]
                if bus.bus_type == "PV":
                    bus.vpu = gen.voltage_setpoint
    #set the flat start initial condition or the NR solver - all voltages at 1.0pu and all angles at 0.0pu
        for bus in self.circuit.buses.values():
        #loop through every bus in the circuit
            if bus.bus_type == "Slack":
                continue
            #skip the Slack bus

            bus.delta = 0.0
            #reset angle to 0.0 pu for all non-slack bus

            if bus.bus_type == "PQ":
                bus.vpu = 1.0
            #reset voltage to 1.0 pu PQ buses
            #PV buses are skipped here because their voltage magnitude are fixed by generator's voltage_setpoint and should never be reset to 1.0 pu

    def solve(self, faulted_bus_name = None, vf=1.0):
        if self.mode == "powerflow":
            self._solve_powerflow()
        #call _solve_powerflow() if mode is power flow; the same for the other 2 cases below
        elif self.mode == "fault":
            self._solve_fault(faulted_bus_name, vf)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

    def _solve_powerflow(self):
        buses = self.circuit.buses
        ybus = self.circuit.ybus
        #create 2 local variables for convenience instead of repeatedly writing self.circuit.buses and self.circuit.ybus throughout the method

        self.initialize()
        #set flat starts for all non-slack buses before the iterations begin
        for iter_count in range(self.max_iter):
        #with range(self.max_iter), iter_count will start from 0 to (max_iter - 1)
        #this iter_count is different from self.iter_count
            self.iter_count = iter_count
            #update the number of iter_count and store it in self.iter_count. That way we can show the number of iterations by calling NRsolver.iter_count (note that NRsolver is an object)
            voltages = {}
            for bus in buses.values():
                voltages[bus.name] = (bus.vpu, bus.delta)
            #build the voltages dictionary at the start of each iteration to capture all the current vpu and delta of all buses, used to calculate the power mismatch and Jacobian

            f = self.circuit.compute_power_mismatch(buses, ybus, voltages)
            #create power mismatch array f
            if np.max(np.abs(f)) < self.tol:
            #convergence check - take the maximum of all mismatch entries and compare against tolerance
                print (f"The problem is converged after {iter_count+1} iterations")
                #iter_count starts at 0
                for bus in buses.values():
                    print(f"{bus.name}: vpu={bus.vpu:.4f}, delta={bus.delta:.4f}")
                #print voltage and angle of all buses when converged
                return

            J = self.jacobian.calc_jacobian()
            #compute the Jacobian matrix

            delta_x = np.linalg.solve(J,f)
            #solve the linear system

            nP = len(self.jacobian.P_buses)
            #get the number of non-slack buses (N - 1) and split delta_x into 2 parts below
            delta_delta = delta_x[:nP]
            #first nP entries - angle correction for all non-slack buses
            delta_V = delta_x[nP:]
            #remaining part - voltage correction for all PQ buses

            for i, bus in enumerate(self.jacobian.P_buses):
                bus.delta += delta_delta[i]
            #update the angles for all non-slack buses using += as the angle correction is added to the current value
            for i, bus in enumerate(self.jacobian.Q_buses):
                bus.vpu += delta_V[i]
            #same as angle but for voltage of all PQ buses

        print(f"Did not converge within max iterations")
        #if the loop complete all max_iter iterations without converging, print a non-converge message

    def _solve_fault(self, faulted_bus_name, vf=1.0):
        if faulted_bus_name is None:
            raise ValueError(f"faulted_bus_name bust be provided for fault mode")
        if faulted_bus_name not in self.circuit.buses:
            raise ValueError(f"Bus {faulted_bus_name} is not found in circuit")
        #validate the faulted bus name
        self.circuit.calc_ybus()
        self.circuit.calc_zbus()
        #recompute the Ybus for the fault mode then compute the faulted Zbus
        i_fault = self.circuit.calc_fault_current(faulted_bus_name, vf)
        voltages = self.circuit.calc_bus_voltage_fault(faulted_bus_name, vf)

        print(f"Fault current at bus {faulted_bus_name}: {abs(i_fault):.4f} pu")
        print(f"Post-fault bus voltages:")
        for bus_name, voltage in voltages.items():
            print(f"Bus {bus_name}: {abs(voltage): .4f} pu")
        #print all the voltages after the fault occur at the faulted voltage

        return i_fault, voltages


















