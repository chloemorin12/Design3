import numpy as np
import matplotlib.pyplot as plt

# Circle parameters
diameter = 25  # mm
radius = diameter / 2

# Hexagonal grid parameters
hex_radius = radius / 8  # Adjust for higher density

# Generate hexagonal grid
x_vals = []
y_vals = []
y_shift = np.sqrt(3) * hex_radius
x_shift = 2 * hex_radius

rows = int(2 * radius / y_shift) * 2  # Increase density
cols = int(2 * radius / x_shift) * 2  # Increase density

for row in range(-rows // 2, rows // 2 + 1):
    for col in range(-cols // 2, cols // 2 + 1):
        x = col * x_shift + (row % 2) * hex_radius  # Offset every other row
        y = row * y_shift
        
        if x**2 + y**2 <= radius**2:  # Keep points inside the circle
            x_vals.append(x)
            y_vals.append(y)

# Convert to numpy arrays
x_final = np.array(x_vals)
y_final = np.array(y_vals)
print(x_final)
print(y_final)
print(len(x_final))
# Plot
fig, ax = plt.subplots(figsize=(6,6))
ax.scatter(x_final, y_final, color='red', s=5, label='Hexagonal Points')  # Singular points

ax.add_patch(plt.Circle((0, 0), radius, color='blue', fill=False, linestyle='dashed', label='Circle Boundary'))
ax.set_xlim(-radius - 2, radius + 2)
ax.set_ylim(-radius - 2, radius + 2)
ax.set_aspect('equal')
ax.legend()
plt.title("Dense Hexagonal Grid Inside a Circle")
plt.xlabel("X (mm)")
plt.ylabel("Y (mm)")
plt.grid(True)
plt.show()