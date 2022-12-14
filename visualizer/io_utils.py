import json
import ast
import os


def new_to_old(data):
    out_data = []
    for node in data['nodes']:
        properties = node
        node_id = node['id']
        properties.pop('id', None)
        try:
            out_data.append(get_old_node_dict(node_id, properties))
        except KeyError:
            print('At least one node in the input file does not specify an ID. Every node needs to have an ID.')

    for edge in data['links']:
        properties = edge
        source = edge['source']
        target = edge['target']
        properties.pop('source', None)
        properties.pop('target', None)
        try:
            out_data.append(get_old_edge_dict(source, target, properties))
        except KeyError:
            print('At least one edge in the input file does not specify a source or target. '
                  'Every edge needs to have both: A source and a target.')
    return out_data


def new_to_old_file(filepath, file_name):
    with open(filepath) as input_file:
        in_data = json.load(input_file)
        data = new_to_old(in_data)
    with open(file_name, 'w') as fp:
        fp.write('# Converted from new format. For internal use only.\n' +
                 '\n'.join(json.dumps(i) for i in data))


def get_old_node_dict(node_id, properties):
    '''
    Get old format node object.
    :param node_id: Node ID as a string.
    :param properties: Dictionary with all the properties of the node.
    :return: Dictionary representing a single node as used in the old format.
    '''

    return {"type": "node", "id": node_id, "properties": properties}


def get_old_edge_dict(source, target, properties):
    '''
    Get old format edge object
    :param source: ID of the source node as a string.
    :param target: ID of the target node as a string.
    :param properties: Dictionary with all the properties of the edge.
    :return: Dictionary representing a single edge as used in the old format.
    '''

    return {"type": "edge", "source": source, "target": target, "properties": properties}

def get_external_data(directory):
    data_info = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename)) as data_file:
                data = json.load(data_file)
                try:
                    id = data['graph']['id']
                    name = data['graph']['name']
                except KeyError:
                    print('The file {} is not in the correct format.'.format(str(filename)))
                path = os.path.join(directory, filename)
                data_info.append({'id': id, 'name': name, 'path': path})
    return data_info


if __name__ == '__main__':
    # Just for testing. Replace by actual paths.
    # Add actual command line argument parsing for use as a command line tool.
    new_to_old_file('datasets/preprocessed/graph_roxanne_roxsd_v3_ucsc.json',
                    'datasets/preprocessed/graph_roxanne_roxsd_v3_ucsc_old_format.json')
    new_to_old_file('datasets/preprocessed/graph_phone_number_roxsd_v3_ucsc.json',
                    'datasets/preprocessed/graph_phone_number_roxsd_v3_ucsc_old_format.json')
    new_to_old_file('datasets/preprocessed/graph_groundtruth_roxsd_v3_ucsc.json',
                    'datasets/preprocessed/graph_groundtruth_roxsd_v3_ucsc_old_format.json')
