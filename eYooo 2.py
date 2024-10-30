import simpy
import random
import matplotlib.pyplot as plt
import numpy as np  # Necessary for array handling

# Constants
NUM_REQUESTS = 50  # Total number of requests per PC
NUM_PCS = 30  # Number of PCs
NUM_SERVERS = 3  # Number of HTTP servers
FIFO_COUNT = 8  # Number of FIFO switches
PRIORITY_COUNT = 8  # Number of Priority switches
SWITCH_CAPACITY = 1  # Capacity of each switch

# Latency data collection
latencies = {'FIFO': [], 'Priority': []}  # Store latency for each queue type

# PC class representing a personal computer
class PC:
    def __init__(self, env, name, http_servers, switches):
        self.env = env
        self.name = name
        self.http_servers = http_servers
        self.switches = switches

    def request_http(self):
        for _ in range(NUM_REQUESTS):
            yield self.env.timeout(random.uniform(0.1, 0.5))  # Think time
            request_time = self.env.now

            # Randomly select a switch and server
            switch = random.choice(self.switches)
            server = random.choice(self.http_servers)

            with switch.request() as request:
                yield request
                # Handle request to the HTTP server
                start_time = self.env.now
                yield self.env.process(server.handle_request(self.name))
                end_time = self.env.now

                if isinstance(switch, FIFOQueue):
                    latencies['FIFO'].append(end_time - request_time)  # Record FIFO latency
                else:
                    latencies['Priority'].append(end_time - request_time)  # Record Priority latency

# HTTP Server class
class HTTPServer:
    def __init__(self, env, name):
        self.env = env
        self.name = name

    def handle_request(self, pc_name):
        service_time = random.uniform(0.5, 1.5)  # Simulate processing time
        yield self.env.timeout(service_time)

# Switch classes
class FIFOQueue(simpy.Resource):
    def __init__(self, env, name, capacity):
        super().__init__(env, capacity)
        self.name = name

class PriorityQueue(simpy.PriorityResource):
    def __init__(self, env, name, capacity):
        super().__init__(env, capacity)
        self.name = name

# Setup the environment
env = simpy.Environment()

# Create HTTP servers
http_servers = [HTTPServer(env, f'Server{i + 1}') for i in range(NUM_SERVERS)]

# Create switches
switches = []
for i in range(FIFO_COUNT):
    switch = FIFOQueue(env, f'FIFO Switch {i + 1}', capacity=SWITCH_CAPACITY)
    switches.append(switch)

for i in range(PRIORITY_COUNT):
    switch = PriorityQueue(env, f'Priority Switch {i + 1}', capacity=SWITCH_CAPACITY)
    switches.append(switch)

# Create PCs
pcs = []
for i in range(NUM_PCS):
    pc = PC(env, f'PC{i + 1}', http_servers, switches)
    pcs.append(pc)
    env.process(pc.request_http())

# Run the simulation
env.run()

# Calculate average latencies
average_latency_fifo = np.mean(latencies['FIFO']) if latencies['FIFO'] else 0
average_latency_priority = np.mean(latencies['Priority']) if latencies['Priority'] else 0

print(f"Average Latency (FIFO): {average_latency_fifo:.2f} seconds")
print(f"Average Latency (Priority): {average_latency_priority:.2f} seconds")

# Visualization of latency
plt.figure(figsize=(12, 6))

# Plot FIFO Latencies Histogram
plt.subplot(1, 2, 1)
plt.hist(latencies['FIFO'], bins=20, color='blue', alpha=0.7)
plt.title('FIFO Latency Histogram')
plt.xlabel('Latency (seconds)')
plt.ylabel('Frequency')
plt.grid()

# Plot Priority Latencies Histogram
plt.subplot(1, 2, 2)
plt.hist(latencies['Priority'], bins=20, color='orange', alpha=0.7)
plt.title('Priority Latency Histogram')
plt.xlabel('Latency (seconds)')
plt.ylabel('Frequency')
plt.grid()

plt.tight_layout()
plt.show()
