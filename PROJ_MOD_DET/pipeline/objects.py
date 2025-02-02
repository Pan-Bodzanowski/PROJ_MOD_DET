import json
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.patches as patches
import matplotlib.animation as animation

def load_params(filename="PROJ_MOD_DET/data.json"):
    with open(filename, "r") as file:
        return json.load(file)

class Room:
    def __init__(self, params):
        self.length, self.width = params["room_dimensions"]
        self.corridor_width = params["corridor_width"]
        self.total_length = self.length + self.corridor_width
        self.h = params["space_step"]
        
        self.nx = int(self.total_length / self.h) + 1
        self.ny = int(self.width / self.h) + 1
        self.alpha = params["thermal_conductivity"]
        self.dt = params["time_step"]
        
        self.temperature = np.ones((self.ny, self.nx)) * params["initial_temperature"]
        
        self.window_start, self.window_end = [int(h / self.h) for h in params["window_position"]]
        self.door_x = int(self.length / self.h)
        self.door_start, self.door_end = [int(h / self.h) for h in params["door_position"]]
    
    def apply_boundary_conditions(self, Tout):
        self.temperature[self.window_start:self.window_end, 0] = Tout
        
        self.temperature[:self.window_start, 0] = self.temperature[:self.window_start, 1]
        self.temperature[self.window_end:, 0] = self.temperature[self.window_end:, 1]
        self.temperature[:, -1] = self.temperature[:, -2]
        self.temperature[-1, :] = self.temperature[-2, :]
        self.temperature[0, :] = self.temperature[1, :]
        
        for i in range(self.ny):
            if i < self.door_start or i > self.door_end:
                self.temperature[i, self.door_x] = self.temperature[i, self.door_x - 1]
            else:
                avg_temp = (self.temperature[i, self.door_x - 1] + self.temperature[i, self.door_x + 1]) / 2
                self.temperature[i, self.door_x] = avg_temp

    def update_temperature(self):
        new_temp = self.temperature.copy()
        for i in range(1, self.ny - 1):
            for j in range(1, self.nx - 1):
                new_temp[i, j] = self.temperature[i, j] + self.alpha * self.dt / self.h**2 * (
                    self.temperature[i+1, j] + self.temperature[i-1, j] +
                    self.temperature[i, j+1] + self.temperature[i, j-1] - 4 * self.temperature[i, j])
        self.temperature = new_temp

class Heater:
    def __init__(self, params):
        self.power = params["heater_power"]
        self.rho = params["air_density"]
        self.c = params["specific_heat_capacity"]
        self.width = params["heater_dimensions"][0]
        self.height = params["heater_dimensions"][1]
        self.area = self.width * self.height
        self.heat_contribution = (self.power * params["time_step"]) / (self.rho * self.area * self.c) 
        
    def calculate_heating_energy(self):
        """Oblicza energię wydzieloną przez grzejnik w danym czasie."""
        energy = self.power * self.rho * self.area * self.c * self.heat_contribution
        return energy

    def place_heater(self, room, x, y):
        self.position = (min(max(x, 1), room.nx - 2), min(max(y, 1), room.ny - 2))

    def heat_room(self, room):
        hx, hy = self.position
        width_in_grid = int(self.width / room.h)
        height_in_grid = int(self.height / room.h)
        for i in range(hy - height_in_grid, hy + height_in_grid + 1):
            for j in range(hx - width_in_grid, hx + width_in_grid + 1):
                if 0 <= i < room.ny and 0 <= j < room.nx:
                    room.temperature[i, j] += self.heat_contribution

class Simulation:
    def __init__(self, params, title="Przewodnictwo cieplne"):
        self.params = params
        self.room = Room(params)
        self.heater = Heater(params)
        self.heater.place_heater(self.room, int(params["heater_placement"][0] / params["space_step"]), 
                                 int(params["heater_placement"][1] / params["space_step"]))
        self.dt = params["time_step"]
        self.T = params["simulation_time"]
        self.t_steps = int(self.T / self.dt)
        self.Tout = np.linspace(params["window_temperature"][0], params["window_temperature"][1], self.t_steps)
        self.snapshots = []
        self.title = title
        self.total_energy = 0

    def run(self, offstart=0, offend=0):
        for t in tqdm(range(self.t_steps)):
            if t * self.dt < offstart or t * self.dt >= offend:
                self.heater.heat_room(self.room)
            self.room.update_temperature()
            self.room.apply_boundary_conditions(Tout=self.Tout[t])
            if t % self.params["animation_step"] == 0 or t == self.t_steps - 1:
                self.snapshots.append(self.room.temperature.copy())

            self.total_energy += self.heater.calculate_heating_energy()

    def animate(self):
        fig, ax = plt.subplots()
        img = ax.imshow(self.snapshots[0], cmap='hot', origin='lower', vmin=15, vmax=40, extent=[0, self.room.total_length, 0, self.room.width])
        plt.colorbar(img, label="Temperatura (°C)")
        ax.set_title(self.title)

        ax.add_patch(patches.Rectangle((0, 0), self.room.total_length, self.room.width, fill=False, edgecolor='pink', linewidth=4))
        ax.add_patch(patches.Rectangle((self.room.length, 0), 0, self.room.door_start * self.room.h, fill=False, edgecolor='pink', linewidth=2))
        ax.add_patch(patches.Rectangle((self.room.length, self.room.door_end * self.room.h), 0, self.room.width - self.room.door_end * self.room.h, fill=False, edgecolor='pink', linewidth=2))
        ax.add_patch(patches.Rectangle((0, self.room.window_start * self.room.h), 0, (self.room.window_end - self.room.window_start) * self.room.h, fill=False, edgecolor='blue', linewidth=4))

        def update(frame):
            img.set_array(self.snapshots[frame])
            return img,

        ani = animation.FuncAnimation(fig, update, frames=len(self.snapshots), interval=50, blit=False, repeat=False)
        plt.show()

        print(f"Całkowita energia zużyta przez grzejnik: {self.total_energy} J")
