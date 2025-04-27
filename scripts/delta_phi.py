import random
from datetime import datetime

# Generate a random phi value (example logic)
phi_value = random.uniform(0.5, 1.5)

# Get current UTC timestamp
timestamp = datetime.utcnow().isoformat() + 'Z'

# Print to console for GitHub Actions log
print(f"phi_value: {phi_value}")
print(f"timestamp: '{timestamp}'")

# SAVE the phi_value to a file for the pulse entry
with open("delta_phi.txt", "w") as f:
    f.write(str(phi_value))
