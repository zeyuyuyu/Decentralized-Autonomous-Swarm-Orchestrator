import os
import json
import time
import random
import subprocess

from typing import List, Dict

class SwarmOrchestrator:
    def __init__(self, config_file: str = 'config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.node_states: Dict[str, str] = {}
        self.node_health: Dict[str, int] = {}
        
    def start_swarm(self):
        for node in self.config['nodes']:
            self.start_node(node)
            self.node_states[node] = 'running'
            self.node_health[node] = 100
        
        self.monitor_swarm()
        
    def start_node(self, node_name: str):
        subprocess.run(['docker', 'run', '-d', '--name', node_name, self.config['node_image']], check=True)
        print(f'Started node: {node_name}')
        
    def monitor_swarm(self):
        while True:
            time.sleep(self.config['monitoring_interval'])
            self.check_node_health()
            self.heal_swarm()
            
    def check_node_health(self):
        for node in self.node_states:
            if self.node_states[node] == 'running':
                if random.randint(1, 100) < self.config['failure_rate']:
                    self.node_states[node] = 'failed'
                    self.node_health[node] = 0
                    print(f'Node {node} has failed!')
                else:
                    self.node_health[node] = self.node_health[node] - 1
                    
    def heal_swarm(self):
        for node, state in self.node_states.items():
            if state == 'failed':
                self.start_node(node)
                self.node_states[node] = 'running'
                self.node_health[node] = 100
                print(f'Healed node: {node}')
                
if __name__ == '__main__':
    orchestrator = SwarmOrchestrator()
    orchestrator.start_swarm()