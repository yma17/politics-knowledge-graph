import pandas as pd
import numpy as np
from kmodes.kmodes import KModes

df = pd.read_csv('House_Data_For_Clustering v01.csv')
df.replace("Yea",1,inplace=True)
df.replace("Nay",-1,inplace=True)
df.replace("Present",0,inplace=True)
df.replace("Not Voting",0,inplace=True)
df.fillna(2,inplace=True)

cat_cols = ['bill_id','topic', 'subject'] + [i for i in df.columns if 'vote' in i]
df_cat = df[cat_cols]

topics_list = ['Government operations and politics','Finance and financial sector',\
'Economics and public finance','Armed forces and national security','Health']
topic_subject_dict = {}

for topic in topics_list:
    top_10_subs = list(df_cat[df_cat['topic'] == topic].groupby(['subject'])['bill_id'].nunique().reset_index().sort_values('bill_id',ascending=False).reset_index().loc[:9,'subject'].values)
    topic_subject_dict[topic] = top_10_subs

fin_cluster_df = pd.DataFrame({'voters':list(df_cat.columns)[4:]})
for topic in topic_subject_dict.keys():
    for subject in topic_subject_dict[topic]:
#         print(topic,':',subject)
        df_filter = df_cat[(df_cat['topic']==topic)&(df_cat['subject']==subject)]
        dfMatrix = df_filter.iloc[:,4:].to_numpy().T
        kmodes = KModes(n_jobs = -1, n_clusters = 3, init = 'Huang', random_state = 0)
        kmodes.fit_predict(dfMatrix)
        
        df_cat_transposed = df_filter.iloc[:,3:].T
        df_cat_transposed.columns=df_cat_transposed.iloc[0]
        df_cat_transposed = df_cat_transposed.iloc[1:]

        # Add the cluster to the dataframe
        colname= "_".join([topic,subject,'cluster'])
        df_cat_transposed[colname] = kmodes.labels_
        cluster_df = df_cat_transposed[[colname]].reset_index
        fin_cluster_df = pd.concat([fin_cluster_df,cluster_df],axis=1)

fin_cluster_df = fin_cluster_df.loc['vote_A000374':,:]
fin_cluster_df['voters'] = fin_cluster_df.index
fin_cluster_df.to_csv('voter_clusters.csv',index=False)