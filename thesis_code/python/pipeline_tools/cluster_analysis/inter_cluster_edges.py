from results.graph import Graph, Edge
from results.cluster import ClustersInformation
import logging

def find_cluster_of_node(clusters: ClustersInformation, node_name: str):
    '''
    Finds the cluster a node belongs to based on the node's name.
    '''
    for cluster in clusters.clusters:
        for node in cluster.nodes:
            if node.name == node_name:
                return cluster
    logging.warning(f'Cluster of node {node_name} not found.')
    return None

def find_inter_cluster_edges(graph: Graph, clusters: ClustersInformation):
    '''
    Identifies inter-cluster edges.
    '''
    inter_cluster_edges = list()
    for edge in graph.edges:
        src_cluster = find_cluster_of_node(clusters, edge.source)
        dest_cluster = find_cluster_of_node(clusters, edge.destination)
        if src_cluster != dest_cluster:
            inter_cluster_edges.append(edge)
    return inter_cluster_edges


