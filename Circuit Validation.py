from Circuit import Circuit
from Settings import Settings

circuit1 = Circuit("Test Circuit")

print(circuit1.name)
print(type(circuit1.name))
print(circuit1.buses)
print(type(circuit1.buses))
print(circuit1.transformers)
print(circuit1.transmission_lines)
print(circuit1.generators)
print(circuit1.loads)

circuit1.add_bus("Bus 1", 20.0, "PQ")
circuit1.add_bus("Bus 2", 230.0, "PQ")
print(list(circuit1.buses.keys()))
print(circuit1.buses["Bus 1"].name, circuit1.buses["Bus 1"].nominal_kv, circuit1.buses["Bus 1"].bus_type)
print(circuit1.buses["Bus 2"].name, circuit1.buses["Bus 2"].nominal_kv, circuit1.buses["Bus 2"].bus_type)

circuit1.add_transformer("T1", "Bus 1", "Bus 2", 0.01, 0.02)
print(list(circuit1.transformers.keys()))
print(circuit1.transformers["T1"].name, circuit1.transformers["T1"].bus1_name, circuit1.transformers["T1"].bus2_name, circuit1.transformers["T1"].r, circuit1.transformers["T1"].x)
print(circuit1.transformers["T1"].yseries)
print(circuit1.transformers["T1"].calc_yprim())

circuit1.add_transmission_line("Tr1", "Bus1", "Bus2", 0.01, 0.02, 0.02, 0.03)
print(list(circuit1.transmission_lines.keys()))
print(circuit1.transmission_lines["Tr1"].bus1_name, circuit1.transmission_lines["Tr1"].bus2_name, circuit1.transmission_lines["Tr1"].r, circuit1.transmission_lines["Tr1"].x, circuit1.transmission_lines["Tr1"].g, circuit1.transmission_lines["Tr1"].b)
print(circuit1.transmission_lines["Tr1"].yseries, circuit1.transmission_lines["Tr1"].yshunt)
print(circuit1.transmission_lines["Tr1"].calc_yprim())

settings = Settings()
print(settings.freq, settings.sbase)

circuit1.add_generator("Gen1", "Bus 1", 1.04, 70.0)
circuit1.generators["Gen1"].calc_p(settings)
print(list(circuit1.generators.keys()))
print(circuit1.generators["Gen1"].name, circuit1.generators["Gen1"].bus1_name, circuit1.generators["Gen1"].voltage_setpoint, circuit1.generators["Gen1"].mw_setpoint, circuit1.generators["Gen1"].p)

circuit1.add_load("L1","Bus 2", 50.0, 30.0)
circuit1.loads["L1"].calc_p(settings)
circuit1.loads["L1"].calc_q(settings)
print(list(circuit1.loads.keys()))
print(circuit1.loads["L1"].name, circuit1.loads["L1"].bus1_name, circuit1.loads["L1"].mw, circuit1.loads["L1"].mvar, circuit1.loads["L1"].p, circuit1.loads["L1"].q)

print(circuit1.buses)
print(type(circuit1.buses))
print(circuit1.transformers)
print(circuit1.transmission_lines)
print(circuit1.generators)
print(circuit1.loads)


