import dgl
import torch
import pandas as pd
from glob import glob
from tqdm import tqdm
import os
join = os.path.join


# Load, process node data
NODE_PATH = "../../../data/nodes.csv"
df_node = pd.read_csv(NODE_PATH)
df_node.set_index('nid', inplace=True)
node_types = list(set(df_node["ntype"].to_list()))
node_types.sort()
nid2nid = {}
for ntype in node_types:
    df_node_ntype1 = df_node[df_node["ntype"] == ntype]
    index1 = df_node_ntype1.index.to_list()
    df_node_ntype2 = df_node_ntype1.reset_index()
    index2 = df_node_ntype2.index.to_list()
    for i1, i2 in zip(index1, index2):
        nid2nid[i1] = i2


# Load, process edge data
EDGE_PATH = "../../../data/edges"
edge_files = glob(join(EDGE_PATH, "*.csv"))
edge_files.sort()
df_edge = []
data_dict = {}
for edge_file in tqdm(edge_files):
    spo = edge_file.split("/")[-1][:-4]
    s, p, o = spo.split("_")
    df_edge = pd.read_csv(edge_file)
    src_nids, tgt_nids = [], []
    for _, row in df_edge.iterrows():
        src_nids.append(nid2nid[row["src_nid"]])
        tgt_nids.append(nid2nid[row["tgt_nid"]])

    src_nids = torch.IntTensor(src_nids)
    tgt_nids = torch.IntTensor(tgt_nids)
    
    # SPO relation
    data_dict[(s, p, o)] = (src_nids, tgt_nids)

    # Inverse of SPO relation
    data_dict[(o, p + "_inv", s)] = (tgt_nids, src_nids)

# Create DGL graph
g = dgl.heterograph(data_dict)
print(g)
dgl.save_graphs("../../../data/graph.dgl", g)