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
    lineages['Patrilineage'] = lineages['Ego'].map(lambda x: patrilineage[x])
    lineages['Patriarch'] = lineages['Ego'].map(lambda x: paternal_founders[x])
    lineages['Matrilineage'] = lineages['Ego'].map(lambda x: matrilineage[x])
    lineages['Matriarch'] = lineages['Ego'].map(lambda x: maternal_founders[x])

    return lineages

def findPatLineage(df, ego):
    if np.isnan(ego):
        return [], None
    else:
        temp = df[df['Ego'] == ego]['Father'].values[0]
        if not np.isnan(temp):
            father_id = (int)(temp)
            lineage, founder = findPatLineage(df, father_id)
        else:
            lineage, founder = findPatLineage(df, temp)
        lineage.append(ego)
        if founder is None:
            founder = ego
        return lineage, founder

def findMatLineage(df, ego):
    if np.isnan(ego):
        return [], None
    else:
        temp = df[df['Ego'] == ego]['Mother'].values[0]
        if not np.isnan(temp):
            mother_id = (int)(temp)
            lineage, founder = findPatLineage(df, mother_id)
        else:
            lineage, founder = findPatLineage(df, temp)
        lineage.append(ego)
        if founder is None:
            founder = ego
        return lineage, founder


