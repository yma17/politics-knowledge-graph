"""
Script to derive node file of knowledge graph.
All nodes (regardless of type) will be in a single file.
The node types are as follows:
- Political party
- Chamber
- Bill
- Topic (Includes SubTopic too)
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
df_bills_house = pd.read_csv("../../../data/house_bills.csv", sep='\x01')
df_bills_sen = pd.read_csv("../../../data/senate_bills.csv", sep='\x01')

df_topics_house = pd.read_csv("../../../data/house_topics_subjects.tsv", sep = "\t")
df_topics_sen = pd.read_csv("../../../data/senate_topics_subjects.tsv", sep = "\t")

df_committee_house = pd.read_csv("../../../data/house_committees_v2.csv")
df_committee_sen = pd.read_csv("../../../data/senate_committees_v2.csv")
df_committee_joint = pd.read_csv("../../../data/joint_committees.csv")

df_lobbyist = pd.concat([
    pd.read_csv(fname) for fname in glob("../../../data/contributions_*.csv")])  # don't use 2021

df_member_house = pd.read_csv("../../../data/house_116.csv")
df_member_sen = pd.read_csv("../../../data/senate_116.csv")

df_vote_house = pd.read_csv("../../../data/house_votes.csv", dtype=str)
df_vote_house['number'] = df_vote_house['number'].astype(int)
df_vote_house['session'] = df_vote_house['session'].astype(int)
df_vote_house = df_vote_house[df_vote_house["session"] != 2021]  # filter out 2021
df_vote_house = df_vote_house.sort_values(by=["session", "number"])

df_vote_sen = pd.read_csv("../../../data/senate_votes.csv", dtype=str)
df_vote_sen['number'] = df_vote_sen['number'].astype(int)
df_vote_sen['session'] = df_vote_sen['session'].astype(int)
df_vote_sen = df_vote_sen[df_vote_sen["session"] != 2021]  # filter out 2021
df_vote_sen = df_vote_sen.sort_values(by=["session", "number"])


### DERIVE NODE FILE ###
node_data = {"nid": [], "ntype": [], "nid_type": [], "nname": [], "ntype_name": []}

# Political party
party_set = list(set(df_member_house["party"].to_list() +
                df_member_sen["party"].to_list()))
party_set.sort()
for i, item in enumerate(party_set):
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("party")
    node_data["nid_type"].append(i)
    node_data["nname"].append(item)
    node_data["ntype_name"].append("party" + "_" + item)

# Chamber
chamber_set = ["house", "senate"]
for i, item in enumerate(chamber_set):
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("chamber")
    node_data["nid_type"].append(i)
    node_data["nname"].append(item)
    node_data["ntype_name"].append("chamber" + "_" + item)

# Bill
bill_set_house = list(set(df_bills_house['bill_id'].to_list()))
bill_set_senate = list(set(df_bills_sen['bill_id'].to_list()))
bill_set_house.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
bill_set_senate.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
bill_set = bill_set_house + bill_set_senate
for i, item in enumerate(bill_set):
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("bill")
    node_data["nid_type"].append(i)
    node_data["nname"].append(item)
    node_data["ntype_name"].append("bill" + "_" + item)

# Topic (includes subtopics)
topic_set = list(set(df_topics_house['topic'].str.strip().to_list() + df_topics_sen['topic'].str.strip().to_list() +
                df_topics_house['subject'].str.strip().to_list() + df_topics_sen['subject'].str.strip().to_list()))
topic_set.sort()
for i, item in enumerate(topic_set):
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("topic")
    node_data["nid_type"].append(i)
    node_data["nname"].append(item)
    node_data["ntype_name"].append("topic" + "_" + item)

# Committee
committee_set = list(set(df_committee_house["name_x"].to_list() +
                    df_committee_sen["name_x"].to_list() +
                    df_committee_joint["name"].to_list()))
committee_set.sort()
for i, item in enumerate(committee_set):
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("committee")
    node_data["nid_type"].append(i)
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
for i, item in enumerate(subcommittee_set):
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("subcommittee")
    node_data["nid_type"].append(i)
    node_data["nname"].append(item)
    node_data["ntype_name"].append("subcommittee" + "_" + item)

# Member
member_set = list(set(df_member_house["id"].to_list() +
                    df_member_sen["id"].to_list()))
member_set.sort()
for i, item in enumerate(member_set):
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("member")
    node_data["nid_type"].append(i)
    node_data["nname"].append(item)
    node_data["ntype_name"].append("member" + "_" + item)

# Vote
vote_set = df_vote_house["vote_id"].to_list() + df_vote_sen["vote_id"].to_list()
for i, item in enumerate(vote_set):
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("vote")
    node_data["nid_type"].append(i)
    node_data["nname"].append(item)
    node_data["ntype_name"].append("vote" + "_" + item)

# Lobbyist
lobbyist_set = list(set(df_lobbyist["registrant"].to_list()))
lobbyist_set.sort()
for i, item in enumerate(lobbyist_set):
    node_data["nid"].append(len(node_data["nid"]))
    node_data["ntype"].append("lobbyist")
    node_data["nid_type"].append(i)
    node_data["nname"].append(item)
    node_data["ntype_name"].append("lobbyist" + "_" + item)


# Save the node data into csv file
NODE_PATH = "../../../data/nodes.csv"
pd.DataFrame(node_data).to_csv(NODE_PATH, index=False)