import objects

def exp1():
    params = objects.load_params()
    sim = objects.Simulation(params,"domyślne parametry")
    sim.run()
    sim.animate()

def exp2():
    params = objects.load_params()
    params["heater_placement"] = [2,5, 1]
    params["heater_dimensions"] = [0.1, 0.1]
    params["heater_power"] = 250
    sim = objects.Simulation(params,"co jeśli grzejnik dać na środku?")
    sim.run()
    sim.animate()

def exp3():
    params = objects.load_params()
    params["heater_placement"] = [1, 2.3]
    params["heater_dimensions"] = [0.4, 0.05]
    sim = objects.Simulation(params,"co jeśli grzejnik dać przy ścianie i blisko okna?")
    sim.run()
    sim.animate()

#wybieramy eksperyment
def exp():
    exp1()
