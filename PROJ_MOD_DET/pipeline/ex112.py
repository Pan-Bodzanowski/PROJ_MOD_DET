import objects

def exp1():
    params = objects.load_params()
    sim = objects.Simulation(params)
    sim.run()
    sim.animate()

def exp2():
    params = objects.load_params()
    sim = objects.Simulation(params)
    sim.run(40,140)
    sim.animate()

def exp3():
    params = objects.load_params()
    sim = objects.Simulation(params)
    sim.run(0,70)
    sim.animate()

def exp():
    exp3()