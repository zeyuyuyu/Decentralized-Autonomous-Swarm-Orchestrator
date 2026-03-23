import asyncio
from dataclasses import dataclass
from typing import Dict, List, Set
import time

@dataclass
class SwarmNode:
    node_id: str
    ip_address: str 
    last_heartbeat: float
    capabilities: List[str]
    status: str = 'active'

class SwarmManager:
    def __init__(self, heartbeat_interval: int = 30):
        self.nodes: Dict[str, SwarmNode] = {}
        self.heartbeat_interval = heartbeat_interval
        self.mesh_connections: Dict[str, Set[str]] = {}
    
    async def register_node(self, node_id: str, ip_address: str, capabilities: List[str]) -> None:
        """Register a new node in the swarm"""
        self.nodes[node_id] = SwarmNode(
            node_id=node_id,
            ip_address=ip_address,
            last_heartbeat=time.time(),
            capabilities=capabilities
        )
        self.mesh_connections[node_id] = set()
        await self._update_mesh_topology()

    async def heartbeat(self, node_id: str) -> None:
        """Update node heartbeat timestamp"""
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = time.time()

    async def _update_mesh_topology(self) -> None:
        """Dynamically update mesh network connections between nodes"""
        active_nodes = [n for n in self.nodes.values() if n.status == 'active']
        
        # Ensure minimum redundancy - each node connects to at least 3 others if possible
        for node in active_nodes:
            while len(self.mesh_connections[node.node_id]) < min(3, len(active_nodes) - 1):
                # Find best node to connect to based on capabilities and existing connections
                potential_peers = [
                    n for n in active_nodes 
                    if n.node_id != node.node_id
                    and n.node_id not in self.mesh_connections[node.node_id]
                ]
                
                if potential_peers:
                    peer = max(potential_peers, key=lambda x: len(set(x.capabilities) & set(node.capabilities)))
                    self.mesh_connections[node.node_id].add(peer.node_id)
                    self.mesh_connections[peer.node_id].add(node.node_id)
                else:
                    break

    async def monitor_health(self) -> None:
        """Monitor node health and trigger auto-healing"""
        while True:
            current_time = time.time()
            
            for node_id, node in self.nodes.items():
                if current_time - node.last_heartbeat > self.heartbeat_interval:
                    if node.status == 'active':
                        node.status = 'degraded'
                    elif node.status == 'degraded':
                        node.status = 'offline'
                        # Trigger mesh reorganization when node goes offline
                        await self._update_mesh_topology()
            
            await asyncio.sleep(self.heartbeat_interval)

    def get_node_connections(self, node_id: str) -> List[str]:
        """Get list of nodes connected to the specified node"""
        return list(self.mesh_connections.get(node_id, set()))

    def get_swarm_status(self) -> Dict:
        """Get current status of the entire swarm"""
        return {
            'total_nodes': len(self.nodes),
            'active_nodes': len([n for n in self.nodes.values() if n.status == 'active']),
            'degraded_nodes': len([n for n in self.nodes.values() if n.status == 'degraded']),
            'offline_nodes': len([n for n in self.nodes.values() if n.status == 'offline']),
            'mesh_connections': {k: list(v) for k, v in self.mesh_connections.items()}
        }