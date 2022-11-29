"""Q3: Who are the most important lobbyists?"""
from get_subgraph import get_subgraph
import dgl
import pandas as pd
from collections import Counter
(g,), _ = dgl.load_graphs('../../../data/graph.dgl')
start_node_ids = {'member': [10,11,12,13,14]}  # example only
valid_edge_types = [
    ('member', 'paidto_inv', 'lobbyist')]
sg = get_subgraph(g, start_node_ids, valid_edge_types)
member_srcids, lobbyist_tgtids = sg.edges(etype=('member', 'paidto_inv', 'lobbyist'))
#print(member_srcids)
#print(party_tgtids)

df_node = pd.read_csv('../../../data/nodes.csv')
df_node_lobbyist = df_node[df_node["ntype"]=='lobbyist']
df_node_lobbyist.set_index("nid_type", inplace=True)

#print(df_node_party)

c = Counter([df_node_lobbyist.loc[x.item()]["nname"] for x in lobbyist_tgtids])
print(c)