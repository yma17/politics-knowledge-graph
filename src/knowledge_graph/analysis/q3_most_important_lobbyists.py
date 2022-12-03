"""Q3: Who are the most important lobbyists?"""

from get_subgraph import get_subgraph
import dgl
import pandas as pd
from tqdm import tqdm
from collections import Counter, defaultdict

(g,), _ = dgl.load_graphs('../../../data/graph.dgl')

df_node = pd.read_csv('../../../data/nodes.csv')
df_node_member = df_node[df_node["ntype"]=='member']
df_node_member.set_index("nname", inplace=True)
df_node_lobbyist = df_node[df_node["ntype"]=='lobbyist']
df_node_lobbyist.set_index("nid_type", inplace=True)

valid_edge_types = [
    ('member', 'paidto_inv', 'lobbyist')]
n = 5

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
        member_srcids, lobbyist_tgtids = sg.edges(etype=('member', 'paidto_inv', 'lobbyist'))

        c = Counter([df_node_lobbyist.loc[x.item()]["nname"] for x in lobbyist_tgtids])
        c_top = c.most_common(n)
        #print(c)
        df_out["topic"].append(topic)
        df_out["subtopic"].append(subtopic)
        df_out["cluster_id"].append(cluster_id)
        df_out["cluster_count"].append(len(member_ids))
        for i in range(n):
            if i < len(c_top):
                lobbyist_name, lobbyist_count = c_top[i]
                df_out["name_rank_" + str(i + 1)].append(lobbyist_name)
                df_out["count_rank_" + str(i + 1)].append(lobbyist_count)
            else:
                df_out["name_rank_" + str(i + 1)].append("")
                df_out["count_rank_" + str(i + 1)].append(0)
    
    #print()

df_out = pd.DataFrame(df_out)
df_out.to_csv("../../../data/q3_most_important_lobbyists.csv", index=False)