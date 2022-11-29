import requests
import json
import pandas as pd
from collections import defaultdict

# senate file = '../bills_data/senate_joint_bills.json'
f = open('../bills_data/house_joint_bills.json')
data = f.readlines()
data = [x.strip('\n') for x in data]
data = [x.replace("\\n",".") for x in data]
data = [x.replace("..",".") for x in data]
json_str = ",".join(data)
json_str = "["+json_str+"]"
js_text = json.loads(json_str)
# len(data)

fin_list = []
for i in range(len(js_text)):
#     print(i)
    dict1 = defaultdict()
    ### id variables ###
    dict1['bill_id'] = js_text[i]['bill_id']
    # dict1['bill_type'] = js_text[0]['bill_type']
    # dict1['bill_number'] = js_text[0]['number']
    # dict1['congress'] = js_text[0]['congress']
    # bill_id,bill_type,bill_number,congress

    ### title variables ###
    dict1['official_title'] = js_text[i]['official_title']
    dict1['popular_title'] = js_text[i]['popular_title']
    dict1['short_title'] = js_text[i]['short_title']

    ### summary & KWs ###
    dict1['topic'] = js_text[i]['subjects_top_term']
    try:
        dict1['summary'] = js_text[i]['summary']['text']
    except :
        dict1['summary'] = ''
    dict1['subjects'] = js_text[i]['subjects']

    ### current status & history ###
    dict1['status'] = js_text[i]['status']
    dict1['veto'] = js_text[i]['history']['vetoed']
    dict1['enacted'] = js_text[i]['history']['enacted']
#     if dict1['enacted']:
#         dict1['law_number'] = js_text[i]['law_type'] + 'Law' + js_text[i]['congress'] + '-' + js_text[i]['number']
#     else:
#         dict1['law_number'] = ''

    ### sponsors & co-sponsors ###
    try :
        dict1['sponsor_id'] = js_text[i]['sponsor']['bioguide_id']
        dict1['sponsor_nm'] = js_text[i]['sponsor']['name']
        dict1['sponsor_state'] =js_text[i]['sponsor']['state']
    except :
        dict1['sponsor_id'],dict1['sponsor_nm'],dict1['sponsor_state'] = '','',''

    dict1['cosponsor_id'],dict1['cosponsor_nm'],dict1['cosponsor_state'] = [],[],[]
    for cosponsor in js_text[i]['cosponsors']:
        dict1['cosponsor_id'].append(cosponsor['bioguide_id'])
        dict1['cosponsor_nm'].append(cosponsor['name'])
        dict1['cosponsor_state'].append(cosponsor['state'])

    ### committees ### 
    dict1['comm_set'] = set()
    for committee in js_text[i]['committees'] :
        comm_id = committee['committee_id']
        dict1['comm_set'].add(comm_id)
    fin_list.append(dict1)

pd.DataFrame(fin_list).to_csv('../bills_data/house_joint_bills.csv',\
                              sep = '\x01',index=False)