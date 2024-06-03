import json
import networkx as nx
import os
import logging
from results.graph import Edge, Graph

def load_json_data(filepath):
    '''
    Load JSON data from a file. If the file does not exist or an error occurs,
    log the error and return None.
    '''
    if not os.path.exists(filepath):
        logging.error(f"File does not exist: {filepath}")
        return None

    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {filepath}. Error: {e}")
    except Exception as e:
        logging.error(f"Error loading JSON data from {filepath}. Error: {e}")
    
    return None

def check_or_create_path(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logging.warning(f"Directory {directory} was created as it did not exist.")
        except OSError as e:
            logging.error(f"Failed to create directory {directory}. Error: {e}")
            return None

def map_custom_graph_to_networkx(graph):
    '''
    Maps the custom Graph structure to a NetworkX graph.
    '''
    nx_graph = nx.MultiDiGraph()
    for node in graph.nodes:
        nx_graph.add_node(node.name, **vars(node))
    for edge in graph.edges:
        nx_graph.add_edge(edge.source.name, edge.destination.name, **vars(edge))
    return nx_graph