"""Q5: How likely / to what degree are two members to share a committee?"""
from get_subgraph import get_subgraph
import dgl
import pandas as pd
from collections import Counter
(g,), _ = dgl.load_graphs('../../../data/graph.dgl')
start_node_ids = {'member': [10,11,12,13,14],\
    'committee' : [1,2,3,4,5]}  # example only
n = len(start_node_ids['member'])
pairs = n*(n-1)/2
valid_edge_types = [('committee', 'memberof_inv', 'member'),\
    ('member', 'memberof', 'committee')]

sg_nodes_mem = dgl.node_type_subgraph(g,ntypes = {'member': [10,11,12,13,14]})
sg_nodes_mem_comm = dgl.node_type_subgraph(sg_nodes_mem,ntypes = {'committee' : [1,2,3,4,5]})

sg = get_subgraph(g, start_node_ids, valid_edge_types)
member_srcids, subcommittee_tgtids = sg.edges()
