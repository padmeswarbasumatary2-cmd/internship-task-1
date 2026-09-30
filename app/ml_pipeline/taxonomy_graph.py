"""
Taxonomy Knowledge Graph for semantic normalization and synonym resolution
"""
from typing import List, Dict, Optional, Set, Tuple
from difflib import SequenceMatcher
import json


class TaxonomyNode:
    """Represents a node in the taxonomy DAG"""

    def __init__(
        self,
        node_id: str,
        name: str,
        node_type: str = "leaf",
        parent_id: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        description: Optional[str] = None
    ):
        """
        Initialize a taxonomy node
        
        Args:
            node_id: Unique identifier
            name: Canonical name
            node_type: "root", "intermediate", or "leaf"
            parent_id: Parent node ID
            aliases: List of alternative names/spellings
            description: Node description
        """
        self.id = node_id
        self.name = name
        self.type = node_type
        self.parent_id = parent_id
        self.aliases = aliases or []
        self.description = description
        self.confidence = 1.0


class TaxonomyGraph:
    """
    Directed Acyclic Graph (DAG) representing hierarchical taxonomy.
    Handles entity resolution and synonym normalization.
    """

    def __init__(self):
        """Initialize the taxonomy graph"""
        self.nodes: Dict[str, TaxonomyNode] = {}
        self.edges: Dict[str, List[str]] = {}  # parent_id -> [child_ids]
        self._build_default_taxonomy()

    def _build_default_taxonomy(self):
        """Build a default sample taxonomy"""
        # Root categories
        self.add_node(TaxonomyNode("data-science", "Data Science", "root"))
        self.add_node(TaxonomyNode("web-dev", "Web Development", "root"))
        self.add_node(TaxonomyNode("devops", "DevOps", "root"))
        
        # Intermediate nodes
        self.add_node(TaxonomyNode(
            "ml", "Machine Learning", "intermediate", "data-science",
            aliases=["ML", "machine-learning"]
        ))
        self.add_node(TaxonomyNode(
            "dl", "Deep Learning", "intermediate", "data-science",
            aliases=["deep-learning", "neural networks"]
        ))
        self.add_node(TaxonomyNode(
            "frontend", "Frontend Development", "intermediate", "web-dev",
            aliases=["front-end", "client-side"]
        ))
        self.add_node(TaxonomyNode(
            "backend", "Backend Development", "intermediate", "web-dev",
            aliases=["back-end", "server-side"]
        ))
        
        # Leaf nodes (tools/frameworks)
        self.add_node(TaxonomyNode(
            "pytorch", "PyTorch", "leaf", "dl",
            aliases=["PyTorch", "torch"]
        ))
        self.add_node(TaxonomyNode(
            "tensorflow", "TensorFlow", "leaf", "dl",
            aliases=["TensorFlow", "tf"]
        ))
        self.add_node(TaxonomyNode(
            "react", "React", "leaf", "frontend",
            aliases=["ReactJS", "React.js", "React framework"]
        ))
        self.add_node(TaxonomyNode(
            "kubernetes", "Kubernetes", "leaf", "devops",
            aliases=["K8s", "k8s"]
        ))
        self.add_node(TaxonomyNode(
            "docker", "Docker", "leaf", "devops",
            aliases=["container", "containerization"]
        ))

    def add_node(self, node: TaxonomyNode):
        """Add a node to the graph"""
        self.nodes[node.id] = node
        
        # Create parent -> child relationship
        if node.parent_id:
            if node.parent_id not in self.edges:
                self.edges[node.parent_id] = []
            if node.id not in self.edges[node.parent_id]:
                self.edges[node.parent_id].append(node.id)

    def get_node(self, node_id: str) -> Optional[TaxonomyNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)

    def get_children(self, parent_id: str) -> List[TaxonomyNode]:
        """Get all child nodes of a parent"""
        child_ids = self.edges.get(parent_id, [])
        return [self.nodes[child_id] for child_id in child_ids if child_id in self.nodes]

    def get_ancestors(self, node_id: str) -> List[TaxonomyNode]:
        """Get all ancestor nodes"""
        ancestors = []
        current_node = self.get_node(node_id)
        
        while current_node and current_node.parent_id:
            parent = self.get_node(current_node.parent_id)
            if parent:
                ancestors.append(parent)
                current_node = parent
            else:
                break
        
        return ancestors

    def resolve_entity(self, text: str, max_distance: float = 0.85) -> Tuple[Optional[str], float]:
        """
        Resolve a raw text entity to canonical taxonomy node
        
        Uses fuzzy string matching (Levenshtein-like) and alias matching.
        
        Args:
            text: Raw entity text
            max_distance: Minimum similarity threshold (0-1)
        
        Returns:
            Tuple of (node_id, confidence_score)
        """
        text_lower = text.lower()
        best_match = None
        best_score = 0.0
        
        for node_id, node in self.nodes.items():
            # Check canonical name
            ratio = SequenceMatcher(None, text_lower, node.name.lower()).ratio()
            if ratio > best_score:
                best_score = ratio
                best_match = node_id
            
            # Check aliases
            for alias in node.aliases:
                ratio = SequenceMatcher(None, text_lower, alias.lower()).ratio()
                if ratio > best_score:
                    best_score = ratio
                    best_match = node_id
        
        # Return match if it exceeds threshold
        if best_score >= max_distance:
            return best_match, best_score
        
        return None, best_score

    def resolve_batch(self, texts: List[str]) -> List[Tuple[Optional[str], float]]:
        """
        Resolve multiple entities to canonical nodes
        
        Args:
            texts: List of entity texts
        
        Returns:
            List of (node_id, score) tuples
        """
        results = []
        for text in texts:
            results.append(self.resolve_entity(text))
        return results

    def get_path_to_root(self, node_id: str) -> List[str]:
        """Get the path from a node to the root"""
        path = [node_id]
        current = self.get_node(node_id)
        
        while current and current.parent_id:
            path.append(current.parent_id)
            current = self.get_node(current.parent_id)
        
        return path

    def get_depth(self, node_id: str) -> int:
        """Get the depth of a node from root"""
        return len(self.get_path_to_root(node_id)) - 1

    def export_as_json(self) -> str:
        """Export taxonomy as JSON"""
        data = {
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "type": node.type,
                    "parent_id": node.parent_id,
                    "aliases": node.aliases,
                    "description": node.description
                }
                for node in self.nodes.values()
            ],
            "edges": self.edges
        }
        return json.dumps(data, indent=2)

    def print_hierarchy(self, node_id: Optional[str] = None, level: int = 0):
        """Pretty-print the taxonomy hierarchy"""
        if node_id is None:
            # Start from root nodes
            root_nodes = [n for n in self.nodes.values() if n.type == "root"]
            for node in root_nodes:
                self.print_hierarchy(node.id, 0)
        else:
            node = self.get_node(node_id)
            if node:
                print("  " * level + f"├─ {node.name} ({node.id})")
                for child_id in self.edges.get(node_id, []):
                    self.print_hierarchy(child_id, level + 1)
