"""Q1: What is the distribution of political parties?"""

from get_subgraph import get_subgraph
import dgl
import pandas as pd
from tqdm import tqdm
from collections import Counter, defaultdict

(g,), _ = dgl.load_graphs('../../../data/graph.dgl')

df_node = pd.read_csv('../../../data/nodes.csv')
df_node_member = df_node[df_node["ntype"]=='member']
df_node_member.set_index("nname", inplace=True)
df_node_party = df_node[df_node["ntype"]=='party']
df_node_party.set_index("nid_type", inplace=True)

valid_edge_types = [
    ('member', 'memberof', 'party')]

df_out = defaultdict(lambda: [])

df_cluster = pd.read_csv("../../../data/voter_clusters.csv")
df_cluster.set_index("voters", inplace=True)
for col in tqdm(df_cluster.columns):
    #print(col)
    df_cluster[col] = df_cluster[col].astype(int)

    topic, subtopic, _ = col.split("_")
    topic, subtopic = topic.strip(), subtopic.strip()

    clusters = df_cluster[col].groupby(df_cluster[col].to_list())
    for cluster_id, member_ids in clusters.groups.items():
        member_ids = member_ids.to_list()
        start_node_ids = {"member": []}
        for x in member_ids:
            try:
                start_node_ids["member"].append(df_node_member.loc[x.split("_")[-1]]["nid_type"])
            except KeyError:
                pass

        sg = get_subgraph(g, start_node_ids, valid_edge_types)
        member_srcids, party_tgtids = sg.edges(etype=('member', 'memberof', 'party'))

        c = Counter([df_node_party.loc[x.item()]["nname"] for x in party_tgtids])
        #print(c)
        df_out["topic"].append(topic)
        df_out["subtopic"].append(subtopic)
        df_out["cluster_id"].append(cluster_id)
        df_out["cluster_count"].append(len(member_ids))
        for p in df_node_party["nname"]:
            df_out[p].append(c[p] if p in c.keys() else 0)
    
    #print()

df_out = pd.DataFrame(df_out)
df_out.to_csv("../../../data/q1_party_distribution.csv", index=False)