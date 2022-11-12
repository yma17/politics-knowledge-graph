"""
Script to derive node file of knowledge graph.
All nodes (regardless of type) will be in a single file.
The node types are as follows:
- Political party
- Chamber
- Bill
- Topic
- Committee
- Subcommittee
- Member
- Vote
- Lobbyist
"""

import pandas as pd
from glob import glob
import os
join = os.path.join

### LOAD IN DATA ###
# TODO: bill & bill text
df_committee_house = pd.read_csv("../../data/house_committees_v2.csv")
df_committee_sen = pd.read_csv("../../data/senate_committees_v2.csv")
df_committee_joint = pd.read_csv("../../data/joint_committees.csv")

df_lobbyist = pd.concat([
    pd.read_csv(fname) for fname in glob("../../data/contributions_*.csv")])  # don't use 2021

df_member_house = pd.read_csv("../../data/house_116.csv")
df_member_sen = pd.read_csv("../../data/senate_116.csv")

df_vote_house = pd.read_csv("../../data/house_votes.csv", dtype=str)
df_vote_house['number'] = df_vote_house['number'].astype(int)
df_vote_house['session'] = df_vote_house['session'].astype(int)
df_vote_house = df_vote_house[df_vote_house["session"] != 2021]  # filter out 2021
df_vote_house = df_vote_house.sort_values(by=["session", "number"])
df_vote_sen = pd.read_csv("../../data/senate_votes.csv", dtype=str)
df_vote_sen['number'] = df_vote_sen['number'].astype(int)
df_vote_sen['session'] = df_vote_sen['session'].astype(int)
df_vote_sen = df_vote_sen[df_vote_sen["session"] != 2021]  # filter out 2021
df_vote_sen = df_vote_sen.sort_values(by=["session", "number"])


### DERIVE NODE FILE ###
node_data = {"nid": [], "ntype": [], "nname": [], "ntype_name": []}

# Political party
party_set = list(set(df_member_house["party"].to_list() +
                df_member_sen["party"].to_list()))
party_set.sort()
for item in party_set:
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("party")
    node_data["nname"].append(item)
    node_data["ntype_name"].append("party" + "_" + item)

# Chamber
chamber_set = ["house", "senate"]
for item in chamber_set:
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("chamber")
    node_data["nname"].append(item)
    node_data["ntype_name"].append("chamber" + "_" + item)

# Bill
pass  # TODO

# Topic
pass  # TODO

# Committee
committee_set = list(set(df_committee_house["name_x"].to_list() +
                    df_committee_sen["name_x"].to_list() +
                    df_committee_joint["name"].to_list()))
committee_set.sort()
for item in committee_set:
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("committee")
    node_data["nname"].append(item)
    node_data["ntype_name"].append("committee" + "_" + item)

# Subcommittee
subcommittee_set = []
for _, row in df_committee_house.iterrows():
    sub_c, parent_c = row["name_y"], row["id_x"]
    if type(row["name_y"]) == float:
        continue
    subcommittee_set += [sub_c + f" ({parent_c})"]
for _, row in df_committee_sen.iterrows():
    if type(row["name_y"]) == float:
        continue
    sub_c, parent_c = row["name_y"], row["id_x"]
    subcommittee_set += [sub_c + f" ({parent_c})"]
subcommittee_set = list(set(subcommittee_set))
for item in subcommittee_set:
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("subcommittee")
    node_data["nname"].append(item)
    node_data["ntype_name"].append("subcommittee" + "_" + item)

# Member
member_set = list(set(df_member_house["id"].to_list() +
                    df_member_sen["id"].to_list()))
member_set.sort()
for item in member_set:
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("member")
    node_data["nname"].append(item)
    node_data["ntype_name"].append("member" + "_" + item)

# Vote
vote_set = df_vote_house["vote_id"].to_list() + df_vote_sen["vote_id"].to_list()
for item in vote_set:
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("vote")
    node_data["nname"].append(item)
    node_data["ntype_name"].append("vote" + "_" + item)

# Lobbyist
lobbyist_set = list(set(df_lobbyist["registrant"].to_list()))
lobbyist_set.sort()
for item in lobbyist_set:
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("lobbyist")
    node_data["nname"].append(item)
    node_data["ntype_name"].append("lobbyist" + "_" + item)

NODE_PATH = "../../data/nodes.csv"
pd.DataFrame(node_data).to_csv(NODE_PATH, index=False)