"""
Author - Christian Clark
Last Updated - 10/17/2022

Details - This script formats the raw json bill data available from the GitHub US Congress project
from folders containing bill data into single .json documents for each house of Congress (the Senate and House of Representatives)

For more details on the original bill file structure, see https://github.com/unitedstates/congress/wiki/bills
"""

import os
import json

current_dir = os.getcwd()
bill_dirs = ["/s","/hr"] #senate bill folder, house bill folder
output_fps = ["senate_bills.json","house_bills.json"] # The output file names

def get_bill_dirs(path: str) -> list:
    """
    Given a path, return a list of tuples containing the path to each folder and its name
    """
    bill_list = []
    bill_names = []
    with os.scandir(path) as it:
        for entry in it:
            bill_list.append(entry.path)
            bill_names.append(entry.name)
    return list(zip(bill_list, bill_names))

def get_folder_json_data(bills: list) -> list:
    """
    Given a list of bill file paths, return a json formatted list of all of the bill json data
    """
    bill_json = []
    for b in bills:
            fp = b[0]
            with os.scandir(fp) as it:
                for entry in it:
                    if "json" in entry.path:
                        with open(entry.path, "r") as f:
                            json_text = json.load(f)
                            bill_json.append(json_text)
    return bill_json

def write_bill_json_file(bill_json: list, output_fp: str) -> None:
    """
    Given a list of json objects and a file path for output, write the json to a file at the given path
    """
    with open(output_fp, "w+") as output:
            for b in bill_json:
                json.dump(b, output)
                output.write("\n")
    return

if __name__ == '__main__':
    for i, dir in enumerate(bill_dirs):
        bills = get_bill_dirs(current_dir)
        bill_json = get_folder_json_data(bills)
        write_bill_json_file(bill_json, output_fps[i])
        