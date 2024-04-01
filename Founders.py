import pandas as pd # Excellent Documentation: https://pandas.pydata.org/docs/reference/frame.html
import numpy as np
import warnings


# Takes in complete dataframe
# Returns dataframe updated df and a new dataframe of Founders (Ego, Father, Mother, Sex, Living)
# Missing Mother/Father becomes a Founder
def findFounders(df):
    # Get all unique Ego IDs, Father IDs, and Mother IDs
    all_egos = set(df['Ego'])

    # Find individuals who have both parents as None or a singular missing parent
    founders = pd.DataFrame()

    # Iterate over each unique Ego ID
    for ego in all_egos:
        father = df.loc[df['Ego'] == ego, 'Father'].iloc[0]
        mother = df.loc[df['Ego'] == ego, 'Mother'].iloc[0]

        # Check if both parents are None or one parent is missing
        if (father is None and mother is None):
            temp = df[df['Ego'] == ego]
            founders = pd.concat([founders, temp])

        # If Father is missing, create a new entry for the Father
        if father is None and mother is not None:
            newEgoID = df['Ego'].max() + 1
            # Create a new entry with the missing father
            new_entry = [{'Ego': newEgoID, 'Father': None, 'Mother': None, 'Sex': 'M', 'Living': None}]
            founders = pd.concat([founders, pd.DataFrame(new_entry)])
            df = pd.concat([df, pd.DataFrame(new_entry)])
            # Update Child to reflect new parent entry
            warnings.simplefilter('ignore')
            df[df['Ego'] == ego]['Father'] = newEgoID # TODO: Causes Warning but works!

        # If Mother is missing, create a new entry for the Mother
        if mother is None and father is not None:
            # Create a new entry with the missing mother
            newEgoID = df['Ego'].max() + 1
            new_entry = [{'Ego': newEgoID, 'Father': None, 'Mother': None, 'Sex': 'F', 'Living': None}]
            # Save Parent as Founder and add to df
            founders = pd.concat([founders, pd.DataFrame(new_entry)])
            df = pd.concat([df, pd.DataFrame(new_entry)])
            # Update Child to reflect new parent entry
            warnings.simplefilter('ignore')
            df[df['Ego'] == ego]['Mother'] = newEgoID # TODO: Causes Warning but works!

    return df, founders


# Takes in complete dataframe and Founders DataFrame
# Returns list of statistics (5 elements)
# Avg. Rounded to 3rd decimal
def getStats(df, founders):
    # Order: [Founders Count, Max descendants, Max Living descendants, Avg descendants, Avg Living descendants]
    stats = []

    # Founders Count
    stats.append(len(founders))

    # Initialize variables for other stats
    maxDesc = 0
    maxLivDesc = 0
    totalDesc = 0
    totalLivDesc = 0

    for index, founder in founders.iterrows():
        # Calculate descendants count for each founder
        descendants_count = getDescCounts(df, founder['Ego'])

        # Calculate living descendants count for each founder
        living_descendants_count = getLivDescCounts(df, founder['Ego'])

        # Update maximum descendants count
        maxDesc = max(maxDesc, descendants_count)

        # Update maximum living descendants count
        maxLivDesc = max(maxLivDesc, living_descendants_count)

        # Update total descendants count
        totalDesc += descendants_count

        # Update total living descendants count
        totalLivDesc += living_descendants_count

    # Calculate average descendants and average living descendants
    avgDesc = round(totalDesc / len(founders), 3)
    avgLivDesc = round(totalLivDesc / len(founders), 3)

    # Add stats to the list
    stats.extend([maxDesc, maxLivDesc, avgDesc, avgLivDesc])

    return stats


# Recursive Function
# Takes in full DataFrame and an Ego
# Returns the number of descendents of Ego
def getDescCounts(df, ego):
    # Base case: if the founder has no descendants, return 0
    temp = df[(df['Father'] == (str)(ego)) | (df['Mother'] == (str)(ego))]
    if not df[(df['Father'] == (str)(ego)) | (df['Mother'] == (str)(ego))].empty:
        # Recursive case: count the direct descendants and recursively count descendants of each child
        descendants_count = 0
        children = pd.concat([df[df['Father'] == (str)(ego)], df[df['Mother'] == (str)(ego)]])
        for index, child in children.iterrows():
            descendants_count += 1  # Count the current child
            descendants_count += getDescCounts(df, child['Ego'])  # Recursively count descendants of the child
        return descendants_count
    else:
        return 0  # No descendants


# Recursive Function
# Takes in full DataFrame and an Ego
# Returns the number of living descendents of Ego
def getLivDescCounts(df, ego):
    # Base case: if the founder has no descendants, return 0
    if not df[((df['Father'] == (str)(ego)) | (df['Mother'] == (str)(ego))) & (df['Living'] == 'Y')].empty:
        # Recursive case: count the direct living descendants and recursively count living descendants of each child
        living_descendants_count = 0
        children = df[((df['Father'] == (str)(ego)) | (df['Mother'] == (str)(ego))) & (df['Living'] == 'Y')]
        for index, child in children.iterrows():
            living_descendants_count += 1  # Count the current living child
            living_descendants_count += getLivDescCounts(df, child['Ego'])  # Recursively count living descendants of the child
        return living_descendants_count
    else:
        return 0  # No living descendants