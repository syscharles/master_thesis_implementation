import json
from results.cluster import Cluster, ClustersInformation
from results.graph import Graph, Edge, Node, Method

def serialize_method(method: Method):
    if method is None:
        return None

    return {
        "return_type": method.return_type,
        "method_name": method.name,
        "declaring_class": method.declaring_class,
        "arguments": [{"type": param["type"], "value": param["name"]} for param in method.parameters],
        "method_signature": method.signature
    }


def serialize_node(node: Node):
    '''Serialize a Node object into a dictionary.'''
    return {
        'name': node.name
    }

def serialize_edge(edge: Edge):
    edge_data = {
        'source': edge.source.name,
        'destination': edge.destination.name,
    }
    if edge.method is not None:
        edge_data['link_method'] = serialize_method(edge.method)
    if edge.source_method is not None:
        edge_data['source_method'] = serialize_method(edge.source_method)
    return edge_data


def serialize_graph(graph: Graph):
    '''Serialize the entire Graph object into a structured dictionary.'''
    graph_data = {
        'nodes': [serialize_node(node) for node in graph.nodes],
        'edges': [serialize_edge(edge) for edge in graph.edges]
    }
    return json.dumps(graph_data, indent=4)

def serialize_cluster(cluster: Cluster):
    '''Serialize a Cluster object into a dictionary.'''
    return {
        'id': cluster.id,
        'nodes': [serialize_node(node) for node in cluster.nodes],
        'intra_cluster_edges': [serialize_edge(edge) for edge in cluster.intra_cluster_edges]
    }

def serialize_clusters_information(clusters_info: ClustersInformation):
    '''Serialize ClustersInformation object into a structured dictionary.'''
    clusters_data = {
        'clusters': [serialize_cluster(cluster) for cluster in clusters_info.clusters],
        'inter_cluster_edges': [serialize_edge(edge) for edge in clusters_info.inter_cluster_edges]
    }
    return json.dumps(clusters_data, indent=4)
