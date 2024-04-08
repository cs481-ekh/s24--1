import pandas as pd # Excellent Documentation: https://pandas.pydata.org/docs/reference/frame.html
import numpy as np

# Dictionaries to store lineage and founders
patrilineage = {}
matrilineage = {}
paternal_founders = {}
maternal_founders = {}

# Takes in Complete DataFrame
# Returns DataFrame with columns:
    # 'Ego', 'Patrilineage', 'Patriarch', 'Pat. size', 'Matrilineage', 'Matriarch', 'Mat. size'
def findLineages(df):
    # Compute patrilineage and matrilineage for each individual
    for index, row in df.iterrows():
        patrilineage[row['Ego']], paternal_founders[row['Ego']] = findPatLineage(df, row['Ego'])
        matrilineage[row['Ego']], maternal_founders[row['Ego']] = findMatLineage(df, row['Ego'])

    lineages = pd.DataFrame()

    lineages['Ego'] = df['Ego']

    # Calculate the length of patrilineage and matrilineage for each individual
    lineages['Pat. Size'] = df['Ego'].map(lambda x: len(patrilineage[x]))
    lineages['Mat. Size'] = df['Ego'].map(lambda x: len(matrilineage[x]))

    # Add columns for paternal and maternal founders
    lineages['Patrilineage'], lineages['Patriarch'] = df['Ego'].map(lambda x: paternal_founders[x])
    lineages['Matrilineage'], lineages['Matriarch'] = df['Ego'].map(lambda x: maternal_founders[x])

def findPatLineage(df, ego):
    if ego == None:
        return [], None
    else:
        father_id = df[(df['Ego'] == ego), 'Father']
        lineage, founder = findPatLineage(df, father_id)
        lineage.append(ego)
        if founder is None:
            founder = ego
        return lineage, founder

def findMatLineage(df, ego):
    if ego == 0:
        return [], None
    else:
        mother_id = df.loc[ego, 'Mother']
        lineage, founder = findMatLineage(df, mother_id)
        lineage.append(ego)
        if founder is None:
            founder = ego
        return lineage, founder


