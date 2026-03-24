import os
import time
import random
import subprocess

class SwarmManager:
    def __init__(self, max_nodes=10):
        self.max_nodes = max_nodes
        self.current_nodes = 0
        self.node_utilization = {}

    def initialize_swarm(self):
        subprocess.run(['docker', 'swarm', 'init'])
        self.current_nodes = 1
        self.node_utilization = {
            'node-1': 0
        }

    def add_node(self):
        if self.current_nodes < self.max_nodes:
            node_name = f'node-{self.current_nodes + 1}'
            subprocess.run(['docker', 'swarm', 'join-token', 'worker'], stdout=subprocess.PIPE)
            self.node_utilization[node_name] = 0
            self.current_nodes += 1

    def remove_node(self):
        if self.current_nodes > 1:
            node_to_remove = min(self.node_utilization, key=self.node_utilization.get)
            subprocess.run(['docker', 'node', 'rm', node_to_remove, '--force'])
            del self.node_utilization[node_to_remove]
            self.current_nodes -= 1

    def schedule_task(self, task):
        least_utilized_node = min(self.node_utilization, key=self.node_utilization.get)
        self.node_utilization[least_utilized_node] += task.resource_requirements
        subprocess.run(['docker', 'service', 'create', '--name', task.name, '--replicas', '1', task.image])

    def monitor_swarm(self):
        while True:
            time.sleep(60)
            for node, utilization in self.node_utilization.items():
                if utilization > 80:
                    self.add_node()
                elif utilization < 20 and self.current_nodes > 1:
                    self.remove_node()
