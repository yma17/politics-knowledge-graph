import pandas as pd
from collections import defaultdict
from glob import glob
from tqdm import tqdm
import os
join = os.path.join

lines_to_print_node, lines_to_print_edge = [], []

#
# NODES
#
NODE_PATH = "../../../data/nodes.csv"
df_node = pd.read_csv(NODE_PATH)
lines_to_print_node += [f"Number of nodes (total) = {len(df_node)}"]
lines_to_print_node += [""]
node_types = list(set(df_node["ntype"].to_list()))
node_types.sort()
ntype2df = {}
for ntype in node_types:
    df_node_ntype = df_node[df_node["ntype"] == ntype]
    lines_to_print_node += [f"Number of nodes ({ntype}) = {len(df_node_ntype)}"]
    lines_to_print_node += [""]
    ntype2df[ntype] = df_node_ntype

#
# EDGES
#
EDGE_PATH = "../../../data/edges"
edge_files = glob(join(EDGE_PATH, "*.csv"))
edge_files.sort()
used_node_ids = set()
used_node_ids_by_ntype = defaultdict(lambda: set())
dfs_edges = []
for edge_file in edge_files:
    df_edge = pd.read_csv(edge_file)
    dfs_edges.append(df_edge)
dfs_edges = pd.concat(dfs_edges)
lines_to_print_edge += [f"Number of edges (total) = {len(dfs_edges)}"]
lines_to_print_edge += [""]
for edge_file in tqdm(edge_files):
    filename = edge_file.split("/")[-1][:-4].split("_")
    src_ntype, tgt_ntype = filename[0], filename[2]
    df_edge = pd.read_csv(edge_file)
    lines_to_print_edge += [f"Number of edges ({filename}) = {len(df_edge)}"]
    num_src = len(set(df_edge["src_nid"].to_list()))
    prop_src = num_src / len(ntype2df[src_ntype])
    num_tgt = len(set(df_edge["tgt_nid"].to_list()))
    prop_tgt = num_tgt / len(ntype2df[tgt_ntype])
    lines_to_print_edge += [f"   num. of all src ({src_ntype}) nodes adj to this edge type = {num_src}"]
    lines_to_print_edge += [f"   prop. of all src ({src_ntype}) nodes adj to this edge type = {prop_src:.4f}"]
    lines_to_print_edge += [f"   num. of all tgt ({tgt_ntype}) nodes adj to this edge type = {num_tgt}"]
    lines_to_print_edge += [f"   prop. of all tgt ({tgt_ntype}) nodes adj to this edge type = {prop_tgt:.4f}"]
    lines_to_print_edge += [""]
    for _, row in df_edge.iterrows():
        used_node_ids.add(row["src_nid"])
        used_node_ids_by_ntype[src_ntype].add(row["src_nid"])
        used_node_ids.add(row["tgt_nid"])
        used_node_ids_by_ntype[tgt_ntype].add(row["tgt_nid"])
num_nodes_used = len(used_node_ids)
prop_nodes_used = num_nodes_used / len(df_node)
i = 1
lines_to_print_node.insert(i, f"    num. of nodes adj to an edge = {num_nodes_used}")
lines_to_print_node.insert(i + 1, f"    prop. of nodes adj to an edge = {prop_nodes_used:.4f}")
for ntype in node_types:
    num_nodes_used = len(used_node_ids_by_ntype[ntype])
    prop_nodes_used = num_nodes_used / len(ntype2df[ntype])
    i += 4
    lines_to_print_node.insert(i, f"    num. of nodes adj to an edge = {num_nodes_used}")
    lines_to_print_node.insert(i + 1, f"    prop. of nodes adj to an edge = {prop_nodes_used:.4f}")

for line in lines_to_print_node + lines_to_print_edge:
    print(line)