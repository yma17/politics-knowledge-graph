"""
Script to derive edge files of knowledge graph.
One file will be created per edge type.
The SPO relations (aka edge types) are as follows:
- Member -> [a member of ] -> Political party
- Member -> [a member of ] -> Chamber
- Member -> [vote “yea” on ] -> Vote
- Member -> [vote “nay” on ] -> Vote
- Member -> [is a member of ] -> Committee
- Member -> [is a member of ] -> Subcommittee
- Subcommittee -> [is part of ] -> Committee
- Committee -> [is based in ] -> Chamber
- Vote -> [on ] -> Bill
- Vote -> [occurred in ] -> Chamber
- Member -> [is a sponsor of ] -> Bill
- Member -> [is a cosponsor of ] -> Bill
<11/12/22: removed for now> - Vote -> [occurred before ] -> Vote
- Bill -> [discusses ] -> Topic
- Topic -> [relates to ] -> Topic
- Committee -> [focuses on ] -> Topic
- Subcommittee -> [focuses on ] -> Topic
- Lobbyist -> [paid money to ] -> Member 
"""

import pandas as pd
import editdistance
from tqdm import tqdm
import numpy as np
import json
from glob import glob
from pathlib import Path
import os
join = os.path.join


### LOAD IN DATA ###
# TODO: bill & bill text
df_committee_house = pd.read_csv("../../data/house_committees_v2.csv")
df_committee_sen = pd.read_csv("../../data/senate_committees_v2.csv")
df_committee_joint = pd.read_csv("../../data/joint_committees.csv")

with open("../../data/house_committee_memberships.json", "r") as f:
    house_cm = json.load(f)
with open("../../data/senate_committee_memberships.json", "r") as f:
    senate_cm = json.load(f)
with open("../../data/joint_committee_memberships.json", "r") as f:
    joint_cm = json.load(f)

df_lobbyist = pd.concat([
    pd.read_csv(fname) for fname in glob("../../data/contributions_*.csv")])

df_member_house = pd.read_csv("../../data/house_116.csv")
df_member_sen = pd.read_csv("../../data/senate_116.csv")

df_vote_house = pd.read_csv("../../data/house_votes.csv", dtype=str)
df_vote_house['number'] = df_vote_house['number'].astype(int)
df_vote_house['session'] = df_vote_house['session'].astype(int)
df_vote_house = df_vote_house[df_vote_house["session"] != 2021]
df_vote_house = df_vote_house.sort_values(by=["session", "number"])
df_vote_sen = pd.read_csv("../../data/senate_votes.csv", dtype=str)
df_vote_sen['number'] = df_vote_sen['number'].astype(int)
df_vote_sen['session'] = df_vote_sen['session'].astype(int)
df_vote_sen = df_vote_sen[df_vote_sen["session"] != 2021]
df_vote_sen = df_vote_sen.sort_values(by=["session", "number"])

df_node = pd.read_csv("../../data/nodes.csv")


### INITIALIZE HELPER VARIABLES / FUNCTIONS
nkey2nid = {}
for _, row in df_node.iterrows():
    nkey2nid[row["ntype_name"]] = row["nid"]

df_node_com = df_node[df_node["ntype"] == "committee"]
df_node_subcom = df_node[df_node["ntype"] == "subcommittee"]
com_list = df_node_com["nname"].to_list()
subcom_list = df_node_subcom["nname"].to_list()

member2id = {}
for df in [df_member_house, df_member_sen]:
    for _, row in df.iterrows():
        k = row["first_name"] + " " + row["last_name"] + " " + row["state"]
        member2id[k] = row["id"]
m_list = list(member2id.keys())

def find_matching_str(str_list, query_str, tol=np.inf):
    matching_str = None
    best_ed = np.inf
    for str in str_list:
        ed = editdistance.eval(query_str.lower(), str.lower())
        if ed < best_ed:
            best_ed = ed
            matching_str = str
    return matching_str if best_ed <= tol else None


### DERIVE EDGE FILES ###
EDGE_PATH = "../../data/edges"
Path(EDGE_PATH).mkdir(parents=True, exist_ok=True)

# Member -> [a member of ] -> Political party
edge_data = {"src_nid": [], "tgt_nid": []}
for df in [df_member_house, df_member_sen]:
    for _, row in df.iterrows():
        edge_data["src_nid"].append(nkey2nid["member_"+row["id"]])
        edge_data["tgt_nid"].append(nkey2nid["party_"+row["party"]])
pd.DataFrame(edge_data).drop_duplicates().sort_values(by=['src_nid', 'tgt_nid']).to_csv(
    join(EDGE_PATH, "member_memberof_party.csv"), index=False)

# Member -> [a member of ] -> Chamber
edge_data = {"src_nid": [], "tgt_nid": []}
for _, row in df_member_house.iterrows():
    edge_data["src_nid"].append(nkey2nid["member_"+row["id"]])
    edge_data["tgt_nid"].append(nkey2nid["chamber_house"])
for _, row in df_member_sen.iterrows():
    edge_data["src_nid"].append(nkey2nid["member_"+row["id"]])
    edge_data["tgt_nid"].append(nkey2nid["chamber_senate"])
pd.DataFrame(edge_data).drop_duplicates().sort_values(by=['src_nid', 'tgt_nid']).to_csv(
    join(EDGE_PATH, "member_memberof_chamber.csv"), index=False)

# Member -> [vote “yea” on ] -> Vote
# Member -> [vote “nay” on ] -> Vote
edge_data_yea = {"src_nid": [], "tgt_nid": []}
edge_data_nay = {"src_nid": [], "tgt_nid": []}
# (house votes)
vote_cols = [col for col in df_vote_house.columns if "vote_" in col]
for _, row in df_vote_house.iterrows():
    for col in vote_cols:
        member_id = col.split("_")[-1]
        if "member_"+member_id not in nkey2nid.keys():
            continue
        if row[col] == "Yea":
            edge_data_yea["src_nid"].append(nkey2nid["member_"+member_id])
            edge_data_yea["tgt_nid"].append(nkey2nid["vote_"+row["vote_id"]])
        elif row[col] == "Nay":
            edge_data_nay["src_nid"].append(nkey2nid["member_"+member_id])
            edge_data_nay["tgt_nid"].append(nkey2nid["vote_"+row["vote_id"]])
# (senate votes)
lis2id = {}
for _, row in df_member_sen.iterrows():
    lis2id[row["lis_id"]] = row["id"]
vote_cols = [col for col in df_vote_sen.columns if "vote_S" in col]
for _, row in df_vote_sen.iterrows():
    for col in vote_cols:
        member_id = lis2id[col.split("_")[-1]]
        if "member_"+member_id not in nkey2nid.keys():
            continue
        if row[col] == "Yea":
            edge_data_yea["src_nid"].append(nkey2nid["member_"+member_id])
            edge_data_yea["tgt_nid"].append(nkey2nid["vote_"+row["vote_id"]])
        elif row[col] == "Nay":
            edge_data_nay["src_nid"].append(nkey2nid["member_"+member_id])
            edge_data_nay["tgt_nid"].append(nkey2nid["vote_"+row["vote_id"]])
pd.DataFrame(edge_data_yea).drop_duplicates().sort_values(by=['src_nid', 'tgt_nid']).to_csv(
    join(EDGE_PATH, "member_votedyeaon_vote.csv"), index=False)
pd.DataFrame(edge_data_nay).drop_duplicates().sort_values(by=['src_nid', 'tgt_nid']).to_csv(
    join(EDGE_PATH, "member_votednayon_vote.csv"), index=False)

# Member -> [is a member of ] -> Committee
edge_data = {"src_nid": [], "tgt_nid": []}
for cm in [house_cm, senate_cm, joint_cm]:
    committees = list(cm.keys())
    for c in committees:
        committee = find_matching_str(com_list, c)
        for mname, mstate in cm[c]["members"]:
            member = find_matching_str(m_list, mname + " " + mstate)
            edge_data["src_nid"].append(nkey2nid["member_"+member2id[member]])
            edge_data["tgt_nid"].append(nkey2nid["committee_"+committee])
pd.DataFrame(edge_data).drop_duplicates().sort_values(by=['src_nid', 'tgt_nid']).to_csv(
    join(EDGE_PATH, "member_memberof_committee.csv"), index=False)

# Member -> [is a member of ] -> Subcommittee
edge_data = {"src_nid": [], "tgt_nid": []}
for cm in [house_cm, senate_cm]:
    committees = list(cm.keys())
    for c in committees:
        subcommittees = list(set(cm[c].keys()) - {"members"})
        for sc in subcommittees:
            subcommittee = find_matching_str(subcom_list, sc)
            for mname, mstate in cm[c][sc]["members"]:
                member = find_matching_str(m_list, mname + " " + mstate)
                edge_data["src_nid"].append(nkey2nid["member_"+member2id[member]])
                edge_data["tgt_nid"].append(nkey2nid["subcommittee_"+subcommittee])
pd.DataFrame(edge_data).drop_duplicates().sort_values(by=['src_nid', 'tgt_nid']).to_csv(
    join(EDGE_PATH, "member_memberof_subcommittee.csv"), index=False)

# Subcommittee -> [is part of ] -> Committee
edge_data = {"src_nid": [], "tgt_nid": []}
for cm in [house_cm, senate_cm]:
    committees = list(cm.keys())
    for c in committees:
        committee = find_matching_str(com_list, c)
        subcommittees = list(set(cm[c].keys()) - {"members"})
        for sc in subcommittees:
            subcommittee = find_matching_str(subcom_list, sc)
            edge_data["src_nid"].append(nkey2nid["subcommittee_"+subcommittee])
            edge_data["tgt_nid"].append(nkey2nid["committee_"+committee])
pd.DataFrame(edge_data).drop_duplicates().sort_values(by=['src_nid', 'tgt_nid']).to_csv(
    join(EDGE_PATH, "subcommittee_partof_committee.csv"), index=False)

# Committee -> [is based in ] -> Chamber
edge_data = {"src_nid": [], "tgt_nid": []}
committees = list(house_cm.keys())
for c in committees:
    committee = find_matching_str(com_list, c)
    edge_data["src_nid"].append(nkey2nid["committee_"+committee])
    edge_data["tgt_nid"].append(nkey2nid["chamber_house"])
committees = list(senate_cm.keys())
for c in committees:
    committee = find_matching_str(com_list, c)
    edge_data["src_nid"].append(nkey2nid["committee_"+committee])
    edge_data["tgt_nid"].append(nkey2nid["chamber_senate"])
committees = list(joint_cm.keys())
for c in committees:
    committee = find_matching_str(com_list, c)
    edge_data["src_nid"].append(nkey2nid["committee_"+committee])
    edge_data["tgt_nid"].append(nkey2nid["chamber_house"])
    edge_data["src_nid"].append(nkey2nid["committee_"+committee])
    edge_data["tgt_nid"].append(nkey2nid["chamber_senate"])
pd.DataFrame(edge_data).drop_duplicates().sort_values(by=['src_nid', 'tgt_nid']).to_csv(
    join(EDGE_PATH, "committee_basedin_chamber.csv"), index=False)

# Vote -> [on ] -> Bill
pass  # TODO

# Vote -> [occurred in ] -> Chamber
edge_data = {"src_nid": [], "tgt_nid": []}
for _, row in df_vote_house.iterrows():
    edge_data["src_nid"].append(nkey2nid["vote_"+row["vote_id"]])
    edge_data["tgt_nid"].append(nkey2nid["chamber_house"])
for _, row in df_vote_sen.iterrows():
    edge_data["src_nid"].append(nkey2nid["vote_"+row["vote_id"]])
    edge_data["tgt_nid"].append(nkey2nid["chamber_senate"])
pd.DataFrame(edge_data).drop_duplicates().sort_values(by=['src_nid', 'tgt_nid']).to_csv(
    join(EDGE_PATH, "vote_occurredin_chamber.csv"), index=False)

# Member -> [is a sponsor of ] -> Bill
pass  # TODO

# Member -> [is a cosponsor of ] -> Bill
pass  # TODO

# # Vote -> [occurred before ] -> Vote
# edge_data = {"src_nid": [], "tgt_nid": []}
# df_node_vote_house = df_node[(df_node["ntype"] == "vote") & (df_node["nname"].isin(df_vote_house["vote_id"]))]
# ntype_name_list = df_node_vote_house["ntype_name"].to_list()
# for i in range(1, len(ntype_name_list)):
#     edge_data["src_nid"].append(nkey2nid[ntype_name_list[i-1]])
#     edge_data["tgt_nid"].append(nkey2nid[ntype_name_list[i]])
# df_node_vote_sen = df_node[(df_node["ntype"] == "vote") & (df_node["nname"].isin(df_vote_sen["vote_id"]))]
# ntype_name_list = df_node_vote_sen["ntype_name"].to_list()
# for i in range(1, len(ntype_name_list)):
#     edge_data["src_nid"].append(nkey2nid[ntype_name_list[i-1]])
#     edge_data["tgt_nid"].append(nkey2nid[ntype_name_list[i]])
# pd.DataFrame(edge_data).drop_duplicates().sort_values(by=['src_nid', 'tgt_nid']).to_csv(
#     join(EDGE_PATH, "vote_occurredbefore_vote.csv"), index=False)

# Bill -> [discusses ] -> Topic
pass  # TODO

# Topic -> [relates to ] -> Topic
pass  # TODO

# Committee -> [focuses on ] -> Topic
pass  # TODO

# Subcommittee -> [focuses on ] -> Topic
pass  # TODO

# Lobbyist -> [paid money to ] -> Member
edge_data = {"src_nid": [], "tgt_nid": []}
pbar = tqdm(total=len(df_lobbyist))
for _, row in df_lobbyist.iterrows():
    pbar.update(1)
    m = row["honoree_name"]
    if type(m) == float:
        continue
    m = m.lower()
    for x in ["for united states congress", "for Congress", "for congress, inc.", "Senator", "Congressman", "Congresswoman", "Rep.", "Representative", "for Senate", "for House", "special election", "friends of"]:
        m = m.replace(x.lower(), "")
    member = find_matching_str(m_list, m, tol=6)
    if member is None:
        continue
    edge_data["src_nid"].append(nkey2nid["lobbyist_"+row["registrant"]])
    edge_data["tgt_nid"].append(nkey2nid["member_"+member2id[member]])
pbar.close()
pd.DataFrame(edge_data).drop_duplicates().sort_values(by=['src_nid', 'tgt_nid']).to_csv(
    join(EDGE_PATH, "lobbyist_paidto_member.csv"), index=False)