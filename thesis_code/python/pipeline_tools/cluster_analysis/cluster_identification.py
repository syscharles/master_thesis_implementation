import networkx as nx
import infomap
import igraph as ig
import leidenalg
from ..utils.utils import map_custom_graph_to_networkx
from results.graph import Graph
from results.cluster import Cluster, ClustersInformation
from pipeline_tools.cluster_analysis.inter_cluster_edges import find_inter_cluster_edges
from enum import Enum, auto
import logging

class ClusteringAlgorithm(Enum):
    LOUVAIN = auto()
    GIRVAN_NEWMAN = auto()
    LEIDEN = auto()

def identify_clusters(graph_repr: Graph, algorithm: ClusteringAlgorithm):
    if algorithm == ClusteringAlgorithm.LOUVAIN:
        logging.info('BEGIN: Cluster identification from Graph representation using the Louvain Method.')
        communities_sets = clusters_from_graph_with_louvain(graph_repr)
        logging.info('END: Cluster identification from Graph representation using the Louvain Method.')
    elif algorithm == ClusteringAlgorithm.GIRVAN_NEWMAN:
        logging.info('BEGIN: Cluster identification from Graph representation using the Girvan-Newman algorithm.')
        communities_sets = clusters_from_graph_with_girvan_newman(graph_repr)
        logging.info('END: Cluster identification from Graph representation using the Girvan-Newman algorithm.')
    elif algorithm == ClusteringAlgorithm.LEIDEN:
        logging.info('BEGIN: Cluster identification from Graph representation using the Leiden algorithm.')
        communities_sets = clusters_from_graph_with_leiden(graph_repr)
        logging.info('END: Cluster identification from Graph representation using the Leiden algorithm.')
    else:
        raise ValueError("Unsupported clustering algorithm")

    cluster_objects = list()
    for community_id, nodes_set in enumerate(communities_sets, start=1):
        cluster_nodes = [graph_repr.get_node_by_name(node) for node in nodes_set]
        intra_cluster_edges = [edge for edge in graph_repr.edges if edge.source.name in nodes_set and edge.destination.name in nodes_set]
        
        cluster_objects.append(Cluster(community_id, cluster_nodes, intra_cluster_edges))

    cluster_info = ClustersInformation(cluster_objects)
    logging.info('BEGIN: Inter-cluster edges identification.')
    cluster_info.inter_cluster_edges = find_inter_cluster_edges(graph_repr, cluster_info)
    logging.info('END: Inter-cluster edges identification.')

    return cluster_info

def clusters_from_graph_with_louvain(graph: Graph):
    '''
    Identify communities in a graph using the Louvain method.
    The function takes a Graph object as input.
    '''
    nx_graph = map_custom_graph_to_networkx(graph)
    seed = 2247
    # Use the Louvain method to find the best partition
    communities_sets = nx.community.louvain_communities(G=nx_graph, 
                                                        seed=seed)
    
    modularity = nx.community.modularity(nx_graph, communities_sets)
    logging.info(f'Modularity of the clusters is: {modularity}')
    
    return communities_sets

def clusters_from_graph_with_girvan_newman(graph: Graph):
    '''
    Identify communities in a graph using the Girvan-Newman algorithm, 
    using the modularity metric to select the level of division.
    The function takes a Graph object as input.
    '''
    nx_graph = map_custom_graph_to_networkx(graph)
    comp = nx.community.girvan_newman(nx_graph)

    # Initialize variables to track modularity and levels
    max_modularity = 0
    current_modularity = 0
    optimal_level = None
    i = 0
    
    base_modularity = nx.community.modularity(nx_graph, [list(nx_graph.nodes)])
    logging.info(f'Base modularity: {base_modularity}')
    
    for level in comp:
        i += 1
        communities = list(level)
        current_modularity = nx.community.modularity(nx_graph, communities)
        logging.info(f'Modularity score at level {i} is {current_modularity}')
        
        # Update the max modularity if the current modularity is higher
        if current_modularity > max_modularity:
            max_modularity = current_modularity
            optimal_level = communities
            optimal_i = i

    if optimal_level is None:
        logging.warning("No optimal level found; using the last level.")
        optimal_level = communities

    logging.info(f'Optimal level of depth in the Girvan-Newman algorithm was level {optimal_i}.')

    communities_sets = optimal_level

    modularity = nx.community.modularity(nx_graph, communities_sets)
    logging.info(f'Modularity of the clusters is: {modularity}')
    
    return communities_sets

def clusters_from_graph_with_leiden(graph):
    '''
    Directly identify communities in a graph using the Leiden algorithm with igraph and leidenalg,
    ensuring determinism with a specified seed.
    The function takes a Graph object as input.
    '''
    seed = 42
    node_to_index = {node.name: index for index, node in enumerate(graph.nodes)}
    
    ig_edges = [(node_to_index[edge.source.name], node_to_index[edge.destination.name]) for edge in graph.edges]
    ig_graph = ig.Graph(edges=ig_edges, directed=True)
    ig_graph.vs["name"] = [node.name for node in graph.nodes]
    
    partition = leidenalg.find_partition(ig_graph, 
                                         leidenalg.ModularityVertexPartition, 
                                         seed=seed)
    
    communities_sets = [{ig_graph.vs[node_id]["name"] for node_id in community} for community in partition]

    nx_graph = map_custom_graph_to_networkx(graph)
    modularity = nx.community.modularity(nx_graph, communities_sets)
    logging.info(f'Modularity of the clusters is: {modularity}')
    
    return communities_sets
