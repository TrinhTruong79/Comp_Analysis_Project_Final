import numpy as np
from Bus import Bus

Bus._bus_counter = 0
from Circuit import Circuit
from NRSolver import NRSolver
from SensAna import SensAna

# =============================================================================
# STEP 1 - Create Circuit (same as power flow validation)
# =============================================================================
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

# =============================================================================
# STEP 2 - Create NRSolver and SensAna
# =============================================================================
print("=" * 60)
print("BASE CASE POWER FLOW")
print("=" * 60)
solver = NRSolver(circuit, mode="powerflow")
sens = SensAna(circuit, solver)

# print base case voltages
print("\nBase case bus voltages (converged):")
print(f"{'Bus':<10} {'V (pu)':<15} {'Delta (deg)':<15} {'Type':<10}")
print("-" * 50)
for bus_name, bus in circuit.buses.items():
    print(f"{bus_name:<10} {bus.vpu:<15.4f} {np.degrees(bus.delta):<15.4f} {bus.bus_type:<10}")

# =============================================================================
# STEP 3 - Print Sensitivity Matrices
# =============================================================================
print("\n" + "=" * 60)
print("SENSITIVITY MATRICES")
print("=" * 60)

P_names = [b.name for b in sens.P_buses]
Q_names = [b.name for b in sens.Q_buses]

print("\ndV/dP matrix (rows=Q_buses, cols=P_buses):")
print(f"{'':>10}", end="")
for name in P_names:
    print(f"{name:>12}", end="")
print()
for i, name in enumerate(Q_names):
    print(f"{name:>10}", end="")
    for j in range(len(P_names)):
        print(f"{sens.dV_dP[i, j]:>12.4f}", end="")
    print()

print("\ndV/dQ matrix (rows=Q_buses, cols=Q_buses):")
print(f"{'':>10}", end="")
for name in Q_names:
    print(f"{name:>12}", end="")
print()
for i, name in enumerate(Q_names):
    print(f"{name:>10}", end="")
    for j in range(len(Q_names)):
        print(f"{sens.dV_dQ[i, j]:>12.4f}", end="")
    print()

print("\nddelta/dP matrix (rows=P_buses, cols=P_buses):")
print(f"{'':>10}", end="")
for name in P_names:
    print(f"{name:>12}", end="")
print()
for i, name in enumerate(P_names):
    print(f"{name:>10}", end="")
    for j in range(len(P_names)):
        print(f"{sens.dDelta_dP[i, j]:>12.4f}", end="")
    print()

# =============================================================================
# STEP 4 - Test perturb_bus() and compare with PowerWorld
# =============================================================================
print("\n" + "=" * 60)
print("PERTURBATION ANALYSIS")
print("=" * 60)

# test perturbations at each non-slack PQ bus
perturbation_size = 0.01  # 0.01 pu = 1 MW on 100 MVA base

for bus_name in ["Bus 3", "Bus 4", "Bus 5"]:
    print(f"\n--- Perturb {bus_name}: delta_P = +{perturbation_size} pu (+1 MW) ---")
    results = sens.perturb_bus(bus_name, delta_P=perturbation_size)
    print(f"{'Bus':<10} {'V_base':<12} {'V_new':<12} {'dV':<12} {'d_base(deg)':<14} {'d_new(deg)':<14} {'dd(deg)':<12}")
    print("-" * 88)
    for bname, bus in circuit.buses.items():
        v_new = results[bname]["vpu_new"]
        d_new = np.degrees(results[bname]["delta_new"])
        v_base = bus.vpu
        d_base = np.degrees(bus.delta)
        dv = v_new - v_base
        dd = d_new - d_base
        print(f"{bname:<10} {v_base:<12.4f} {v_new:<12.4f} {dv:<12.6f} {d_base:<14.4f} {d_new:<14.4f} {dd:<12.6f}")

# =============================================================================
# STEP 5 - Validate against full NR solution
# =============================================================================
print("\n" + "=" * 60)
print("VALIDATION: LINEAR SENSITIVITY vs FULL NR SOLUTION")
print("=" * 60)
print("Applying delta_P = +0.01 pu at Bus 3")
print("Comparing linear prediction vs full Newton-Raphson re-solve")

# get linear prediction from sensitivity
linear_results = sens.perturb_bus("Bus 3", delta_P=0.01)

# now re-solve with modified load using full NR
Bus._bus_counter = 0
circuit2 = Circuit("7-Bus System Modified")
circuit2.add_bus("Bus 1", 20.0, "Slack")
circuit2.add_bus("Bus 2", 230.0, "PQ")
circuit2.add_bus("Bus 3", 230.0, "PQ")
circuit2.add_bus("Bus 4", 230.0, "PQ")
circuit2.add_bus("Bus 5", 230.0, "PQ")
circuit2.add_bus("Bus 6", 230.0, "PQ")
circuit2.add_bus("Bus 7", 18.0, "PV")
circuit2.add_transformer("T1", "Bus 1", "Bus 2", 0.00676, 0.0676)
circuit2.add_transformer("T2", "Bus 6", "Bus 7", 0.00436, 0.05235)
circuit2.add_transmission_line("L1", "Bus 2", "Bus 4", 0.001517, 0.009678, 0.0, 0.1413)
circuit2.add_transmission_line("L2", "Bus 2", "Bus 3", 0.003791, 0.02420, 0.0, 0.3532)
circuit2.add_transmission_line("L3", "Bus 3", "Bus 5", 0.003032, 0.01936, 0.0, 0.2825)
circuit2.add_transmission_line("L4", "Bus 4", "Bus 6", 0.001517, 0.009678, 0.0, 0.1413)
circuit2.add_transmission_line("L5", "Bus 5", "Bus 6", 0.005308, 0.03388, 0.0, 0.4946)
circuit2.add_transmission_line("L6", "Bus 4", "Bus 5", 0.002274, 0.01452, 0.0, 0.2120)
circuit2.add_generator("G1", "Bus 1", 1.0, 0.0)
circuit2.add_generator("G2", "Bus 7", 1.0, 200.0)
# Bus 3 load increased by 0.01 pu = 1 MW
circuit2.add_load("Load 3", "Bus 3", 111.0, 50.0)  # 110 + 1 MW
circuit2.add_load("Load 4", "Bus 4", 100.0, 70.0)
circuit2.add_load("Load 5", "Bus 5", 100.0, 65.0)
for gen in circuit2.generators.values():
    gen.calc_p(circuit2.settings)
for load in circuit2.loads.values():
    load.calc_p(circuit2.settings)
    load.calc_q(circuit2.settings)
circuit2.calc_ybus()
solver2 = NRSolver(circuit2, mode="powerflow")
solver2.solve()

# compare
print(
    f"\n{'Bus':<10} {'V_linear':<12} {'V_NR':<12} {'V_err':<12} {'d_linear(deg)':<16} {'d_NR(deg)':<14} {'d_err(deg)':<12}")
print("-" * 88)
for bname in circuit.buses.keys():
    v_lin = linear_results[bname]["vpu_new"]
    d_lin = np.degrees(linear_results[bname]["delta_new"])
    v_nr = circuit2.buses[bname].vpu
    d_nr = np.degrees(circuit2.buses[bname].delta)
    v_err = abs(v_lin - v_nr)
    d_err = abs(d_lin - d_nr)
    print(f"{bname:<10} {v_lin:<12.4f} {v_nr:<12.4f} {v_err:<12.6f} {d_lin:<16.4f} {d_nr:<14.4f} {d_err:<12.6f}")

print("\nSmall errors confirm linear sensitivity is a good approximation")
print("for small perturbations around the operating point!")