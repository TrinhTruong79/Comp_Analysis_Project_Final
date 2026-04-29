import numpy as np
from Bus import Bus
Bus._bus_counter = 0
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

circuit.add_generator("G1", "Bus 1", 1.0, 0.0, xpp=0.12, mva=100.0)
circuit.add_generator("G2", "Bus 7", 1.0, 200.0, xpp=0.12, mva=200.0)

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
print("FAULTED YBUS")
print("=" * 60)
ybus_fault = circuit.calc_ybus_fault()
print(ybus_fault.to_string())

print("\n" + "=" * 60)
print("ZBUS MATRIX")
print("=" * 60)
zbus = circuit.calc_zbus()
print(zbus.to_string())

print("\n" + "=" * 60)
print("FAULT ANALYSIS RESULTS")
print("=" * 60)

fault_solver = NRSolver(circuit, mode="fault")

for bus_name in circuit.buses.keys():
    print(f"\n{'=' * 50}")
    print(f"THREE-PHASE BOLTED FAULT AT {bus_name}")
    print(f"{'=' * 50}")

    # fault current
    i_fault = circuit.calc_fault_current(bus_name, vf=1.0)
    print(f"Fault current: {abs(i_fault):.4f} pu")
    print(f"               {abs(i_fault) * circuit.settings.sbase / 20:.4f} kA (at 20kV base)")

    # post-fault voltages
    voltages = circuit.calc_bus_voltage_fault(bus_name, vf=1.0)
    print(f"\nPost-fault bus voltages:")
    print(f"{'Bus':<10} {'V (pu)':<15} {'V (kV)':<15}")
    print("-" * 40)
    for vbus_name, voltage in voltages.items():
        vbase = circuit.buses[vbus_name].nominal_kv
        print(f"{vbus_name:<10} {abs(voltage):<15.4f} {abs(voltage) * vbase:<15.4f}")

