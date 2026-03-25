import time
import random
from typing import List

class SwarmNode:
    def __init__(self, id: str):
        self.id = id
        self.state = 'idle'
        self.tasks = []
        self.neighbors = []
        self.consensus_round = 0
        self.consensus_value = None

    def add_neighbor(self, neighbor: 'SwarmNode'):
        self.neighbors.append(neighbor)

    def propose_task(self, task: dict):
        self.tasks.append(task)

    def start_consensus(self):
        self.consensus_round += 1
        self.consensus_value = random.choice(self.tasks)
        self.state = 'consensus'
        self.broadcast_consensus()

    def broadcast_consensus(self):
        for neighbor in self.neighbors:
            neighbor.receive_consensus(self.consensus_round, self.consensus_value)

    def receive_consensus(self, round: int, value: dict):
        if round > self.consensus_round:
            self.consensus_round = round
            self.consensus_value = value
            self.broadcast_consensus()
        elif round == self.consensus_round:
            if self.consensus_value != value:
                self.state = 'resolution'
                self.resolve_consensus()

    def resolve_consensus(self):
        # Implement distributed consensus resolution algorithm
        time.sleep(random.uniform(0.1, 1.0))
        self.consensus_value = self.compute_consensus_value()
        self.state = 'idle'
        self.broadcast_consensus()

    def compute_consensus_value(self) -> dict:
        # Implement logic to compute the final consensus value
        return random.choice(self.tasks)

class SwarmManager:
    def __init__(self, num_nodes: int):
        self.nodes: List[SwarmNode] = [SwarmNode(f'node-{i}') for i in range(num_nodes)]
        self.connect_nodes()

    def connect_nodes(self):
        for i in range(len(self.nodes)):
            for j in range(i+1, len(self.nodes)):
                self.nodes[i].add_neighbor(self.nodes[j])
                self.nodes[j].add_neighbor(self.nodes[i])

    def propose_task(self, task: dict):
        random.choice(self.nodes).propose_task(task)

    def start_consensus(self):
        random.choice(self.nodes).start_consensus()

    def run(self):
        while True:
            self.propose_task({'name': 'task-1', 'priority': 1})
            self.start_consensus()
            time.sleep(1)