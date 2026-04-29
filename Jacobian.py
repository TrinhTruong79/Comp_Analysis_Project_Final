import numpy as np

class Jacobian:
    def __init__(self, circuit):
    #only need 1 parameter: a fully built circuit object. So make sure to have this object fully built before calling Jacobian
        self.circuit = circuit
        #store the circuit object reference so other methods in this class can access it via self.circuit
        self.N = len(circuit.buses)
        #"len()" give the total number of the buses in buses dictionary - all buses of the system
        self.P_buses = [bus for bus in circuit.buses.values() if bus.bus_type != "Slack"]
        #a list comprehension - build a list to store all non-slack buses
        self.Q_buses = [bus for bus in circuit.buses.values() if bus.bus_type == "PQ"]
        #also a list comprehension - build a list of only PQ buses
        self.NPV = len(self.P_buses) - len(self.Q_buses)
        #number of PV buses
        self.NPQ = len(self.Q_buses)
        self.size = 2*self.N - 2 - self.NPV
        #the total size of the Jacobian matrix
        self.J = None
        #placehoder for Jacobian matrix, start with None and get filled when calc_jacobian() is called

    def calc_jacobian(self):

        Y = self.circuit.ybus.values
        #".values" remove the DataFrame label and extract the numpy array of Ybus, allow to access the entries by integer index like Y[k, n]
        bus_map = {name: idx for idx, name in enumerate(self.circuit.buses.keys())}
        #dictionary comprehension

        J1 = np.zeros((self.N - 1, self.N - 1))
        J2 = np.zeros((self.N - 1, self.NPQ))
        J3 = np.zeros((self.NPQ, self.N - 1))
        J4 = np.zeros((self.NPQ, self.NPQ))
        #initialize 4 zero submatrices for J1, J2, J3, J4

        for i, k_bus in enumerate(self.P_buses):
        #outer loop, iterate through all non-slack buses (N - 1); for each bus k, retrieve the vpu and delta attributes of that bus
        #note that i is the row index of J1 matrix
            Vk = k_bus.vpu
            delta_k = k_bus.delta
            for j, n_bus in enumerate(self.P_buses):
            #inner loop, iterate through all non-slack buses (N - 1)
            #j is the column index of J1 matrix
                Vn = n_bus.vpu
                delta_n = n_bus.delta
                k = bus_map[k_bus.name]
                n = bus_map[n_bus.name]
                #k and n are the indices of Y bus matrix and are different from i and j, which are the indices of J1 matrix
                #k, n of Ybus include slack bus but i, j of J1 don't
                Ykn_mag = np.abs(Y[k,n])
                Ykn_theta = np.angle(Y[k,n])
                #extract the magnitude and angle of the complex Ybus entry Ykn

                if k != n:
                    J1[i,j] = Vk * Ykn_mag * Vn * np.sin(delta_k - delta_n - Ykn_theta)
                #off-diagonal element for k != n
                else:
                #diagonal element when k == n
                    sum_J1 = 0.0
                    #initialize sum_J1, all diagonal elements start at 0, or sum_J1 will be reset to 0 when start calculating a new diagonal element
                    for m_bus in self.circuit.buses.values():
                    #loop through all buses including Slack bus since n starts at 1 following the equation
                        m = bus_map[m_bus.name]
                        if m != k:
                            Ykm_mag = np.abs(Y[k, m])
                            Ykm_theta = np.angle(Y[k, m])
                            Vm = m_bus.vpu
                            delta_m = m_bus.delta
                            sum_J1 += Ykm_mag * Vm * np.sin(delta_k - delta_m - Ykm_theta)
                            #accumulate the value of J1 after each iteration
                    J1[i, j] = -Vk * sum_J1
            for j, n_bus in enumerate(self.Q_buses):
            #inner loop for J2 that iterate through all PQ buses (NPQ)
            #same outer loop as J1 since J1 and J2 have the same number of rows (N - 1)
                delta_n = n_bus.delta
                k = bus_map[k_bus.name]
                n = bus_map[n_bus.name]
                Ykn_mag = np.abs(Y[k, n])
                Ykn_theta = np.angle(Y[k, n])
                if k != n:
                #off-diagonal element
                    J2[i, j] = Vk * Ykn_mag * np.cos(delta_k - delta_n - Ykn_theta)
                else:
                #diagonal element
                    sum_J2 = 0.0
                    for m_bus in self.circuit.buses.values():
                        m = bus_map[m_bus.name]
                        Ykm_mag = np.abs(Y[k, m])
                        Ykm_theta = np.angle(Y[k, m])
                        Vm = m_bus.vpu
                        delta_m = m_bus.delta
                        sum_J2 += Ykm_mag * Vm * np.cos(delta_k - delta_m - Ykm_theta)
                    Ykk_mag = np.abs(Y[k, k])
                    Ykk_theta = np.angle(Y[k, k])
                    J2[i, j] = Vk * Ykk_mag * np.cos(Ykk_theta) + sum_J2
        for i, k_bus in enumerate(self.Q_buses):
        #outer loop switches to the number of Q buses since the number of rows now are NPQ
        #i is still the index of row
        #other steps are the same as J1 and J2, just the difference in the number of rows and columns
            Vk = k_bus.vpu
            delta_k = k_bus.delta
            for j, n_bus in enumerate(self.P_buses):
                Vn = n_bus.vpu
                delta_n = n_bus.delta
                k = bus_map[k_bus.name]
                n = bus_map[n_bus.name]
                Ykn_mag = np.abs(Y[k, n])
                Ykn_theta = np.angle(Y[k, n])
                if k != n:
                    J3[i, j] = -Vk * Ykn_mag * Vn * np.cos(delta_k - delta_n - Ykn_theta)
                else:
                    sum_J3 = 0.0
                    for m_bus in self.circuit.buses.values():
                        m = bus_map[m_bus.name]
                        if m != k:
                            Ykm_mag = np.abs(Y[k, m])
                            Ykm_theta = np.angle(Y[k, m])
                            Vm = m_bus.vpu
                            delta_m = m_bus.delta
                            sum_J3 += Ykm_mag * Vm * np.cos(delta_k - delta_m - Ykm_theta)
                    J3[i, j] = Vk * sum_J3
            for j, n_bus in enumerate(self.Q_buses):
                delta_n = n_bus.delta
                k = bus_map[k_bus.name]
                n = bus_map[n_bus.name]
                Ykn_mag = np.abs(Y[k, n])
                Ykn_theta = np.angle(Y[k, n])
                if k != n:
                    J4[i, j] = Vk * Ykn_mag * np.sin(delta_k - delta_n - Ykn_theta)
                else:
                    sum_J4 = 0.0
                    for m_bus in self.circuit.buses.values():
                        m = bus_map[m_bus.name]
                        Vm = m_bus.vpu
                        delta_m = m_bus.delta
                        Ykm_mag = np.abs(Y[k, m])
                        Ykm_theta = np.angle(Y[k, m])
                        sum_J4 += Ykm_mag * Vm * np.sin(delta_k - delta_m - Ykm_theta)
                    Ykk_mag = np.abs(Y[k, k])
                    Ykk_theta = np.angle(Y[k, k])
                    J4[i, j] = -Vk * Ykk_mag * np.sin(Ykk_theta) + sum_J4
        self.J = np.block([[J1, J2],
                            [J3, J4]])
        #assemble the full Jacobian matrix from the 4 submatrices
        return self.J
        #store the result in self.J and return it
        #can be used directly the return value or access later via jacobian.J










