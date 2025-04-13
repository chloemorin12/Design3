import numpy as np
import matplotlib.pyplot as plt

thermistor = np.full((256, 2), np.nan)
real_thermistor_positions = [
    [-6.25, -10.825317547305483], [-3.125, -10.825317547305483], [0.0, -10.825317547305483],
    [3.125, -10.825317547305483], [6.25, -10.825317547305483], [-7.8125, -8.118988160479113],
    [-4.6875, -8.118988160479113], [-1.5625, -8.118988160479113], [1.5625, -8.118988160479113],
    [4.6875, -8.118988160479113], [7.8125, -8.118988160479113], [-9.375, -5.412658773652741],
    [-6.25, -5.412658773652741], [-3.125, -5.412658773652741], [0.0, -5.412658773652741],
    [3.125, -5.412658773652741], [6.25, -5.412658773652741], [9.375, -5.412658773652741],
    [-10.9375, -2.7063293868263707], [-7.8125, -2.7063293868263707], [-4.6875, -2.7063293868263707],
    [-1.5625, -2.7063293868263707], [1.5625, -2.7063293868263707], [4.6875, -2.7063293868263707],
    [7.8125, -2.7063293868263707], [10.9375, -2.7063293868263707], [-12.5, 0.0], [-9.375, 0.0],
    [-6.25, 0.0], [-3.125, 0.0], [0.0, 0.0], [3.125, 0.0], [6.25, 0.0], [9.375, 0.0], [12.5, 0.0],
    [-10.9375, 2.7063293868263707], [-7.8125, 2.7063293868263707], [-4.6875, 2.7063293868263707],
    [-1.5625, 2.7063293868263707], [1.5625, 2.7063293868263707], [4.6875, 2.7063293868263707],
    [7.8125, 2.7063293868263707], [10.9375, 2.7063293868263707], [-9.375, 5.412658773652741],
    [-6.25, 5.412658773652741], [-3.125, 5.412658773652741], [0.0, 5.412658773652741],
    [3.125, 5.412658773652741], [6.25, 5.412658773652741], [9.375, 5.412658773652741],
    [-7.8125, 8.118988160479113], [-4.6875, 8.118988160479113], [-1.5625, 8.118988160479113],
    [1.5625, 8.118988160479113], [4.6875, 8.118988160479113], [7.8125, 8.118988160479113],
    [-6.25, 10.825317547305483], [-3.125, 10.825317547305483], [0.0, 10.825317547305483],
    [3.125, 10.825317547305483], [6.25, 10.825317547305483]]
liste_thermistor_values = [66,82,113,48,32,97,67,98,49,16,0,81,68,83,114,33,17,
                           1,65,69,84,99,50,34,18,2,112,70,85,100,115,51,35,19,
                           3,71,86,101,116,52,36,20,4,87,102,117,53,37,21,5,103,
                           118,54,38,22,6,119,55,39,23,7]

print(len(liste_thermistor_values))
def assign_thermistor_positions():
    for i in range(len(real_thermistor_positions)):
        position = liste_thermistor_values[i]
        thermistor[position] = real_thermistor_positions[i]
    return thermistor

allo = assign_thermistor_positions()
print(allo)

'''n = 120
binary_str = format(n, '08b')
print(binary_str)
print(binary_str[-4])

diameter = 25
radius = diameter / 2
hex_radius = radius / 8
x_vals = []
y_vals = []
y_shift = np.sqrt(3) * hex_radius
x_shift = 2 * hex_radius
rows = int(2 * radius / y_shift) * 2
cols = int(2 * radius / x_shift) * 2

for row in range(-rows // 2, rows // 2 + 1):
    for col in range(-cols // 2, cols // 2 + 1):
        x = col * x_shift + (row % 2) * hex_radius
        y = row * y_shift
        
        if x**2 + y**2 <= radius**2:
            x_vals.append(x)
            y_vals.append(y)

x_final = np.array(x_vals)
y_final = np.array(y_vals)

valeurs = np.vstack((x_final, y_final))
valeurs = valeurs.T.tolist()
#print(valeurs)

fig, ax = plt.subplots(figsize=(6,6))
ax.scatter(x_final, y_final, color='red', s=5, label='Hexagonal Points')
ax.add_patch(plt.Circle((0, 0), radius, color='blue', fill=False, linestyle='dashed', label='Circle Boundary'))
ax.set_xlim(-radius - 2, radius + 2)
ax.set_ylim(-radius - 2, radius + 2)
ax.set_aspect('equal')
ax.legend()
plt.title("Dense Hexagonal Grid Inside a Circle")
plt.xlabel("X (mm)")
plt.ylabel("Y (mm)")
plt.grid(True)
#plt.show()'''