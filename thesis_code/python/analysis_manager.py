import os
import logging
from pipeline_tools.graph_modeling.uml_parsing import graph_json_to_object
from pipeline_tools.cluster_analysis.cluster_identification import identify_clusters, ClusteringAlgorithm
from pipeline_tools.utils.utils import check_or_create_path
from results.serializers import serialize_clusters_information, serialize_graph
from plotting.plot_graph_pyvis import plot_graphs_pyvis
from results.graph import Graph
from results.cluster import ClustersInformation


class AnalysisManager:
    def __init__(self, data_path: str, clustering_algorithm : ClusteringAlgorithm = ClusteringAlgorithm.LOUVAIN):
        self.clustering_algorithm = clustering_algorithm
        # Paths (just for information potentially for debugging or documentation when writing the text)
        self.data_path = data_path
        self._setup_paths()
        self._setup_logging()
        # Results objects produced during analysis
        self.graph_repr = None
        self.clusters = None

    def _setup_logging(self):
        clusters_dir = os.path.dirname(self.clusters_path)
        check_or_create_path(clusters_dir)
        log_file_path = os.path.join(clusters_dir, 'analysis.log')
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=log_file_path,
                            filemode='w')
        logging.info('Logging setup complete. Logs will be saved to {}'.format(log_file_path))

    def _setup_paths(self):
        self.graph_path = os.path.join(self.data_path, 'graph/graph.json')
        if self.clustering_algorithm == ClusteringAlgorithm.LOUVAIN:
            self.clusters_path = os.path.join(self.data_path, 'clusters/louvain/clusters.json')
        elif self.clustering_algorithm == ClusteringAlgorithm.GIRVAN_NEWMAN:
            self.clusters_path = os.path.join(self.data_path, 'clusters/girvan_newman/clusters.json')
        elif self.clustering_algorithm == ClusteringAlgorithm.LEIDEN:
            self.clusters_path = os.path.join(self.data_path, 'clusters/leiden/clusters.json')
        else:
            raise Exception('Unknown clustering algorithm.')
        clusters_dir = os.path.dirname(self.clusters_path)
        check_or_create_path(clusters_dir)

    def save_graph_report(self):
        '''Save detailed graph report to a file.'''
        directory = os.path.dirname(self.graph_path)
        check_or_create_path(directory)
        graph_info = serialize_graph(self.graph_repr)
        with open(self.graph_path, 'w') as graph_file:
            graph_file.write(graph_info)
        logging.info('Detailed graph report saved.')

    def save_clusters_report(self):
        '''Save detailed clusters report to a file.'''
        directory = os.path.dirname(self.clusters_path)
        check_or_create_path(directory)
        clusters_info = serialize_clusters_information(self.clusters)
        with open(self.clusters_path, 'w') as clusters_file:
            clusters_file.write(clusters_info)
        logging.info('Detailed clusters report saved.')

    def log_clusters_analysis(self):
        logging.info('Beginning of analysis logging.')

        assert isinstance(self.graph_repr, Graph), 'Expected graph_repr to be an instance of Graph'
        assert isinstance(self.clusters, ClustersInformation), 'Expected clusters to be an instance of ClustersInformation'

        # Log basic information about the graph
        logging.info(f'Number of nodes in the graph: {len(self.graph_repr.nodes)}')
        logging.info(f'Number of edges (with duplicates): {len(self.graph_repr.edges)}')
        logging.info(f'Number of unique edges: {len(set(self.graph_repr.edges))}')

        # Compute and log metrics for isolated nodes and average edges
        isolated_nodes_count = self.graph_repr.count_isolated_nodes()
        logging.info(f'Number of isolated nodes: {isolated_nodes_count}')
        avg_incoming = self.graph_repr.average_edges()
        logging.info(f'Average edges per node: {avg_incoming}')
        median_incoming = self.graph_repr.median_incoming_edges_per_node()
        logging.info(f'Median number of incoming edges per node: {median_incoming}')
        median_outgoing = self.graph_repr.median_outgoing_edges_per_node()
        logging.info(f'Median number of outgoing edges per node: {median_outgoing}')
        
        # Log basic information about clusters
        logging.info(f'Number of clusters: {len(self.clusters.clusters)}')

        # Analyse and log cluster details
        nb_intra_cluster_edges = sum(len(cluster.intra_cluster_edges) for cluster in self.clusters.clusters)
        nb_inter_cluster_edges = len(self.clusters.inter_cluster_edges)
        total_edges = nb_intra_cluster_edges + nb_inter_cluster_edges
        logging.info(f'Number of intra-cluster edges: {nb_intra_cluster_edges}')
        logging.info(f'Number of inter-cluster edges: {nb_inter_cluster_edges}')
        logging.info(f'Total number of edges (intra + inter-cluster): {total_edges}')

        # Log additional metrics about the clusters
        more_than_2_nodes = sum(len(cluster.nodes) > 2 for cluster in self.clusters.clusters)
        more_than_5_nodes = sum(len(cluster.nodes) > 5 for cluster in self.clusters.clusters)
        logging.info(f'Clusters with more than 2 nodes: {more_than_2_nodes}')
        logging.info(f'Clusters with more than 5 nodes: {more_than_5_nodes}')

        # Calculate and log the average number of nodes per cluster
        total_nodes_all_clusters = sum(len(cluster.nodes) for cluster in self.clusters.clusters)
        avg_nodes_all_clusters = total_nodes_all_clusters / len(self.clusters.clusters)
        logging.info(f'Average number of nodes in all clusters: {avg_nodes_all_clusters}')

        # Calculate and log the average number of nodes per cluster for clusters with more than 2 nodes
        total_nodes_clusters_more_than_2 = sum(len(cluster.nodes) for cluster in self.clusters.clusters if len(cluster.nodes) > 2)
        avg_nodes_clusters_more_than_2 = total_nodes_clusters_more_than_2 / more_than_2_nodes
        logging.info(f'Average number of nodes in clusters with more than 2 nodes: {avg_nodes_clusters_more_than_2}')

        # Calculate and log the average number of nodes per cluster for clusters with more than 5 nodes
        total_nodes_clusters_more_than_5 = sum(len(cluster.nodes) for cluster in self.clusters.clusters if len(cluster.nodes) > 5)
        avg_nodes_clusters_more_than_5 = total_nodes_clusters_more_than_5 / more_than_5_nodes
        logging.info(f'Average number of nodes in clusters with more than 5 nodes: {avg_nodes_clusters_more_than_5}')

        # Calculate and log the median number of nodes per cluster
        nodes_per_cluster = sorted([len(cluster.nodes) for cluster in self.clusters.clusters])
        median_all_clusters = nodes_per_cluster[len(nodes_per_cluster) // 2] if nodes_per_cluster else 0
        logging.info(f'Median number of nodes in all clusters: {median_all_clusters}')

        # Calculate and log the median number of nodes for clusters with more than 2 nodes
        nodes_per_cluster_more_than_2 = sorted([len(cluster.nodes) for cluster in self.clusters.clusters if len(cluster.nodes) > 2])
        median_clusters_more_than_2 = nodes_per_cluster_more_than_2[len(nodes_per_cluster_more_than_2) // 2] if nodes_per_cluster_more_than_2 else 0
        logging.info(f'Median number of nodes in clusters with more than 2 nodes: {median_clusters_more_than_2}')

        # Calculate and log the median number of nodes for clusters with more than 5 nodes
        nodes_per_cluster_more_than_5 = sorted([len(cluster.nodes) for cluster in self.clusters.clusters if len(cluster.nodes) > 5])
        median_clusters_more_than_5 = nodes_per_cluster_more_than_5[len(nodes_per_cluster_more_than_5) // 2] if nodes_per_cluster_more_than_5 else 0
        logging.info(f'Median number of nodes in clusters with more than 5 nodes: {median_clusters_more_than_5}')

        # Log details of each cluster
        for cluster in self.clusters.clusters:
            logging.info(f'Cluster {cluster.id}: {len(cluster.nodes)} nodes, {len(cluster.intra_cluster_edges)} intra-cluster edges')

        # If we have edges, calculate and log the percentage of inter-cluster edges
        if total_edges > 0:
            percentage_inter_cluster_edges = (nb_inter_cluster_edges / total_edges) * 100
            logging.info(f'Percentage of inter-cluster edges: {percentage_inter_cluster_edges:.2f}%')

        logging.info('End of analysis logging.')

    def run_analysis(self):
        logging.info('Begin of analysis.')

        logging.info('BEGIN: Graph JSON to Graph Object.')
        self.graph_repr = graph_json_to_object(self.graph_path)
        logging.info('END: Graph JSON to Graph Object')

        # Several possibilities for the clustering algorithm here
        self.clusters = identify_clusters(self.graph_repr, self.clustering_algorithm)

        self.save_graph_report()
        self.save_clusters_report()
        self.log_clusters_analysis()

        logging.info('Saving Jupyter Notebooks for plotting the graph.')
        plot_graphs_pyvis(os.path.dirname(self.clusters_path), self.clusters, self.graph_repr, single_node_cluster_color_black=True)

        logging.info('End of analysis.')
