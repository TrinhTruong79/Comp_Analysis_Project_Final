import numpy as np
from Circuit import Circuit
from NRSolver import NRSolver

circuit = Circuit("7-Bus System")

circuit.add_bus("Bus 1", 20.0, "Slack")
circuit.add_bus("Bus 2", 230.0, "PQ")
circuit.add_bus("Bus 3", 230.0, "PQ")
circuit.add_bus("Bus 4", 230.0, "PQ")
circuit.add_bus("Bus 5", 230.0, "PQ")
circuit.add_bus("Bus 6", 230.0, "PQ")
circuit.add_bus("Bus 7", 18.0, "PV")

circuit.add_transformer("T1", "Bus 1", "Bus 2", 0.00676, 0.0676)
circuit.add_transformer("T2", "Bus 6", "Bus 7", 0.00436, 0.05235)

circuit.add_transmission_line("L1", "Bus 2", "Bus 4", 0.001517, 0.009678, 0.0, 0.1413)
circuit.add_transmission_line("L2", "Bus 2", "Bus 3", 0.003791, 0.02420, 0.0, 0.3532)
circuit.add_transmission_line("L3", "Bus 3", "Bus 5", 0.003032, 0.01936, 0.0, 0.2825)
circuit.add_transmission_line("L4", "Bus 4", "Bus 6", 0.001517, 0.009678, 0.0, 0.1413)
circuit.add_transmission_line("L5", "Bus 5", "Bus 6", 0.005308, 0.03388, 0.0, 0.4946)
circuit.add_transmission_line("L6", "Bus 4", "Bus 5", 0.002274, 0.01452, 0.0, 0.2120)

circuit.add_generator("G1", "Bus 1", 1.0, 0.0)
circuit.add_generator("G2", "Bus 7", 1.0, 200.0)

circuit.add_load("Load 3", "Bus 3", 110.0, 50.0)
circuit.add_load("Load 4", "Bus 4", 100.0, 70.0)
circuit.add_load("Load 5", "Bus 5", 100.0, 65.0)

for gen in circuit.generators.values():
    gen.calc_p(circuit.settings)

for load in circuit.loads.values():
    load.calc_p(circuit.settings)
    load.calc_q(circuit.settings)

circuit.calc_ybus()
print("=" * 60)
print("YBUS MATRIX")
print("=" * 60)
print(circuit.ybus.to_string())

print("\n" + "=" * 60)
print("POWER FLOW SOLUTION")
print("=" * 60)

solver = NRSolver(circuit, mode="powerflow")
solver.solve()

print("\nFinal Bus Voltages and Angles:")
print(f"{'Bus':<10} {'V (pu)':<15} {'Delta (deg)':<15} {'Type':<10}")
print("-" * 50)
for bus_name, bus in circuit.buses.items():
    delta_deg = np.degrees(bus.delta)
    print(f"{bus_name:<10} {bus.vpu:<15.4f} {delta_deg:<15.4f} {bus.bus_type:<10}")