from results.graph import Graph, Edge, Node, Method, Attribute
from ..utils.utils import load_json_data

def extract_method_info(method_data):
    '''
    Extracts method information from a dictionary and returns a Method object.
    '''
    method_name = method_data.get('method_name', '')
    method_return_type = method_data.get('return_type', '')
    method_arguments = [{'type': arg.get('type', ''), 'name': arg.get('value', '')} for arg in method_data.get('arguments', [])]
    method_declaring_class = method_data.get('declaring_class', '')
    method_signature = method_data.get('method_signature', '')

    return Method(method_name, method_arguments, method_return_type, method_declaring_class, method_signature)

def parse_json_graph(file_path):
    data = load_json_data(file_path)
    if data is None:
        return [], []

    nodes_data = data.get('nodes', [])
    edges_data = data.get('edges', [])

    nodes = []
    link_data = []

    for node in nodes_data:
        node_name = node.get('name', '')
        new_node = Node(node_name)
        nodes.append(new_node)

    for edge in edges_data:
        source = edge.get('source', '')
        destination = edge.get('destination', '')
        
        link_method_data = edge.get('link_method', '')
        link_method_obj = extract_method_info(link_method_data)

        source_method_data = edge.get('source_method', '')
        source_method_obj = extract_method_info(source_method_data)

        link_data.append((source, destination, link_method_obj, source_method_obj))

    return nodes, link_data

def create_graph(nodes, link_data):
    '''
    Creates a Graph from nodes and links, ensuring Edge objects reference Node instances.
    '''
    edges = list()
    node_map = {node.name: node for node in nodes}

    for src_name, dest_name, method, source_method in link_data:
        src_node = node_map.get(src_name)
        dest_node = node_map.get(dest_name)
        if src_node and dest_node:
            edge = Edge(src_node, dest_node, method, source_method)
            edges.append(edge)

    return Graph(nodes, edges)
    
def graph_json_to_object(file_path) -> Graph:
    nodes, link_data = parse_json_graph(file_path)
    graph = create_graph(nodes, link_data)
    return graph
    