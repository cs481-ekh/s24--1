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
    try:
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
    except:
        print("There was a problem finding lineages data")

# Recursively Finds Father(s) and returns list for each with founder
def findPatLineage(df, ego):
    try:
        # Base Case (Ego is Founder)
        if np.isnan(ego):
            return [], None
        else:
            # Gets Father (potentially nan)
            temp = df[df['Ego'] == ego]['Father'].values[0]
            # Converts to int if not nan
            # Recursively calls
            if not np.isnan(temp):
                father_id = (int)(temp)
                lineage, founder = findPatLineage(df, father_id)
            else:
                lineage, founder = findPatLineage(df, temp)
            # adds ego to lineage list
            lineage.append(ego)
            # sets founder
            if founder is None:
                founder = ego
            return lineage, founder
    except:
        print("There was a error finding the Patrilineage for %i", ego)

# Recursively Finds Mother(s) and returns list for each with founder
def findMatLineage(df, ego):
    try:
        # Base Case (Ego is Founder)
        if np.isnan(ego):
            return [], None
        else:
            # Gets Mother (potentially nan)
            temp = df[df['Ego'] == ego]['Mother'].values[0]
            # Converts to int if not nan
            # Recursively calls
            if not np.isnan(temp):
                mother_id = (int)(temp)
                lineage, founder = findPatLineage(df, mother_id)
            else:
                lineage, founder = findPatLineage(df, temp)
            # adds ego to lineage list
            lineage.append(ego)
            # sets founder
            if founder is None:
                founder = ego
            return lineage, founder
    except:
        print("There was a error finding the Matrilineage for %i", ego)


