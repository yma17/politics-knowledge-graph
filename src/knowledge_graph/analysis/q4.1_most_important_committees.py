"""Q4: What are the most important committees?"""
from get_subgraph import get_subgraph
import dgl
import pandas as pd
from collections import Counter
(g,), _ = dgl.load_graphs('../../../data/graph.dgl')
start_node_ids = {'member': [10,11,12,13,14]}  # example only
valid_edge_types = [
    ('member', 'memberof', 'committee')]
sg = get_subgraph(g, start_node_ids, valid_edge_types)
member_srcids, committee_tgtids = sg.edges(etype=('member', 'memberof', 'committee'))
#print(member_srcids)
#print(party_tgtids)

df_node = pd.read_csv('../../../data/nodes.csv')
df_node_committee = df_node[df_node["ntype"]=='committee']
df_node_committee.set_index("nid_type", inplace=True)

#print(df_node_party)

c = Counter([df_node_committee.loc[x.item()]["nname"] for x in committee_tgtids])
print(c)