import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List, Set

@dataclass
class SwarmNode:
    id: str
    address: str
    last_heartbeat: float
    status: str
    capabilities: List[str]

class SwarmManager:
    def __init__(self, heartbeat_interval: int = 30):
        self.nodes: Dict[str, SwarmNode] = {}
        self.active_nodes: Set[str] = set()
        self.heartbeat_interval = heartbeat_interval
        self.is_running = False

    async def start(self):
        """Start the swarm manager and monitoring tasks"""
        self.is_running = True
        await asyncio.gather(
            self.monitor_node_health(),
            self.discovery_service()
        )

    async def monitor_node_health(self):
        """Continuously monitor node health and update status"""
        while self.is_running:
            current_time = time.time()
            dead_nodes = []

            for node_id, node in self.nodes.items():
                if current_time - node.last_heartbeat > self.heartbeat_interval:
                    node.status = 'OFFLINE'
                    dead_nodes.append(node_id)
                    self.active_nodes.discard(node_id)

            for node_id in dead_nodes:
                print(f'Node {node_id} is unresponsive, marking as offline')

            await asyncio.sleep(self.heartbeat_interval / 2)

    async def discovery_service(self):
        """Service for dynamic node discovery and registration"""
        while self.is_running:
            # Simulate network discovery
            # In production, implement actual network scanning/discovery
            await asyncio.sleep(60)

    async def register_node(self, node_id: str, address: str, capabilities: List[str]):
        """Register a new node in the swarm"""
        if node_id in self.nodes:
            print(f'Node {node_id} already registered, updating details')
        
        self.nodes[node_id] = SwarmNode(
            id=node_id,
            address=address,
            last_heartbeat=time.time(),
            status='ONLINE',
            capabilities=capabilities
        )
        self.active_nodes.add(node_id)
        print(f'Node {node_id} registered successfully')

    async def heartbeat(self, node_id: str):
        """Process heartbeat from a node"""
        if node_id not in self.nodes:
            print(f'Unknown node {node_id} sent heartbeat')
            return False

        self.nodes[node_id].last_heartbeat = time.time()
        self.nodes[node_id].status = 'ONLINE'
        self.active_nodes.add(node_id)
        return True

    def get_active_nodes(self) -> List[SwarmNode]:
        """Return list of currently active nodes"""
        return [self.nodes[node_id] for node_id in self.active_nodes]

    def get_nodes_with_capability(self, capability: str) -> List[SwarmNode]:
        """Return list of active nodes with specific capability"""
        return [
            node for node in self.get_active_nodes()
            if capability in node.capabilities
        ]

    async def stop(self):
        """Stop the swarm manager"""
        self.is_running = False
