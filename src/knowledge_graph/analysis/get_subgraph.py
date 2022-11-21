"""
Given the ids of a set of starting nodes,
construct the subgraph of all nodes reachable from it,
given a set of edge types able to be traversed.
"""

import dgl

def get_subgraph(g, start_node_ids, valid_edge_types):
    # Filter by edge type
    sg = dgl.edge_type_subgraph(g, valid_edge_types)
    # Filter by start nodes
    sg = dgl.out_subgraph(sg, start_node_ids)
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
