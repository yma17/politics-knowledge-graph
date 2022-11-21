"""
Given the ids of a set of starting nodes,
construct the subgraph of all nodes reachable from it,
given a set of edge types able to be traversed.
"""

import dgl
from collections import defaultdict

def get_subgraph(g, start_node_ids, valid_edge_types):
    # Filter by edge type
    sg = dgl.edge_type_subgraph(g, valid_edge_types)
    # Filter by start nodes
    sg = dgl.out_subgraph(sg, start_node_ids)
    # Remove nodes with no incident edges
    s2spo, o2spo = defaultdict(lambda: []), defaultdict(lambda: [])
    for s, p, o in valid_edge_types:
        s2spo[s].append((s, p, o))
        o2spo[o].append((s, p, o))
    for ntype in sg.ntypes:
        nodes_to_remove = []
        for node in sg.nodes(ntype):
            remove = True
            if ntype in s2spo.keys():
                for spo in s2spo[ntype]:
                    remove = remove and (sg.successors(node, etype=spo).size()[0] == 0)
            if ntype in o2spo.keys():
                for spo in o2spo[ntype]:
                    remove = remove and (sg.predecessors(node, etype=spo).size()[0] == 0)
            if remove:
                nodes_to_remove.append(node)
        sg.remove_nodes(nodes_to_remove, ntype=ntype)
    return sg

if __name__ == '__main__':
    (g,), _ = dgl.load_graphs('../../../data/graph.dgl')
    start_node_ids = {'member': [0, 1, 2, 3, 4]}
    valid_edge_types = [
        ('member', 'memberof', 'committee'),
        ('member', 'memberof', 'subcommittee'),
        ('member', 'memberof', 'chamber'),
        ('member', 'memberof', 'party'),
        ('member', 'paidto_inv', 'lobbyist'),
        ('member', 'votedyeaon', 'vote'),
        ('member', 'votednayon', 'vote'),
        ('member', 'sponsorof', 'bill'),
        ('member', 'cosponsorof', 'bill')]
    sg = get_subgraph(g, start_node_ids, valid_edge_types)
    print(sg)
