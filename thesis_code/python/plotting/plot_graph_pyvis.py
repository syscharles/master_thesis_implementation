from matplotlib import pyplot as plt
from pyvis.network import Network
import os
import logging

from pipeline_tools.utils.utils import check_or_create_path, map_custom_graph_to_networkx
from results.cluster import ClustersInformation

def visualize_graph_pyvis_without_clusters(G, output_path, net_options):
    net = Network(notebook=True, height="800px", width="100%")
    
    for node in G.nodes():
        net.add_node(node, color='black')

    for edge in G.edges():
        net.add_edge(edge[0], edge[1], color='black')

    net.set_options(net_options)
    net.show(output_path)

    return output_path

def visualize_graph_pyvis_with_clusters(output_path, net_options, clusters: ClustersInformation, single_node_cluster_color_black=False):
    net = Network(notebook=True, height='800px', width='100%')
    colors = {}

    total_clusters = len(clusters.clusters)
    color_map = plt.cm.get_cmap('hsv', total_clusters + 1)  # Adjusted the division to total_clusters + 1

    # Define a safe color start and end index to avoid red and near-red
    safe_start = int(total_clusters * 0.1)  # Start at 10% to skip reds
    safe_end = total_clusters  # End at the last color

    for idx, cluster in enumerate(clusters.clusters):
        if single_node_cluster_color_black and len(cluster.nodes) == 1:
            color = 'black'
        else:
            # Map cluster index to safe color range
            safe_idx = safe_start + (idx % (safe_end - safe_start))
            color = f'rgba({int(color_map(safe_idx)[0]*255)}, {int(color_map(safe_idx)[1]*255)}, {int(color_map(safe_idx)[2]*255)}, 0.9)'

        colors[cluster.id] = color

        for node in cluster.nodes:
            net.add_node(node.name, label=node.name, color=color)

    # Add intra-cluster edges
    for cluster in clusters.clusters:
        for edge in cluster.intra_cluster_edges:
            net.add_edge(edge.source.name, edge.destination.name, color=colors[cluster.id])

    # Add inter-cluster edges with red color
    for edge in clusters.inter_cluster_edges:
        net.add_edge(edge.source.name, edge.destination.name, color='red', title='Inter-cluster edge')

    net.set_options(net_options)
    net.show(output_path)

    return output_path


def plot_graphs_pyvis(data_path, clusters, graph, single_node_cluster_color_black=False):
    logging.basicConfig(level=logging.INFO)

    G = map_custom_graph_to_networkx(graph)
    
    # output paths
    graph_dir = os.path.join(data_path, 'plot')
    check_or_create_path(graph_dir)
    graph_path = os.path.join(graph_dir, 'graph_without_clusters.html')
    clusters_path = os.path.join(graph_dir, 'graph_with_clusters.html')
    net_options = """
    {
    "nodes": {
        "font": {
        "size": 75,
        "face": "sans-serif"
        }
    },
    "edges": {
        "width": 8,
        "arrows": {
        "to": {
            "enabled": true,
            "scaleFactor": 2.5
        }
        }
    },
    "physics": {
        "barnesHut": {
        "gravitationalConstant": -80000,
        "centralGravity": 0.3,
        "springLength": 95,
        "damping": 0.09
        },
        "minVelocity": 0.75
    }
    }
    """

    visualize_graph_pyvis_without_clusters(G, os.path.abspath(graph_path), net_options)
    visualize_graph_pyvis_with_clusters(os.path.abspath(clusters_path), net_options, clusters, single_node_cluster_color_black=single_node_cluster_color_black)
