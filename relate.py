###############################################################################
# NAME: relate.py
# VERSION: 0.2.0.0 (21 MAY 2005)
# AUTHOR: Edward H. Hagen (e.hagen@biologie.hu-berlin.de)
# LICENSE: BSD
# Copyright (c) 2000-2005, Edward H. Hagen
###############################################################################

from __future__ import generators
import string, profile #, time
import wx
from random import *
#import Numeric
#from LinearAlgebra import eigenvectors
#from MLab import cov, mean, svd
#from orngMDS import *
#import pyp_metrics, pyp_nrm

class dataMatrix:
    def __init__(self, data, app):
        self.data = data
        self.app = app
        self.fieldDef = app.frame.notebook.Panel('Editor').GetFieldDef()
        self.missing = self.fieldDef['missing']
        self.makeDict()

    def makeDict(self):
        # {Ego : [father, mother, sex, living], ...}
        self.dict ={}
        for i in self.data:
            if i[self.fieldDef['father']].strip()=='': father=self.missing
            else: father=i[self.fieldDef['father']]
            if i[self.fieldDef['mother']].strip()=='': mother=self.missing
            else: mother=i[self.fieldDef['mother']]
            self.dict[i[self.fieldDef['ego']]]=[father,mother,i[self.fieldDef['sex']], i[self.fieldDef['living']]]

    def idMatrix(self, data):
        iMatrix={}
        for i in data.keys(): iMatrix[i]={}
        return iMatrix
        
class rMatrix(dataMatrix):
    def __init__(self, data, app):
        dataMatrix.__init__(self, data, app)
        self.powersof2 = [2**i for i in range(50)]
        self.inversePowersof2 = [1.0/(2**i) for i in range(50)]
        self.dim = 0 # For MDS
        self.app = app
        self.PyPedalPedigree = self.app.frame.notebook.Panel('Editor').pedigree
        
    def Tree(self, ego):
        "Compiles a tree of ancestors for ego."
        # bigTree = {ego:[[path1, path2, path3, ...], [link1, link2, link3, ...]], ...}, where path1 = path of ids to ancestor 1
        # and link1 = relationship links to ancestor 1 (e.g., FFM).
        missing = self.fieldDef['missing']
        # Initialize ancestor with ego
        ancestors = [[str(ego)]]
        links = ['']
        lastAncestors = ancestors[:] # make a copy
        lastLinks = links[:] # make a copy
        # Loop to find ancestors
        while 1:
            tempAncestors = []
            tempLinks = []
            allMissing = 1
            for j in range(len(lastAncestors)):
                ID = lastAncestors[j][-1]
                if self.dict.get(ID, [missing])[0] != missing: # Father
                    ancestors += [lastAncestors[j] + [self.dict[ID][0]]]
                    links += [lastLinks[j] + 'F']
                    tempAncestors += [lastAncestors[j] + [self.dict[ID][0]]]
                    tempLinks += [lastLinks[j] + 'F']
                    allMissing = 0
                if self.dict.get(ID, [1, missing])[1] != missing: # Mother
                    ancestors += [lastAncestors[j] + [self.dict[ID][1]]]
                    links += [lastLinks[j] + 'M']
                    tempAncestors += [lastAncestors[j] + [self.dict[ID][1]]]
                    tempLinks += [lastLinks[j] + 'M']
                    allMissing = 0
            lastAncestors = tempAncestors
            lastLinks = tempLinks
            if allMissing: break
        return [ancestors, links]
        
    def PathFinder(self, treeA, treeB):
        "Find all paths between two egos."
        pathsA = []; pathsB = [] # Paths terminating in a common ancestor will be stored here.
        LinksA = []; LinksB = [] # Formatted paths (e.g., FFMM) will be stored here.
        commonAncestors = []
        for i, a in enumerate(treeA[0]):
            for j, b in enumerate(treeB[0]):
                # Looking for common ancestors.  Must search starting with short paths
                if a[-1] == b[-1]: # a, b share a common ancestor,
                    if len(a) > 1 and len(b) > 1:
                        if a[-2] == b[-2]: continue # there was a shorter link along the same path
                    pathsA += [a]
                    pathsB += [b]
                    LinksA += [treeA[1][i]]
                    LinksB += [treeB[1][j]]
        for i in pathsA: commonAncestors += [i[-1]]
        return (pathsA, LinksA, pathsB, LinksB, commonAncestors)
    
    def AlterEgos(self, ego, kinOnly):
        "Find alter egos of ego; list relationship and relatedness.  Must call relatedness before calling AlterEgos."
        treeA = self.Tree(ego)
        alteregos =  self.dict.keys()
        alteregos.sort()
        kin = [['Alterego', 'Relatedness', 'Common ancestors (path)']]
        for alterego in alteregos:
            if ego == alterego: continue
            r = self.rMatrix(ego, alterego)
            if r != 0:
                treeB = self.Tree(alterego)
                pathsA, LinksA, pathsB, LinksB, commonAncestors = self.PathFinder(treeA, treeB)
                connections = ''
                for i, a in enumerate(commonAncestors):
                    connection = self.formatConnection([LinksA[i], LinksB[i]], a, alterego)
                    connections = connections + a + ' (' + connection + '), '
                kin.append([alterego, r, connections[:-2]]) # get rid of trailing ', '
            elif not kinOnly: kin.append([alterego, r, ''])
        if len(kin) == 1: kin += [['','','']] # Hack. Add an empty dummy row if there are no alteregos so table routines don't choke.
        return kin
        
    def formatConnection(self, connection, link, alterego):
        mapping = {'F':'S', 'M':'D'}
        kin = connection[0]
        for i in range(len(connection[1])-1): kin = kin + mapping[connection[1][-(i+2)]]
        if link != alterego:
            if self.dict[alterego][2] == self.fieldDef['male']: kin = kin + 'S' # Males are sons, females daughters
            else: kin = kin + 'D'
        return kin    

    def relatednessOLD(self):
        # Loop to calculate everyones r with everyone else
        #self.makeDict()
        ids=self.dict.keys()
        # ids.sort()
        length=len(ids)
        self.app.frame.ProgressBar(length) # Call back to GUI code to create progress bar
        self.progress=0
        self.rMatrix=self.idMatrix(self.dict) # matrix of relatedness coefficients
        self.kMatrix=self.idMatrix(self.dict) # matrix of kin ties
        self.ancestorTree()
        for a in range(length-1):
            treeA = self.bigTree[ids[a]][0]
            linksA = self.bigTree[ids[a]][1]
            for b in range(a+1, length):
                treeB = self.bigTree[ids[b]][0]
                linksB = self.bigTree[ids[b]][1]
                #if ids[a] == '088' and ids[b] == '086': debug = 1
                #else: debug = 0
                #if debug: print 'treeA and treeB: ', treeA, '\n\n', treeB
                pathsA = [] # paths terminating in a common ancestor will be stored here.
                pathsB = [] # ditto
                tempLinksA = []
                tempLinksB = []
                for i in range(len(treeA)):
                    for j in range(len(treeB)):
                        # Looking for common ancestors.  Must search starting with short paths
                        if treeA[i][-1] == treeB[j][-1]: # a, b share a common ancestor,
                            if len(treeA[i]) > 1 and len(treeB[j]) > 1:
                                if treeA[i][-2] == treeB[j][-2]: continue # there was a shorter link along the same path
                            pathsA += [treeA[i]]
                            pathsB += [treeB[j]]
                            tempLinksA += [linksA[i]]
                            tempLinksB += [linksB[j]]
                r=0
                for i in range(len(pathsA)):
                    r = r + self.inversePowersof2[len(pathsA[i]) + len(pathsB[i]) - 2] # Subtract 2, one for each ego
                self.rMatrix[ids[a]][ids[b]] = r
                self.rMatrix[ids[b]][ids[a]] = r
                
                commonAncestors = []
                for i in pathsA: commonAncestors += [i[-1]]
                # if debug:
                    # print 'pathsA and pathsB: ', pathsA, '\n', pathsB
                    # print 'commonAncestors: ', commonAncestors
                    # print 'tempLinksA, tempLinksB: ', tempLinksA, tempLinksB
                self.kMatrix[ids[a]][ids[b]] = [commonAncestors, tempLinksA, tempLinksB] 
                self.kMatrix[ids[b]][ids[a]] = [commonAncestors, tempLinksB, tempLinksA]
            self.app.frame.ProgressBar(a) # Call back to update progress bar
        self.app.frame.ProgressBar(-1) # Call back to delete progress bar

    def ancestorTree(self):
        # bigTree = {ego:[[path1, path2, path3, ...], [link1, link2, link3, ...]], ...}, where path1 = path of ids to ancestor 1
        # and link1 = relationship links to ancestor 1 (e.g., FFDS).
        missing = self.fieldDef['missing']
        self.bigTree = {}
        for i in self.dict.keys():
            # Initialize ancestor with ego
            ancestors = [[i]]
            links = ['']
            lastAncestors = ancestors[:] # make a copy
            lastLinks = links[:] # make a copy
            # Loop to find ancestors
            while 1:
                tempAncestors = []
                tempLinks = []
                allMissing = 1
                for j in range(len(lastAncestors)):
                    ID = lastAncestors[j][-1]
                    if self.dict.get(ID, [missing])[0] != missing:
                        ancestors += [lastAncestors[j] + [self.dict[ID][0]]]
                        links += [lastLinks[j] + 'F']
                        tempAncestors += [lastAncestors[j] + [self.dict[ID][0]]]
                        tempLinks += [lastLinks[j] + 'F']
                        allMissing = 0
                    if self.dict.get(ID, [1, missing])[1] != missing:
                        ancestors += [lastAncestors[j] + [self.dict[ID][1]]]
                        links += [lastLinks[j] + 'M']
                        tempAncestors += [lastAncestors[j] + [self.dict[ID][1]]]
                        tempLinks += [lastLinks[j] + 'M']
                        allMissing = 0
                lastAncestors = tempAncestors
                lastLinks = tempLinks
                if allMissing: break
            self.bigTree[i] = [ancestors, links]
    
    def findFounders(self, count):
        "Find population ancestors and their descendants."
        # Find founders
        founders = []
        missing = self.fieldDef['missing']
        for i in self.dict.keys():
            # If both parents are missing, ego is a founder
            if self.dict[i][0] == missing and self.dict[i][1] == missing: founders += [i]
            else:
                # If father/mother are not egos then they are founders
                if self.dict[i][0] not in self.dict.keys() and self.dict[i][0] not in founders and self.dict[i][0] != missing:
                    founders += [ self.dict[i][0] ]
                    # Add father to list of egos
                    self.dict[self.dict[i][0]] = [missing, missing, self.fieldDef['male'], missing]
                if self.dict[i][1] not in self.dict.keys() and self.dict[i][1] not in founders and self.dict[i][1] != missing:
                    founders += [ self.dict[i][1] ]
                    # Add mother to list of egos               
                    self.dict[self.dict[i][1]] = [missing, missing, self.fieldDef['female'], missing]
        
        # Find all descendants and living descendants of each founder
        descendants = {} # {ego: [descendant ID's], ...}
        living = {} # {ego: [living descendant ID's], ...}
        for f in founders:
            descendants[f] = self.findDescendants(f)
            living[f] = self.findLiving(descendants[f])
        
        ### PyPedal stuff, commented out for now ###
        #pedigree = self.app.frame.notebook.Panel('Editor').pedigree
        #_f_contribs, _f_contribs_weighted, _f_contribs_sum, _f_contribs_weighted_sum_sq, _f_e  = pyp_metrics.effective_founders_lacy(pedigree.pedigree)
        
        # Format table
        if count:
            #founderTable = [['Founder', 'Descendants', 'Living descendants', 'Founder contributions', 'Proportional contributions']]
            founderTable = [['Founder', 'Descendants', 'Living descendants']]
            for f in founders:
                #a = pedigree.dIndex[f] # PyPedal animal object that corresponds to f
                #pID = str(a.originalID) # PyPedal ID of that animal (Shouldn't be original ID, should it?)
                #founderTable += [[f, len(descendants[f]), len(living[f]), _f_contribs[pID], _f_contribs_weighted[pID]]]
                founderTable += [[f, len(descendants[f]), len(living[f])]]
        else:
            founderTable = [['Founder', 'Descendants', 'Living descendants']]
            for f in founders:
                temp1 = ''
                temp2 = ''
                for k in descendants[f]: temp1 = temp1 + ',' + k
                for k in living[f]: temp2 = temp2 + ',' + k
                founderTable += [[f, temp1[1:], temp2[1:]]]

        return founderTable
    
    def findDescendants(self, ego):
        "Find all descendants of egos."
        descendants = set([]) # There may be multiple paths to a descendant, but descendants are unique!
        temp = [ego]
        while 1:
            for d in temp:
                offspring = []
                # If ego is male, search father column, else search mother column
                if self.dict[d][2] == self.fieldDef['male']: col = 0
                else: col = 1
                for i in self.dict.keys():
                    if self.dict[i][col] == d: offspring += [i]
            if offspring == []: break
            descendants.update(offspring)
            temp = offspring
        return descendants
        
    def findLiving(self, egos):
        if self.fieldDef['allAlive']: return egos
        else:
            living = []
            for e in egos:
                if self.dict[e][3] == self.fieldDef['alive']: living += [e]
        return living
    
    def relatedness(self):
        "Compute relatedness matrix using PyPedal. Wrap matrix to interface with Descent."
        self.pedigree = self.app.frame.notebook.Panel('Editor').pedigree.pedigree.pedigree
        self.a, self.f_avg, self.fnz_avg, self.r_avg, self.rnz_avg = pyp_metrics.fast_a_coefficients(self.pedigree)
        
    def rMatrix(self, id1, id2):
        return self.a[self.PyPedalPedigree.rIndex[id1], self.PyPedalPedigree.rIndex[id2]]
    
    def FgALL(self):
        # Calculates FgALL and inbreeding coefficients using PyPedal
        table=[['Ego','FgALL', 'FgCON', '# of relatives', 'inbreeding']]
        pypedalfgall = {}
        pypedalfgcon = {}
        pypedalrelatives = {}
        pypedalinbreeding = {}
        n = len(self.pedigree)
        # Compute FgALL, FgCON, etc. via PyPedal matrix
        for row in range(n):
            r_pop_avg = 0.
            r_con_avg = 0.
            r_con_counter = 0
            for col in range(n):
                if row != col:
                    r_pop_avg = r_pop_avg + self.a[row,col]
                    if self.a[row,col] != 0:
                        r_con_avg += self.a[row,col]
                        r_con_counter += 1
            r_pop_avg = r_pop_avg / n
            if r_con_counter != 0: r_con_avg = r_con_avg / r_con_counter
            name = self.pedigree[row].name
            pypedalfgall[name] = r_pop_avg
            pypedalfgcon[name] = r_con_avg
            pypedalinbreeding[name] = self.a[row,row]-1
            pypedalrelatives[name] = r_con_counter
        theKeys=self.dict.keys()
        theKeys.sort()
        for i in theKeys: table.append([i, pypedalfgall[i], pypedalfgcon[i], pypedalrelatives[i], pypedalinbreeding[i]])
        return table
    
    def FgALL_OLD(self):
        # Calculates FgALL, FgCON, and inbreeding coefficient
        #average=[['Ego','FgALL', 'FgCON', '# relatives', 'inbreeding']]
        # This is all the PyPedal stuff, commented out for now.
        average=[['Ego','FgALL', 'FgCON', '# relatives', 'inbreeding', 'PP-FgALL', 'PP-FgCon', 'PP-Inbreeding']]        
        # First, let's compute relatedness and inbreeding using PyPedal
        pedigree = self.app.frame.notebook.Panel('Editor').pedigree
        a, f_avg, fnz_avg, r_avg, rnz_avg = pyp_metrics.fast_a_coefficients(pedigree.pedigree.pedigree, method="r")
        pypedalfgall = {}
        pypedalfgcon = {}
        pypedalinbreeding = {}
        n = len(pedigree.pedigree.pedigree)
        # Compute FgALL via PyPedal matrix
        for row in range(n):
            r_pop_avg = 0.
            r_con_avg = 0.
            r_con_counter = 0
            for col in range(n):
                if row != col:
                    r_pop_avg = r_pop_avg + a[row,col]
                    if a[row,col] != 0:
                        r_con_avg += a[row,col]
                        r_con_counter += 1
            r_pop_avg = r_pop_avg / n
            if r_con_counter != 0: r_con_avg = r_con_avg / r_con_counter
            pypedalfgall[pedigree.pedigree.pedigree[row].name] = r_pop_avg
            pypedalfgcon[pedigree.pedigree.pedigree[row].name] = r_con_avg
            pypedalinbreeding[pedigree.pedigree.pedigree[row].name] = a[row,row]-1
        # Compute FgALL via Descent (this will eventually be deleted).
        theKeys=self.rMatrix.keys()
        theKeys.sort()
        for i in theKeys:
            sumALL=0
            sizeALL=0
            sumCON=0
            sizeCON=0
            if self.fieldDef['allAlive'] or self.dict[i][3] == self.fieldDef['alive']: # this filters out dead people
                for j in self.rMatrix[i].keys():
                    if self.fieldDef['allAlive'] or self.dict[j][3] == self.fieldDef['alive']: # this also filters out dead people
                        sumALL=sumALL+self.rMatrix[i][j]
                        sizeALL+=1
                        if self.rMatrix[i][j] !=0:
                            sumCON=sumCON+self.rMatrix[i][j]
                            sizeCON+=1
            if sizeCON==0: FgCON=0
            else:FgCON=sumCON/sizeCON
            father=self.dict[i][0]
            mother=self.dict[i][1]
            if self.rMatrix.has_key(father) and self.rMatrix.has_key(mother):
                inbreedingCoeff=self.rMatrix[father][mother]/2
            else: inbreedingCoeff=0
            if sizeALL != 0: FgALL = sumALL/sizeALL
            else: FgALL = 0
            average.append([i, FgALL, FgCON, sizeCON, inbreedingCoeff, pypedalfgall[i], pypedalfgcon[i], pypedalinbreeding[i]])
            #average.append([i, FgALL, FgCON, sizeCON, inbreedingCoeff])
        return average

    def idMatrix2Array(self, d):
        # Helper function to convert the dictionary 'array' of relatedness values to a Numeric array
        self.IDS = d.keys(); self.IDS.sort()
        n = len(self.IDS)
        array = Numeric.identity(n, Numeric.Float)
        for i in range(n):
            for j in range(n):
                if i != j: array[i, j] = d[self.IDS[i]][self.IDS[j]]
        return array
        
    def PCA2(self):
        "Perform PCA on rMatrix, sort eigenvectors and eigenvalues"
        if hasattr(self, 'evals'): return # Don't re-compute PCA
        self.M = self.a #self.idMatrix2Array(self.rMatrix) # Convert dictionary 'array' of relatedness values to a Numeric array
        # Center the data, and negate for dissimilarities
        self.M = mean(self.M) - self.M
        # Compute eigenvectors of covariance matrix of M
        self.evals, self.evecs = eigenvectors(cov(self.M))
        self.evals = self.evals.astype(Numeric.Float) # make sure all eigenvalues are real (symmetric matrix, so should be)
        # sort the eigenvalues and eigenvectors, decending order
        order = (Numeric.argsort(self.evals)[::-1])
        self.evecs = Numeric.take(self.evecs, order, 1)
        self.evals = Numeric.take(self.evals, order)
    
    def PCAPlot2(self, dim):
        featureVector = Numeric.transpose(Numeric.take(self.evecs, range(dim), 1)).astype(Numeric.Float) # Take first 'dim' eigenvectors and transpose
        return Numeric.transpose(Numeric.matrixmultiply(featureVector, Numeric.transpose(self.M)))

    def PCA(self):
        if hasattr(self, 'evals'): return # Don't re-compute PCA
        self.M = self.a #self.idMatrix2Array(self.rMatrix)
        self.M = self.M - mean(self.M)
        self.u, self.evals, v = svd(self.M)
    
    def PCAPlot(self, dim):
        #print 'v: ', self.v[:,:dim]
        #print 'u: ', self.u[:,:dim]
        return matrixmultiply(transpose(self.M), self.u[:,:dim])
        
    def MDS(self, dim):
        if hasattr(self, 'mds') and self.dim==dim: return # Don't re-compute MDS for same dim
        self.dim = dim
        self.M = self.a #self.idMatrix2Array(self.rMatrix)
        self.mds = MDS(-self.M*self.M, dimensions=dim) # squared distances are apparently better
        self.stress1 = self.mds.getStress()
        self.mds.Torgerson()
        self.stress2 = self.mds.getStress()
        
class Groups(dataMatrix):
    def __init__(self, rMatrix, data, groupColumn, app):
        dataMatrix.__init__(self, data, app)
        self.fieldDef['group'] = groupColumn
        self.rMatrix = rMatrix
        self.makeGroupDict()
        
    def makeGroupDict(self):
        "Make a dictionary of lists keyed by group ID's.  Each list contains group members."
        groupColumn = self.fieldDef['group']
        egoColumn = self.fieldDef['ego']
        livingColumn = self.fieldDef['living']
        self.groupDict = {}
        if groupColumn == 0 or groupColumn == 1:
            # This is for Patrilineages (0) and Matrilineages (1)
            if groupColumn == 0: c = 1
            else: c = 4
            L = Lineages(self.data, self.app)
            lineages = L.computeLineages()
            for i in lineages[1:]: # chop off the header
                if (self.dict[i[0]][3] != self.fieldDef['alive']) and not self.fieldDef['allAlive']: continue # Don't include the dead
                if i[c] not in self.groupDict: self.groupDict[i[c]] = [i[0]]
                else: self.groupDict[i[c]].append(i[0])
        else:
            # Non-lineage groups
            groupColumn = groupColumn - 2  # Since had prepended Patri- and Matrilineages to list
            egos = self.dict.keys()
            for i in self.data:
                if (self.dict[i[egoColumn]][3] != self.fieldDef['alive']) and not self.fieldDef['allAlive']: continue # Don't include the dead
                groupID = i[groupColumn]
                if groupID == '': groupID = self.fieldDef['missing']
                if groupID not in self.groupDict: self.groupDict[groupID] = [i[egoColumn]]
                else: self.groupDict[groupID].append(i[egoColumn])
        
    def averageGroupRelatedness(self):
        "Within-group average relatedness."
        groupIDs = self.groupDict.keys()
        groupAvg = {}
        for i in groupIDs:
            rSum, count = 0, 0
            for j, k in xuniqueCombinations(self.groupDict[i], 2):
                rSum = rSum + self.rMatrix(j, k)
                count += 1
            if count != 0: groupAvg[i] = float(rSum)/count
            else: groupAvg[i] = 1
        return groupAvg
    
    def relatedness(self):
        "Average between-group relatedness."
        self.gMatrix = self.idMatrix(self.groupDict)
        groupIDs = self.groupDict.keys()
        groupIDs.sort()
        length = len(groupIDs)
        self.app.frame.ProgressBar(length) # Call back to GUI code to create progress bar
        for i in range(length - 1):
            groupA = self.groupDict[groupIDs[i]]
            for j in range(i+1, length):
                groupB = self.groupDict[groupIDs[j]]
                sum, count = 0, 0
                for m in groupA:
                    for n in groupB:
                        sum += self.rMatrix(m, n)
                        count += 1
                self.gMatrix[groupIDs[i]][groupIDs[j]] = float(sum)/count
                self.gMatrix[groupIDs[j]][groupIDs[i]] = float(sum)/count
            self.app.frame.ProgressBar(i) # Call back to update progress bar
        self.app.frame.ProgressBar(-1) # Call back to delete progress bar                
        
    def stats(self):
        groupStats = [['Group ID', 'Group size', 'Avg. relatedness']]
        g = self.averageGroupRelatedness()
        groupIDs = g.keys()
        groupIDs.sort()
        for i in groupIDs: groupStats.append([i, len(self.groupDict[i]), g[i]])
        return groupStats
    
class KinGroups(dataMatrix):
    def __init__(self, data, app):
        dataMatrix.__init__(self, data, app)
    
    def fathers(self, idList):
        # idList is a list of lists of ego id's
        fatherIDsList=[]
        for ids in idList:
            if type(ids) != type([]): ids=[ids]
            fatherIDs=[]
            for i in ids:
                if self.dict.has_key(i):
                    if self.dict[i][0] != self.fieldDef['missing'] and self.dict[i][0] not in fatherIDs:
                        fatherIDs.append(self.dict[i][0])
            fatherIDsList.append(fatherIDs)
        return fatherIDsList
    
    def mothers(self, idList):
        motherIDsList=[]
        for ids in idList:
            if type(ids) != type([]): ids=[ids]
            motherIDs=[]
            for i in ids:
                if self.dict.has_key(i):
                    if self.dict[i][1] != self.fieldDef['missing'] and self.dict[i][1] not in motherIDs:
                        motherIDs.append(self.dict[i][1])
            motherIDsList.append(motherIDs)
        return motherIDsList
        
    def parents(self, idList):
        return self.zipLists(self.fathers(idList), self.mothers(idList))
        
    def sons(self, idList):
        sonsIDsList=[]
        for ids in idList:
            if type(ids) != type([]): ids=[ids]
            sonIDs=[]
            IDkeys=self.dict.keys()
            for i in ids:
                for j in IDkeys:
                    # Because we might not know the sex of ids, check whether father or mother
                    if (self.dict[j][0]==i or self.dict[j][1]==i) and self.dict[j][2]==self.fieldDef['male']:
                        if j not in sonIDs: sonIDs.append(j)
            sonsIDsList.append(sonIDs)
        return sonsIDsList
    
    def daughters(self, idList):
        daughtersIDsList=[]
        for ids in idList:
            if type(ids) != type([]):ids=[ids]
            daugherIDs=[]
            IDkeys=self.dict.keys()
            for i in ids:
                for j in IDkeys:
                    # Because we might not know the sex of ids, check whether father or mother
                    if (self.dict[j][0]==i or self.dict[j][1]==i) and self.dict[j][2]==self.fieldDef['female']:
                        if j not in daugherIDs: daugherIDs.append(j)
            daughtersIDsList.append(daugherIDs)
        return daughtersIDsList

    def offspring(self, idList):
        return self.zipLists(self.sons(idList), self.daughters(idList))
        
    def grandparents(self, idList):
        pass
    
    def brothers(self, idList):
        brothersIDsList=[]
        for ids in idList:
            if type(ids) != type([]): ids=[ids]
            brotherIDs=[]
            IDkeys=self.dict.keys()
            for i in ids:
                if i not in IDkeys: continue
                fatherID=self.dict[i][0]
                motherID=self.dict[i][1]
                if fatherID != self.fieldDef['missing'] and motherID != self.fieldDef['missing']:
                    for j in IDkeys: 
                        if i==j: continue # don't add ego as own brother
                        if self.dict[j][0]==fatherID and self.dict[j][1]==motherID and self.dict[j][2]==self.fieldDef['male']:
                            if j not in brotherIDs: brotherIDs.append(j)
            brothersIDsList.append(brotherIDs)
        return brothersIDsList
            
    def sisters(self, idList):
        sistersIDsList=[]
        for ids in idList:
            if type(ids) != type([]):ids=[ids]
            sisterIDs=[]
            IDkeys=self.dict.keys()
            for i in ids:
                if i not in IDkeys:continue
                fatherID=self.dict[i][0]
                motherID=self.dict[i][1]
                if fatherID != self.fieldDef['missing'] and motherID != self.fieldDef['missing']:
                    for j in IDkeys:
                        if i==j: continue # don't add ego as own sister
                        if self.dict[j][0]==fatherID and self.dict[j][1]==motherID and self.dict[j][2]==self.fieldDef['female']:
                            if j not in sisterIDs:sisterIDs.append(j)
            sistersIDsList.append(sisterIDs)
        return sistersIDsList
        
    def siblings(self, idList):
        return self.zipLists(self.brothers(idList), self.sisters(idList))
        
    def halfbrothers(self, idList):
        halfbrothersIDsList=[]
        for ids in idList:
            if type(ids) != type([]):ids=[ids]
            brotherIDs=[]
            IDkeys=self.dict.keys()
            for i in ids:
                if i not in IDkeys:continue
                fatherID=self.dict[i][0]
                motherID=self.dict[i][1]
                for j in IDkeys:
                    if ((self.dict[j][0]==fatherID and fatherID != self.fieldDef['missing']) ^ (self.dict[j][1]==motherID and motherID != self.fieldDef['missing'])) and self.dict[j][2]==self.fieldDef['male']:
                        if j not in brotherIDs: brotherIDs.append(j)
            halfbrothersIDsList.append(brotherIDs)
        return halfbrothersIDsList
    
    def halfsisters(self, idList):
        halfsistersIDsList=[]
        for ids in idList:
            if type(ids) != type([]):ids=[ids]
            sisterIDs=[]
            IDkeys=self.dict.keys()
            for i in ids:
                if i not in IDkeys:continue
                fatherID=self.dict[i][0]
                motherID=self.dict[i][1]
                for j in IDkeys:
                    if ((self.dict[j][0]==fatherID and fatherID != self.fieldDef['missing']) ^ (self.dict[j][1]==motherID and motherID != self.fieldDef['missing'])) and self.dict[j][2]==self.fieldDef['female']:
                        if j not in sisterIDs: sisterIDs.append(j)
            halfsistersIDsList.append(sisterIDs)
        return halfsistersIDsList
        
    def halfsiblings(self, idList):
        return self.zipLists(self.halfbrothers(idList), self.halfsisters(idList))
        
    def cousins(self, idList):
        cousins = self.offspring(self.siblings(self.parents(idList)))
        # If there is sibling incest, ego can be own cousin; filter out egos from cousins in this case
        for i in range(len(idList)):
            ids = idList[i]
            if type(ids) != type([]): ids=[ids]
            for j in cousins[i][:]:
                if j in ids: cousins[i].remove(j)
        return cousins
    
    def mates(self, idList):
        matesIDsList=[]
        for ids in idList:
            if type(ids) != type([]):ids=[ids]
            mates=[]
            IDkeys=self.dict.keys()
            for i in ids:
                for j in IDkeys:
                    if self.dict[j][0]==i and self.dict[j][1] not in mates and self.dict[j][1] != self.fieldDef['missing']:
                        mates.append(self.dict[j][1])
                    elif self.dict[j][1]==i and self.dict[j][0] not in mates and self.dict[j][0] != self.fieldDef['missing']:
                        mates.append(self.dict[j][0])
            matesIDsList.append(mates)
        return matesIDsList

    def stepsons(self, idList):
        # This could be done more efficiently, but what the hell.
        matesSons = self.sons(self.mates(idList))
        mySons = self.sons(idList)
        stepsonsIDsList = []
        for i in idList: stepsonsIDsList.append([])
        for i in range(len(matesSons)):
            for j in matesSons[i]:
                if j not in mySons[i] and j not in stepsonsIDsList[i]: stepsonsIDsList[i].append(j)
        return stepsonsIDsList

    def stepdaughters(self, idList):
        matesDaughters = self.daughters(self.mates(idList))
        myDaughters = self.daughters(idList)
        stepdaughtersIDsList = []
        for i in idList: stepdaughtersIDsList.append([])
        for i in range(len(matesDaughters)):
            for j in matesDaughters[i]:
                if j not in myDaughters[i] and j not in stepdaughtersIDsList[i]: stepdaughtersIDsList[i].append(j)
        return stepdaughtersIDsList
        
    def stepchildren(self, idList):
        return self.zipLists(self.stepsons(idList), self.stepdaughters(idList))
        
    def stepbrothers(self, idList):
        allBrothers = self.sons(self.mates(self.parents(idList)))
        bloodBrothers = self.brothers(idList)
        halfbrothers = self.halfbrothers(idList)
        stepbrothersIDsList = []
        for i in idList: stepbrothersIDsList.append([])
        for i in range(len(allBrothers)):
            for j in allBrothers[i]:
                if j == idList[i]: continue # Don't add self to stepbrothers 
                if j not in bloodBrothers[i] and j not in halfbrothers[i] and j not in stepbrothersIDsList[i]: stepbrothersIDsList[i].append(j)
        return stepbrothersIDsList

    def stepsisters(self, idList):
        allSisters = self.daughters(self.mates(self.parents(idList)))
        bloodSisters = self.sisters(idList)
        halfsisters = self.halfsisters(idList)
        stepsistersIDsList = []
        for i in idList: stepsistersIDsList.append([])
        for i in range(len(allSisters)):
            for j in allSisters[i]:
                if j == idList[i]: continue # Don't add self to stepsisters
                if j not in bloodSisters[i] and j not in halfsisters[i] and j not in stepsistersIDsList[i]: stepsistersIDsList[i].append(j)
        return stepsistersIDsList
        
    def stepsiblings(self, idList):
        return self.zipLists(self.stepbrothers(idList), self.stepsisters(idList))
    
    def zipLists(self, list1, list2):
        zippedLists = []
        for i in range(len(list1)):zippedLists.append(list1[i]+list2[i])
        return zippedLists
        
    def kinFunctionMap(self, fnc, idList):
        if   fnc=='fathers': return self.fathers(idList)
        elif fnc=='mothers': return self.mothers(idList)
        elif fnc=='parents': return self.parents(idList)
        elif fnc=='sons': return self.sons(idList)
        elif fnc=='daughters': return self.daughters(idList)
        elif fnc=='offspring': return self.offspring(idList)
        elif fnc=='grandparents': return self.parents(self.parents(idList))
        elif fnc=='grandchildren': return self.offspring(self.offspring(idList))
        elif fnc=='full brothers': return self.brothers(idList)
        elif fnc=='full sisters': return self.sisters(idList)
        elif fnc=='full siblings': return self.siblings(idList)
        elif fnc=='halfbrothers': return self.halfbrothers(idList)
        elif fnc=='halfsisters': return self.halfsisters(idList)
        elif fnc=='halfsiblings': return self.halfsiblings(idList)
        elif fnc=='full cousins': return self.cousins(idList)
        elif fnc=='mates': return self.mates(idList)
        elif fnc=='stepsons': return self.stepsons(idList)
        elif fnc=='stepdaughters': return self.stepdaughters(idList)
        elif fnc=='stepchildren': return self.stepchildren(idList)
        elif fnc=='stepbrothers': return self.stepbrothers(idList)
        elif fnc=='stepsisters': return self.stepsisters(idList)
        elif fnc=='stepsiblings': return self.stepsiblings(idList)
        else: return []

    def kinFunctionExec(self, functionList, idList):
        kinLists=[]
        for fList in functionList:
            if fList==[] or fList==['']: continue
            kin=idList
            for fnc in fList: kin=self.kinFunctionMap(fnc, kin)
            kinLists.append(kin)
        return kinLists

    def kinCount(self, count, functionList, allAlive = False):
        idList = self.dict.keys()
        idList.sort()
        #self.errors=`functionList`
        matrix=[['ego']]
        for i in functionList: # Create column names
            temp1, temp2 = 'Count ', ''
            for j in i:
                temp1=temp1+j+':'; temp2=temp2+j+':'
            matrix[0].append(temp1[:-1]) # Get rid of trailing ':'
            matrix[0].append(temp2[:-1]) # Get rid of trailing ':'
        matrix[0].append('Sum') # Add Sum column to the end
        matrix[0].append('All') # Add All column to the end
        kinGroups=self.kinFunctionExec(functionList, idList)
        
        # Filter out the dead
        if not self.fieldDef['allAlive'] and not allAlive:
            for j in kinGroups:
                for i in j:   
                    for k in i[:]: # Makes temp copy of i so we can delete stuff from the real i
                        if self.dict.has_key(k):
                            if self.dict[k][3] == self.fieldDef['dead']: i.remove(k)

        # Filter out parents who don't appear as egos
        if 1: # Leave if_statement here in case we want to make this an option
            for j in kinGroups:
                for i in j:
                    for k in i[:]: # Makes temp copy of i so we can delete stuff from the real i
                        # if k not an ego
                        if not self.dict.has_key(k): i.remove(k)
                            
        for i in range(len(idList)):
            matrix.append([idList[i]])
            sum = []
            for j in range(len(kinGroups)):
                sum = sum + kinGroups[j][i]
                matrix[i+1].append(len(kinGroups[j][i]))
                # Format kinGroups[j][i] into comma-delimited list
                temp = ''
                for k in kinGroups[j][i]: temp = temp + ',' + k
                matrix[i+1].append(temp[1:])
            # Make sure sum contains only unique entries
            unique=[]; [unique.append(x) for x in sum if not unique.count(x)]
            matrix[i+1].append(len(unique))
            # Format sum into comma-delimited list
            temp = ''
            for k in unique: temp = temp + ',' + k
            matrix[i+1].append(temp[1:])
        return matrix

class Lineages(dataMatrix):
    def __init__(self, data, app):
        dataMatrix.__init__(self, data, app)
    
    def computeLineages(self):
        table = [['Ego', 'Patrilineage', 'Patriarch', 'Pat. size', 'Matrilineage', 'Matriarch', 'Mat. size']]
        ids = self.dict.keys()
        patriLineageSize, egoPatrilineage, self.patStats = self.lineageFounders(ids, 'patrilineage')
        matriLineageSize, egoMatrilineage, self.matStats = self.lineageFounders(ids, 'matrilineage')
        keys = egoPatrilineage.keys()
        keys.sort()
        for i in keys:
            table.append([i, egoPatrilineage[i], patriLineageSize[egoPatrilineage[i]][1], patriLineageSize[egoPatrilineage[i]][0], egoMatrilineage[i], matriLineageSize[egoMatrilineage[i]][1], matriLineageSize[egoMatrilineage[i]][0]])
        return table
        
    def lineageFounders(self, ids, lineageType):
        # Compute Patri- or Matrilineages
        if lineageType == 'patrilineage': code, sex = 0, 'male'
        else: code, sex = 1, 'female'        
        lineages = {self.missing:[0, ' ']} # {lineage_founder: [lineage_size, patriarch]}; initialize with missing
        egoLineage = {} # {Ego: lineage_founder}
        for i in ids:
            ego, parentID = i, self.dict[i][code]
            patriarch = ' '
            while parentID != self.missing:
                # this loop finds the most distant lineal ancestor;
                # it also finds the 'patriarch', the most distant living lineal ancestor
                ego = parentID
                if self.dict.get(ego, [0,0,0,self.fieldDef['dead']])[3] == self.fieldDef['alive']: patriarch = ego
                parentID = self.dict.get(ego, [self.missing, self.missing])[code]
            if self.fieldDef['allAlive']: patriarch = ego
            if ego not in lineages:
                if ego == i: # If ego has a missing parent
                    if self.dict[ego][2] == self.fieldDef[sex]:
                        # if ego is same sex as missing parent, then ego is lineage founder
                        if (self.dict[ego][3] == self.fieldDef['alive']) or (self.fieldDef['allAlive']): patriarch = ego
                        lineages[ego] = [0, patriarch] # set ego as lineage founder; we will increment to 1 later if i is living
                    else: ego = self.missing # set lineage founder for i to missing
                else: lineages[ego] = [0, patriarch] # set ego as lineage founder; we will increment to 1 later if i is living                  
            if self.dict.get(i, [0,0,0,self.fieldDef['dead']])[3] == self.fieldDef['alive'] or self.fieldDef['allAlive']:
                lineages[ego][0] += 1
            egoLineage[i] = ego
        return lineages, egoLineage, self.lineageStats(lineages, lineageType)

    def lineageStats(self, lineages, lineageType):
        # make new list of lineages omitting lineages with zero living members and those not belonging to any lineage
        lin = [lineages[x][0] for x in lineages if (lineages[x][0] != 0) and x != self.missing]
        stats = {}
        stats['keyOrder'] = ['No. of '+ lineageType +'s', 'Smallest '+ lineageType, 'Largest '+ lineageType, 'Mean ' + lineageType + ' size', 'No. not belonging to any ' + lineageType]
        #stats['No. not belonging to any ' + lineageType] = `lineages[self.missing][0]`
        #for i in lineages:
            #if lineages[i][0] == 0: del lin[i] # get rid of lineages with 0 living members
        #if self.missing in lin: del lin[self.missing] # Don't want to include number of missing in the stats
        #stats['No. of '+ lineageType +'s'] = `len(lin)`
        #stats['Smallest '+ lineageType] = `min(lin)`
        #stats['Largest '+ lineageType] = `max(lin)`
        sum = 0
        for i in lin: sum += i
        stats['Mean ' + lineageType + ' size'] = '%-5d' % round(float(sum)/len(lin))
        return stats
        
def xuniqueCombinations(items, n):
    # This code from Python Cookbook recipes: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/190465
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in xuniqueCombinations(items[i+1:],n-1):
                yield [items[i]]+cc
                
                
                
                
