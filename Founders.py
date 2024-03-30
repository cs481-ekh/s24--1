import pandas as pd # Excellent Documentation: https://pandas.pydata.org/docs/reference/frame.html
import numpy as np


# Takes in complete dataframe
# Returns dataframe of Founders (Ego, Father, Mother, Sex, Living)
def findFounders(df):
    # TODO: Incorrect Logic
    # Creates Missing Parents (They become Founders)
    egos = set(df['Ego'])
    fathers = set(df['Father'].dropna().astype(int))
    mothers = set(df['Mother'].dropna().astype(int))

    # Finds unlinked parents
    unlinkedFathers = egos - fathers
    unlinkedMothers = egos - mothers

    # Creates New Entries for each missing parent
    newFounders = []
    for f in unlinkedFathers:
        newFounders.append({'Ego': f, 'Father': None, 'Mother': None, 'Sex': 'M', 'Living': None})
    for m in unlinkedMothers:
        newFounders.append({'Ego': m, 'Father': None, 'Mother': None, 'Sex': 'F', 'Living': None})
    
    # Adds the new entries to DataFrame
    addedFounders = pd.DataFrame(newFounders)
    df = pd.concat([df, addedFounders], ignore_index=True)

    # Gets Founders
    return df[(df['Mother'] == None) & (df['Father'] == None)]


# Takes in complete dataframe and Founders DataFrame
# Returns list of statistics (5 elements)
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
    avgDesc = totalDesc / len(founders)
    avgLivDesc = totalLivDesc / len(founders)

    # Add stats to the list
    stats.extend([maxDesc, maxLivDesc, avgDesc, avgLivDesc])

    return stats


# Recursive Function
# Takes in full DataFrame and an Ego
# Returns the number of descendents of Ego
def getDescCounts(df, ego):
    # Base case: if the founder has no descendants, return 0
    if not df[(df['Father'] == ego) | (df['Mother'] == ego)].empty:
        # Recursive case: count the direct descendants and recursively count descendants of each child
        descendants_count = 0
        children = df[df['Father'] == ego].append(df[df['Mother'] == ego])
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
    if not df[((df['Father'] == ego) | (df['Mother'] == ego)) & (df['Living'] == 'Y')].empty:
        # Recursive case: count the direct living descendants and recursively count living descendants of each child
        living_descendants_count = 0
        children = df[((df['Father'] == ego) | (df['Mother'] == ego)) & (df['Living'] == 'Y')]
        for index, child in children.iterrows():
            living_descendants_count += 1  # Count the current living child
            living_descendants_count += getLivDescCounts(df, child['Ego'])  # Recursively count living descendants of the child
        return living_descendants_count
    else:
        return 0  # No living descendants