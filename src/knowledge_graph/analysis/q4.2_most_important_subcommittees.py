"""Q4: What are the most important subcommittees?"""
from get_subgraph import get_subgraph
import dgl
import pandas as pd
from collections import Counter
(g,), _ = dgl.load_graphs('../../../data/graph.dgl')
start_node_ids = {'member': [10,11,12,13,14]}  # example only
valid_edge_types = [
    ('member', 'memberof', 'subcommittee')]
sg = get_subgraph(g, start_node_ids, valid_edge_types)
member_srcids, subcommittee_tgtids = sg.edges(etype=('member', 'memberof', 'subcommittee'))
#print(member_srcids)
#print(party_tgtids)

df_node = pd.read_csv('../../../data/nodes.csv')
df_node_subcommittee = df_node[df_node["ntype"]=='subcommittee']
df_node_subcommittee.set_index("nid_type", inplace=True)

#print(df_node_party)

c = Counter([df_node_subcommittee.loc[x.item()]["nname"] for x in subcommittee_tgtids])
print(c)