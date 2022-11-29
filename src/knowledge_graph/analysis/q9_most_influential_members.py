"""
Use eigenvector centrality or pagerank centrality
on members connected with bills through (co)sponsorship
to determine most important/influential members in cluster
when it comes to proposing legislation.

NOTE: centrality is not used in the current code
"""

from get_subgraph import get_subgraph
import dgl
import pandas as pd
from tqdm import tqdm
from collections import Counter, defaultdict

(g,), _ = dgl.load_graphs('../../../data/graph.dgl')

df_node = pd.read_csv('../../../data/nodes.csv')
df_node_member = df_node[df_node["ntype"]=='member']
df_node_member.set_index("nname", inplace=True)
df_node_member_2 = df_node[df_node["ntype"]=='member']
df_node_member_2.set_index("nid_type", inplace=True)

df_votes = pd.read_csv('../../../data/house_116.csv')
df_votes.set_index("id", inplace=True)
# NOTE: senate currently not considered

valid_edge_types = [
    ('member', 'sponsorof', 'bill'),
    #('member', 'cosponsorof', 'bill')
    ]
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
        member_srcids, bill_tgtids = [], []
        m, b = sg.edges(etype=('member', 'sponsorof', 'bill'))
        member_srcids += m
        bill_tgtids += b
        # m, b = sg.edges(etype=('member', 'cosponsorof', 'bill'))
        # member_srcids += m
        # bill_tgtids += b

        member_names = []
        for x in member_srcids:
            member_row = df_votes.loc[df_node_member_2.loc[x.item()]["nname"]]
            member_name = ""
            member_name += member_row["first_name"]
            if type(member_row["middle_name"]) != float:
                member_name += " " + member_row["middle_name"]
            member_name += " " + member_row["last_name"]
            member_names.append(member_name)
        member_names = [x for x in member_names if type(x) == str]
        c = Counter(member_names)
        c_top = c.most_common(n)
        #print(c)
        df_out["topic"].append(topic)
        df_out["subtopic"].append(subtopic)
        df_out["cluster_id"].append(cluster_id)
        df_out["cluster_count"].append(len(member_ids))
        for i in range(n):
            if i < len(c_top):
                member_name, member_count = c_top[i]
                df_out["name_rank_" + str(i + 1)].append(member_name)
                df_out["count_rank_" + str(i + 1)].append(member_count)
            else:
                df_out["name_rank_" + str(i + 1)].append("")
                df_out["count_rank_" + str(i + 1)].append(0)
    
    #print()

df_out = pd.DataFrame(df_out)
df_out.to_csv("../../../data/q9_most_influential_members.csv", index=False)