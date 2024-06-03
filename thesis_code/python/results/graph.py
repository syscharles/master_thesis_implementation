import logging 

class Method:
    def __init__(self, name, parameters, return_type, declaring_class, signature) -> None:
        if name is None:
            raise Exception('Name of a method must not be undefined.')
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.declaring_class = declaring_class
        self.signature = signature

    def __eq__(self, other):
        if not isinstance(other, Method):
            return NotImplemented
        return (self.name, tuple(self.parameters), self.return_type, self.declaring_class) == \
               (other.name, tuple(other.parameters), other.return_type, other.declaring_class)

    def __str__(self):
        params = ', '.join(self.parameters)
        return f'{self.name}({params}): {self.return_type} @ {self.declaring_class}'

class Attribute:
    def __init__(self, name, typeAtt) -> None:
        if name is None:
            raise Exception('Name of an attribute must not be undefined.')
        if typeAtt is None:
            raise Exception('Type of an attribute must not be undefined.')
        self.name = name
        self.type = typeAtt

    def __eq__(self, other):
        if not isinstance(other, Attribute):
            return NotImplemented
        return (self.name, self.type) == (other.name, other.type)

    def __str__(self):
        return f'{self.name}: {self.type}'

class Node:
    def __init__(self, name) -> None:
        if name is None:
            raise Exception('Name of a node (class) must not be undefined.')
        self.name = name

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        if not isinstance(other, Node):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return f'Node: {self.name}'

class Edge:
    def __init__(self, source, destination, method, source_method, weight=1) -> None:
        if not isinstance(source, Node):
            raise Exception('Departure node of an edge must be of type Node.')
        if not isinstance(destination, Node):
            raise Exception('Destination node of an edge must be of type Node.')
        if method is None:
            raise Exception('method must not be null')
        if source_method is None:
            raise Exception('source_method must not be null')
        self.source = source
        self.destination = destination
        self.method = method
        self.source_method = source_method
        self.weight = weight

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return NotImplemented
        return (self.source, self.destination) == \
               (other.source, other.destination)

    def __hash__(self):
        return hash((self.source, self.destination, self.weight))

    def __str__(self):
        return f'Edge: {self.source} -> {self.destination}, Weight: {self.weight}, Method: {self.method}'

class Graph:
    def __init__(self, nodes: list[Node], edges: list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges

    def add_node(self, node: Node) -> None:
        self.nodes.append(node)

    def add_edge(self, edge: Edge) -> None:
        if edge.source not in [n.name for n in self.nodes]:
            raise Exception(f'Graph does not have the source node {edge.departure} in its nodes.')
        if edge.destination not in [n.name for n in self.nodes]:
            raise Exception(f'Graph does not have the destination node {edge.destination} in its nodes.')        
        self.edges.append(edge)

    def count_isolated_nodes(self):
        isolated_nodes = [node for node in self.nodes if self.is_isolated(node)]
        return len(isolated_nodes)
    
    def is_isolated(self, node):
        for edge in self.edges:
            if edge.source == node or edge.destination == node:
                return False
        return True

    def average_edges(self):
        edges_count = {node: 0 for node in self.nodes}
        for edge in self.edges:
            edges_count[edge.destination] += 1
        return sum(edges_count.values()) / len(self.nodes)

    def median_incoming_edges_per_node(self):
        incoming_edges_counts = self.all_incoming_edges_per_node()
        return self.calculate_median(incoming_edges_counts)

    def median_outgoing_edges_per_node(self):
        outgoing_edges_counts = self.all_outgoing_edges_per_node()
        return self.calculate_median(outgoing_edges_counts)

    def all_incoming_edges_per_node(self):
        incoming_edges = {node: 0 for node in self.nodes}
        for edge in self.edges:
            incoming_edges[edge.destination] += 1
        return list(incoming_edges.values())

    def all_outgoing_edges_per_node(self):
        outgoing_edges = {node: 0 for node in self.nodes}
        for edge in self.edges:
            outgoing_edges[edge.source] += 1
        return list(outgoing_edges.values())

    def calculate_median(self, data):
        data.sort()
        n = len(data)
        if n % 2 == 1:
            return data[n // 2]
        else:
            mid1 = data[n // 2 - 1]
            mid2 = data[n // 2]
            return (mid1 + mid2) / 2

    def get_node_by_name(self, name: str) -> Node:
        for node in self.nodes:
            if node.name == name:
                return node
        logging.warning(f'Node with name {name} was not found.')
        return None

    def __str__(self):
        return f'Graph with {len(self.nodes)} nodes and {len(self.edges)} edges.'


