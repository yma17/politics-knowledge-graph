"""
Author - Christian Clark
Last Updated - 10/17/2022

Details - This script formats the raw json vote data available from the GitHub US Congress project
from folders containing bill data into single .json documents for each house of Congress (the Senate and House of Representatives)
for each year of the 116th Congress

For more details on the original vote file structure, see https://github.com/unitedstates/congress/wiki/votes
"""

import os
import json

current_dir = os.getcwd()
years = [2019, 2020, 2021] # The years we need to get data for

def get_vote_dirs(path: str) -> list:
    """
    Given a path, return a list of tuples containing the path to each folder and its name
    """
    vote_list = []
    with os.scandir(path) as it:
        for entry in it:
            vote_list.append(entry.path)
    return vote_list

def get_folder_json_data(fp_list: list) -> list:
    """
    Given a list of bill file paths, return a json formatted list of all of the bill json data
    """
    vote_json = []
    for fp in fp_list:
            with os.scandir(fp) as it:
                for entry in it:
                    if "json" in entry.path:
                        with open(entry.path, "r") as f:
                            json_text = json.load(f)
                            vote_json.append(json_text)
    return vote_json

def write_vote_json_file(bill_json: list, output_fp: str) -> None:
    """
    Given a list of json objects and a file path for output, write the json to a file at the given path
    """
    with open(output_fp, "w+") as output:
            for b in bill_json:
                json.dump(b, output)
                output.write("\n")
    return

if __name__ == '__main__':
    print(current_dir)
    for year in years:
        year_fp = current_dir + "/" + str(year)
        votes = get_vote_dirs(year_fp)
        vote_json = get_folder_json_data(votes)
        output_fp = str(year) + "_votes.json"
        write_vote_json_file(vote_json, output_fp)
