from  results.graph import Node, Edge

class Cluster:
    def __init__(self, id, nodes, intra_cluster_edges=list()) -> None:
        if not isinstance(id, int):
            raise Exception('ID of cluster must be of type int.')
        if not isinstance(nodes, list):
            raise Exception('Nodes must be a list.')
        if not isinstance(intra_cluster_edges, list):
            raise Exception('Intra-cluster edges must be a list.')
        for node in nodes:
            if not isinstance(node, Node):
                raise Exception(f'Nodes of a cluster must all be of type Node, found a node of type {type(node)}')
        self.id = id
        self.nodes: list[Node] = nodes
        self.intra_cluster_edges: list[Edge] = intra_cluster_edges

    def __str__(self):
        return f'Cluster {self.id}: {len(self.nodes)} nodes, {len(self.intra_cluster_edges)} intra-cluster edges'

    def __eq__(self, other):
        if not isinstance(other, Cluster):
            return NotImplemented
        return self.id == other.id and self.nodes == other.nodes and self.intra_cluster_edges == other.intra_cluster_edges

    def __hash__(self):
        return hash((self.id, self.nodes, self.intra_cluster_edges))

class ClustersInformation:
    def __init__(self, clusters):
        self.clusters: list[Cluster] = clusters
        self.inter_cluster_edges: list[Edge] = list()

    def __str__(self):
        return f'Clusters Information: {len(self.clusters)} clusters, {len(self.inter_cluster_edges)} inter-cluster edges'

    def __eq__(self, other):
        if not isinstance(other, ClustersInformation):
            return NotImplemented
        return set(self.clusters) == set(other.clusters)
    def __hash__(self):
            return hash((self.clusters))
