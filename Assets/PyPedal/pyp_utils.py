#####
#NOTES: PETER BUSCHE
    # 1) got pyp_classes and pyp_demog working
        # this caused alot of errors to go away


###



# FUNCTIONS:
#   load_pedigree()
#   preprocess()
#   new_preprocess()
#   set_ancestor_flag()
#   set_generation()
#   set_age()
#   set_species()
#   assign_sexes()
#   assign_offspring()
#   reorder()
#   fast_reorder()
#   renumber()
#   load_id_map()
#   delete_id_map()
#   id_map_new_to_old()
#   trim_pedigree_to_year()
#   pedigree_range()
#   sort_dict_by_keys()
#   simple_histogram_dictionary()
#   reverse_string()
#   pyp_nice_time()


##
# pyp_utils contains a set of procedures for creating and operating on PyPedal pedigrees.
# This includes routines for reordering and renumbering pedigrees, as well as for modifying
# pedigrees.
##

from numpy import *
import os
from Assets.PyPedal import pyp_classes
from Assets.PyPedal import pyp_demog
from Assets.PyPedal import pyp_metrics
from Assets.PyPedal import pyp_newclasses
from Assets.PyPedal import pyp_newclasses
import string
import sys
from time import *

##
# load_pedigree() wraps several processes useful for loading and preparing a pedigree for use in an
# analysis, including reading the animals into a list of animal objects, forming lists of sires and dams,
# checking for common errors, setting ancestor flags, and renumbering the pedigree.
# @param inputfile Name of the file from which the pedigree is to be read.
# @param filetag A descriptor prepended to output file names.
# @param sepchar Indicates which character is used to separate entries in the pedigree file (default is CSV).
# @param debug Flag to indicate whether or not progress messages are written to stdout.
# @param io Indicates whether or not to write an ancestor list to a file..
# @param renum Flag to indicate whether or not the pedigree is to be renumbered.
# @param outformat Flag to indicate whether or not to write an asd pedigree (0) or a full pedigree (1).
# @param name The name of the pedigree (descriptive).
# @param alleles Flag to indicate whether or not pyp_metrics/effective_founder_genomes() should be called for a single round to assign alleles.
# @param progress Flag to indicate whether or not to print progress messages to STDOUT when loading very large pedigrees.
# @return A list of Animal() objects; a pedigree metadata object.
# @defreturn lists
def load_pedigree(inputfile,filetag='_load_pedigree_',sepchar=',',debug=0,io='no',renum=1,outformat='0',name='Pedigree Metadata',alleles=0,progress=0):
    myped = preprocess(inputfile,sepchar=sepchar,debug=debug,progress=progress)
    if renum:
        if debug:
            print(('-'*80))
            print(('\tCalling fast_reorder() at %s' % asctime(localtime(time()))))
        myped = fast_reorder(myped,filetag=filetag,io=io,debug=debug)
        if debug:
            print(('-'*80))
            print(('\tCalling renumber() at %s' % asctime(localtime(time()))))
        myped = renumber(myped,filetag=filetag,io=io,outformat=outformat,debug=debug)
    if debug:
        print(('-'*80))
        print(('\tCalling set_generation() at %s' % asctime(localtime(time()))))
    set_generation(myped)
    if debug:
        print(('-'*80))
        print(('\tCalling set_ancestor() at %s' % asctime(localtime(time()))))
    set_ancestor_flag(myped,filetag=filetag,io=io,debug=debug)
    if debug:
        print(('-'*80))
        print(('\tCalling assign_sexes() at %s' % asctime(localtime(time()))))
    assign_sexes(myped,debug)
    if alleles:
        if debug:
            print(('-'*80))
            print(('\tCalling pyp_metrics.effective_founder_genomes() at %s' % asctime(localtime(time()))))
        pyp_metrics.effective_founder_genomes(myped,filetag=filetag,rounds=1,verbose=0,quiet=1)
    if debug:
        print(('-'*80))
        print(('\tCalling pyp_classes/Pedigree() at %s' % asctime(localtime(time()))))
    mymeta = Pedigree(myped,inputfile,name=name,debug=debug)
    return myped,mymeta

##
# preprocess() processes a pedigree file, which includes reading the animals into a list of animal
# objects, forming lists of sires and dams, and checking for common errors.
# @param inputfile Name of the file from which the pedigree is to be read.
# @param sepchar Indicates which character is used to separate entries in the pedigree file (default is CSV).
# @param debug Flag to indicate whether or not progress messages are written to stdout.
# @param progress Flag to indicate whether or not to print progress messages to STDOUT when loading very large pedigrees.
# @return A list of Animal() objects; this is what PyPedal calls a pedigree.
# @defreturn list
def preprocess(inputfile,sepchar=',',debug=0,progress=0):
    """Preprocess a pedigree file, which includes reading the animals into a list, forming lists of sires and dams, and checking for common errors."""
    #from pyp_classes import *
    lineCounter = 0     # count the number of lines in the pedigree file
    animalCounter = 0   # count the number of animal records in the pedigree file
    animals= []     # holds a list of Animal() objects
    _animals = {}
    males = {}      # holds a list of male IDs in the pedigree
    females = {}        # holds a list of female IDs in the pedigree
    unknowns = {}       # holds a list of animals of unknown sex
    pedformat = ''      # stores the pedigree format string
    infile=open(inputfile,'r')
    while 1:
        line = infile.readline()
        if not line:
            break
        else:
            if debug > 1:
                print(line)
            line = string.strip(line[:-1])
            lineCounter = lineCounter + 1
            if line[0] == '#':
                pass
            elif line[0] == '%':
                pedformat = string.strip(line[1:]) # this lets us specify the format of the pedigree file
                if debug:
                    print(('[DEBUG]: Pedigree format: %s' % (pedformat)))
                pass
            else:
                if debug == 1:
                    if animalCounter == 0:
                        print('[DEBUG]: Reading animal records from pedigree file...')
                        if fmod(animalCounter,10000) == 0:
                            print(('\t%s ' % (animalCounter)))
                animalCounter = animalCounter + 1
                l = string.split(line,sepchar)
                # Some people *cough* Brad Heins *cough* insist on sending me pedigree
                # files vomited out by Excel, which pads cells in a column with spaces
                # to right-align them...
                for i in range(len(l)):
                    l[i] = string.strip(l[i])
                if len(l) < 3:
                    errorString = 'The record on line %s of file %s is too short - all records must contain animal, sire, and dam ID numbers (%s fields detected).\n' % (lineCounter,inputfile,len(l))
                    print(('[ERROR]: %s' % (errorString)))
                    break
                # now we have to deal with different pedigree data formats...
                ###
                ### 07/20/2004
                ### Thoughts on fixing this mess
                ### ----------------------------
                ### 01. Define a set of single-digit codes to variable types:
                ### 01a. a = animal
                ### 01b. s = sire
                ### 01c. d = dam
                ### 01d. g = generation
                ### 01e. x = sex
                ### 01f. b = birth year in YYYY format (?)
                ### 01g. f = inbreeding
                ### 01h. t = alleles (NOTE: occupies two adjacent columns)
                ### 01i. r = breed
                ### 01j. n = name
                ### 01k. y = birthyear in MM/DD/YYYY format (?)
                ### 01l. l = alive (1) or dead (0)
                ### o1m. e = age
                ### 02. Read the format string
                ### 03. Use len() to find the number of codes in the format string
                ### 04. Check for duplicate codes -- throw error if necessary
                ### 05. Populate a dictionary to map codes to columns
                ### 06. Process datalines:
                ### 06a.    Split the line based on the sepchar
                ### 06b.    Map the data in the split dataline to the proper
                ###     Animal() object __init__ keywords based using the
                ###     dictionary from step 05.  This does imply that ALL
                ###     arguments to the __init__() method must be keyword
                ###     arguments.  That is not a big deal, but it will
                ###     require some tweakage of the code to avoid breakage.
                ### This method is a little more complicated than the current method
                ### but it is much less clumsy and is more easily extensible.  Looking
                ### at the 'b' and 'y' codes, it appears that I may have to think care-
                ### fully about handling dates, which is always a can of worms.
                ###
                if pedformat == '':
                    pedformat = 'asd'
                    if debug:
                        print('[DEBUG]: Null pedigree format string assigned a default value in pyp_utils/preprocess().')
                if pedformat == 'asd':
                    an = Animal(l[0],l[1],l[2])
                elif pedformat == 'asdg':
                    an = Animal(l[0],l[1],l[2],gen=l[3])
                elif pedformat == 'asdx':
                    an = Animal(l[0],l[1],l[2],l[3])
                elif pedformat == 'asdb':
                    an = Animal(l[0],l[1],l[2],by=l[3])
                elif pedformat == 'asdf':
                    an = Animal(l[0],l[1],l[2],fa=l[3])
                elif pedformat == 'asdt':
                    an = Animal(l[0],l[1],l[2],alleles=[l[3],l[4]])
                elif pedformat == 'asdxb':
                    an = Animal(l[0],l[1],l[2],sex=l[3],by=l[4])
                elif pedformat == 'asdgb':
                    an = Animal(l[0],l[1],l[2],gen=l[3],by=l[4])
                elif pedformat == 'asdbx':
                    an = Animal(l[0],l[1],l[2],sex=l[4],by=l[3])
                elif pedformat == 'asdxf':
                    an = Animal(l[0],l[1],l[2],sex=l[3],fa=l[4])
                elif pedformat == 'asdbf':
                    an = Animal(l[0],l[1],l[2],by=l[3],fa=l[4])
                elif pedformat == 'asdxbf':
                    an = Animal(l[0],l[1],l[2],sex=l[3],by=l[4],fa=l[5])
                elif pedformat == 'asdyxfg':
                    # This is the format that I have put the TSEI pedigrees into for preprocessing.
                    if len(l[3]) > 0:
                        splityear = l[3].split('/')
                        birthyear = splityear[2]
                    else:
                        birthyear = '1950'
                    an = Animal(l[0],l[1],l[2],by=birthyear,sex=l[4],fa=l[5],gen=l[6])
                    #print 'DEBUG: %s' % (line)
                    #an.printme()
                elif pedformat == 'asdbxfg':
                    # This is the format that PyPedal puts TSEI pedigrees into for analysis.
                    an = Animal(l[0],l[1],l[2],by=l[3],sex=l[4],fa=l[5],gen=l[6])
                else:
                    errorString = 'Pedigree file %s has an invalid format code (%s) on line %s.\n' % (inputfile,pedformat,lineCounter)  #PETERBUSCHE
                    # errorString = 'Pedigree file %s has an invalid format code (%s) on line %s.\n' % (inputfile,pedformat,counter) 
                    print(('[ERROR]: %s' % (errorString)))

                # NOTE: we have an odd situation where animals may appear in both unknown and known
                # [sex] lists b/c the sex of sires and dams is inferred from their location in the
                # animal record.  Base animals without sex codes are assigned a sex of 'u' (unknown)
                # by default if no code is included in the pedigree file.  When those parents appear
                # later as parents, they will be placed in the appropriate list.  The program does
                # remove animals from the UNKNOWN list once they are placed in a sex-specific list.
                #
                # There is a problem with the current implementation here.  An "if animal in list"
                # statement is used, which is fine for small pedigrees.  It degrades very badly for
                # large pedigrees.  Hm...maybe a dictionary?  Dictionaries are insanely faster.  The
                # right tool...
                #
                # Do not insert duplicate males into the MALES list
                try:
                    _i =  males[an.sireID]
                except KeyError:
                    if int(an.sireID) != 0:
                        males[an.sireID] = int(an.sireID)
                # Do not insert duplicate females into the FEMALES list
                try:
                    _i =  females[an.damID]
                except KeyError:
                    if int(an.damID) != 0:
                        females[an.damID] = int(an.damID)
                # Check the sex code to see in which list an animal should be placed
                # 'M' or 'm' codes for males
                if an.sex == 'M' or an.sex == 'm':
                    try:
                        _i =  males[an.animalID]
                    except KeyError:
                        if int(an.animalID) != 0:
                            males[an.animalID] = int(an.animalID)
                # 'F' or 'f' codes for females
                elif an.sex == 'F' or an.sex == 'f':
                    try:
                        _i =  females[an.animalID]
                    except KeyError:
                        if int(an.animalID) != 0:
                            females[an.animalID] = int(an.animalID)
                # Any other character is treated as unknown
                else:
                    if int(an.animalID) != 0:
                        unknowns[an.animalID] = int(an.animalID)
                # Make sure that sires are not also coded as dams
                try:
                    _i = females[an.sireID]
                    if _i != 0 and _i != '0':
                        print(('[ERROR]: Animal %s is coded as a sire (male) for some animal records, but as a dam (female) for other animal records (check record %s - animal ID %s)' % (an.sireID,animalCounter,an.animalID)))
                        break
                except:
                    pass
                # Make sure that dams are not also coded as sires
                try:
                    _i = males[an.damID]
                    if _i != 0 and _i != '0':
                        print(('[ERROR]: Animal %s is coded as a dam (female) for some animal records, but as a sire (male) for other animal records (check record %s - animal ID %s)' % (an.damID,animalCounter,an.animalID)))
                        break
                except:
                    pass

                # Infers the sex of an animal with unknown gender based on whether or not they later appear as a sire
                # or a dam in the pedigree file.
                try:
                    if debug:
                        print(('\tTrying to delete a male (%s) from the unknowns list...' % (unknowns[an.sireID])))
                    _i = unknowns[an.sireID]
                    del unknowns[an.sireID]
                except KeyError:
                    pass
                try:
                    if debug:
                        print(('\tTrying to delete a female (%s) from the unknowns list...' % (unknowns[an.damID])))
                    _i = unknowns[an.damID]
                    del unknowns[an.damID]
                except KeyError:
                    pass

                # Suppose that base animals are not given an individual entry in the
                # pedigree file...it is necessary to catch that case and add an animal
                # object to the list for them.
                # First for sires...
                try:
                    _i = _animals[an.sireID]
                except KeyError:
                    if int(an.sireID) != 0:
                        _an = Animal(an.sireID,'0','0')
                        _animals[an.sireID] = an.sireID
                        animals.append(_an)
                # ...and then for dams
                try:
                    _i = _animals[an.damID]
                except KeyError:
                    if int(an.damID) != 0:
                        _an = Animal(an.damID,'0','0')
                        _animals[an.damID] = an.damID
                        animals.append(_an)

                animals.append(an)
                _animals[an.animalID] = an.animalID

    if debug:
        print(('[DEBUG]: males ', males))
        print(('[DEBUG]: females ', females))
        print(('[DEBUG]: unknowns ', unknowns))
        print(('='*80))
                
    # Make sure that known males have the proper sex code in their instance
    for _m in males:
        try:
            if debug:
                print(('[DEBUG]: MALE %s has SIRE %s and DAM %s' % (animals[int(_m) - 1].animalID,animals[int(_m) - 1].sireID,animals[int(_m) - 1].damID)))
            if animals[int(_m)].sex == 'u':
                animals[int(_m)].sex = 'm'
            # Add the animal's ID to the sire and dam's daughter lists
            if int(animals[int(_m) - 1].sireID) != 0 and int(animals[int(_m) - 1].animalID) != 0:
                try:
                    _md = animals[int(animals[int(_m) - 1].sireID) - 1].sons[_m]
                except KeyError:
                    if debug:
                        print(('\t%s is a SON of SIRE %s' % (animals[int(_m) - 1].animalID,animals[int(_m) - 1].sireID)))
                        print(('\tAdding animal %s to sire %s\'s sons list.' % (_m,animals[int(_m) - 1].sireID)))
                    animals[int(animals[int(_m) - 1].sireID) - 1].sons[_m] = int(_m)
            if int(animals[int(_m) - 1].damID) != 0 and int(animals[int(_m) - 1].animalID) != 0:
                try:
                    _md = animals[int(animals[int(_m) - 1].damID) - 1].sons[_m]
                except KeyError:
                    if debug:
                        print(('\t%s is a SON of DAM %s' % (animals[int(_m) - 1].animalID,animals[int(_m) - 1].damID)))
                        print(('\tAdding animal %s to dam %s\'s sons list.' % (_m,animals[int(_m) - 1].damID)))
                    animals[int(animals[int(_m) - 1].damID) - 1].sons[_m] = int(_m)
        except:
            pass
    # Make sure that known females have the proper sex code in their instance
    for _f in females:
        try:
            if debug:
                print(('[DEBUG]: FEMALE %s has SIRE %s and DAM %s' % (animals[int(_f) - 1].animalID,animals[int(_f) - 1].sireID,animals[int(_f) - 1].damID)))
            if animals[int(_f)].sex == 'u':
                animals[int(_f)].sex = 'f'
            # Add the animal's ID to the sire and dam's daughter lists
            if int(animals[int(_f) - 1].sireID) != 0 and int(animals[int(_f) - 1].animalID) != 0:
                try:
                    _fd = animals[int(animals[int(_f) - 1].sireID) - 1].daus[_f]
                except KeyError:
                    if debug:
                        print(('\t%s is a DAUGHTER of SIRE %s' % (animals[int(_f) - 1].animalID,animals[int(_f) - 1].sireID)))
                        print(('\tAdding animal %s to sire %s\'s daus list.' % (_f,animals[int(_f) - 1].sireID)))
                    animals[int(animals[int(_f) - 1].sireID) - 1].daus[_f] = int(_f)
            if int(animals[int(_f) - 1].damID) != 0 and int(animals[int(_f) - 1].animalID) != 0:
                try:
                    _fd = animals[int(animals[int(_f) - 1].damID) - 1].daus[_f]
                except KeyError:
                    if debug:
                        print(('\t%s is a DAUGHTER of DAM %s' % (animals[int(_f) - 1].animalID,animals[int(_f) - 1].damID)))
                        print(('\tAdding animal %s to dam %s\'s daus list.' % (_f,animals[int(_f) - 1].damID)))
                    animals[int(animals[int(_f) - 1].damID) - 1].daus[_f] = int(_f)
        except:
            pass

    for _u in unknowns:
        try:
            if debug:
                print(('[DEBUG]: UNKNOWN %s has SIRE %s and DAM %s' % (animals[int(_u) - 1].animalID,animals[int(_u) - 1].sireID,animals[int(_u) - 1].damID)))
            if int(animals[int(_u) - 1].sireID) != 0 and int(animals[int(_u) - 1].animalID) != 0:
                try:
                    _ud = animals[int(animals[int(_u) - 1].sireID) - 1].unks[_u]
                except KeyError:
                    if debug:
                        print(('\t%s (UNK) has SIRE %s' % (animals[int(_u) - 1].animalID,animals[int(_u) - 1].sireID)))
                    animals[int(animals[int(_u) - 1].sireID) - 1].unks[_u] = int(_u)
            if int(animals[int(_u) - 1].damID) != 0 and int(animals[int(_u) - 1].animalID) != 0:
                try:
                    if debug:
                        print(('\t%s (UNK) has DAM %s' % (animals[int(_u) - 1].animalID,animals[int(_u) - 1].damID)))
                    _ud = animals[int(animals[int(_u) - 1].damID) - 1].unks[_u]
                except KeyError:
                    animals[int(animals[int(_u) - 1].damID) - 1].unks[_u] = int(_u)
        except:
            pass

    if debug:
        for _a in animals:
            print(('[DEBUG]: Animal %s:' % (_a.animalID)))
            print(('\tSons: %s' % (_a.sons)))
            print(('\tDaus: %s' % (_a.daus)))
            print(('\tUnks: %s' % (_a.unks)))                
        print(('[DEBUG]: males ', males))
        print(('[DEBUG]: females ', females))
        print(('[DEBUG]: unknowns ', unknowns))

    infile.close()
    if debug:
        print('')
        print(('[MESSAGE]: %s animal records read from pedigree file %s'  %(animalCounter,inputfile)))
        print(('[MESSAGE]: %s animal records created from the pedigree file' % (len(animals))))
        print(('[MESSAGE]: %s unique sires found in the pedigree file' % (len(males))))
        print(('[MESSAGE]: %s unique dams found in the pedigree file' % (len(females))))
        print(('[MESSAGE]: %s unique animals of unknown gender found in the pedigree file' % (len(unknowns))))
        print('')

    return animals

##
# set_ancestor_flag() loops through a pedigree to build a dictionary of all of the parents
# in the pedigree.  It then sets the ancestor flags for the parents.  It assumes that the
# pedigree is reordered and renumbered.  NOTE: set_ancestor_flag() expects a reordered and
# renumbered pedigree as input!
# @param myped A PyPedal pedigree object.
# @param filetag A descriptor prepended to output file names.
# @param io Indicates whether or not to write an ancestor list to a file.
# @return 0 for failure and 1 for success.
# @defreturn integer
def set_ancestor_flag(myped,filetag='_ancestor_',io='no',debug=0):
    parents = {}        # holds a list of animals who are parents
    l = len(myped)
    if l < 2:
        print('[ERROR]: myped only contains one record -- nothing to do in set_ancestor_flag()!')
        return

    myped.reverse()     # We want to go from young to old.
    for i in range(l):
        # Put the animalIDs of the animals parents in the parents list if
        # they are known and are not already in the dictionary.
        if debug == 1:
            print(('[DEBUG]:\t\tanimal: %s\tsire: %s\tdam: %s' % (myped[i].animalID,myped[i].sireID,myped[i].damID)))
        if int(myped[i].sireID) != 0:
            try:
                _i = parents[int(myped[i].sireID)]
            except:
                parents[int(myped[i].sireID)] = int(myped[i].sireID)
                myped[int(myped[i].sireID)-1].ancestor = 1

        if int(myped[i].damID) != 0:
            try:
                _i = parents[int(myped[i].damID)]
            except:
                parents[int(myped[i].damID)] = int(myped[i].damID)
                myped[int(myped[i].damID)-1].ancestor = 1
    myped.reverse()     # Put myped back the way it was -- pass-by-reference, don't you know!

    if io == 'yes':
        a_outputfile = '%s%s%s' % (filetag,'_ancestors','.dat')
        aout = open(a_outputfile,'w')
        aname = '# FILE: %s\n' % (a_outputfile)
        aout.write(aname)
        aout.write('# ANCESTOR list produced by PyPedal.\n')
        for l in list(parents.keys()):
            line = '%s\n' % (l)
            aout.write(line)
        aout.close()
    return 1

##
# set_generation() Works through a pedigree to infer the generation to which an animal
# belongs based on founders belonging to generation 1.  The igen assigned to an animal
# as the larger of sire.igen+1 and dam.igen+1.  This routine assumes that myped is
# reordered and renumbered.
# @param myped A PyPedal pedigree object.
def set_generation(myped):
    l = len(myped)
    for i in range(l):
        if int(myped[i].sireID) == 0 and int(myped[i].damID) == 0:
            myped[i].igen = 1
        elif int(myped[i].sireID) == 0:
            myped[i].igen = myped[int(myped[i].damID)-1].igen + 1
        elif int(myped[i].damID) == 0:
            myped[i].igen = myped[int(myped[i].sireID)-1].igen + 1
        else:
            myped[i].igen = max(myped[int(myped[i].sireID)-1].igen + 1,myped[int(myped[i].damID)-1].igen + 1)

##
# set_age() Computes ages for all animals in a pedigree based on the global
# BASE_DEMOGRAPHIC_YEAR defined in pyp_demog.py.  If the by is unknown, the
# inferred generation is used.  If the inferred generation is unknown, the
# age is set to -999.
# @param myped A PyPedal pedigree object.
def set_age(myped):
    l = len(myped)
    for i in range(l):
        if myped[i].by == -999 and myped[i].igen == -999:
            myped[i].age = -999
        elif myped[i].by == -999 and myped[i].igen != -999:
            myped[i].age = myped[i].igen
        else:
            myped[i].age = myped[i].by - BASE_DEMOGRAPHIC_YEAR

##
# set_species() assigns a specie to every animal in the pedigree.
# @param myped A PyPedal pedigree object.
# @param species A PyPedal string.
def set_species(myped,species='u'):
    l = len(myped)
    for i in range(l):
        if len(species) > 0:
            myped[i].species = species
        else:
            myped[i].species = 'u'

##
# assign_sexes() assigns a sex to every animal in the pedigree using sire and daughter
# lists for improved accuracy.
# @param myped A renumbered and reordered PyPedal pedigree object.
# @param debug Flag to indicate whether or not progress messages are written to stdout.
def assign_sexes(myped,debug=0):
    for _m in myped:
        if int(_m.sireID) == 0 and int(_m.damID) == 0:
            pass
        elif int(_m.sireID) == 0:
            if myped[int(_m.damID)-1].sex != 'f':
                if debug:
                    print(('\t\tAnimal %s has sex %s' % (_m.damID,myped[int(_m.damID)-1].sex)))
                    print(('\t\tAnimal %s sex set to \'f\'' % (_m.damID)))
                myped[int(_m.damID)-1].sex = 'f'
        elif int(_m.damID) == 0:
            if myped[int(_m.sireID)-1].sex != 'm':
                if debug:
                    print(('\t\tAnimal %s sex set to \'m\'' % (_m.sireID)))
                    print(('\t\tAnimal %s has sex %s' % (_m.sireID,myped[int(_m.sireID)-1].sex)))
                myped[int(_m.sireID)-1].sex = 'm'
        else:
            if myped[int(_m.damID)-1].sex != 'f':
                if debug:
                    print(('\t\tAnimal %s has sex %s' % (_m.damID,myped[int(_m.damID)-1].sex)))
                    print(('\t\tAnimal %s sex set to \'f\'' % (_m.damID)))
                myped[int(_m.damID)-1].sex = 'f'
            if myped[int(_m.sireID)-1].sex != 'm':
                if debug:
                    print(('\t\tAnimal %s has sex %s' % (_m.sireID,myped[int(_m.sireID)-1].sex)))
                    print(('\t\tAnimal %s sex set to \'m\'' % (_m.sireID)))
                myped[int(_m.sireID)-1].sex = 'm'

##
# assign_offspring() assigns offspring to their parent(s)'s unknown sex offspring
# list (well, dictionary).
# @param myped A renumbered and reordered PyPedal pedigree object.
# @param debug Flag to indicate whether or not progress messages are written to stdout.
def assign_offspring(myped,debug=0):
    try:
        for _m in myped:
            myped[int(_m.animalID)-1].unks = {}
        for _m in myped:
            #print 'Animal %s has sire %s and dam %s' % (_m.animalID,_m.sireID,_m.damID)
            if int(_m.sireID) == 0 and int(_m.damID) == 0:
                pass
            elif int(_m.sireID) == 0:
#                 print '\tAdding animal %s to unk list for dam %s' % (_m.animalID,myped[int(_m.damID)-1].animalID)
                myped[int(_m.damID)-1].unks[_m.animalID] = _m.animalID
            elif int(_m.damID) == 0:
#                 print '\tAdding animal %s to unk list for sire %s' % (_m.animalID,myped[int(_m.sireID)-1].animalID)
                myped[int(_m.sireID)-1].unks[_m.animalID] = _m.animalID
            else:
#                 print '\tAdding animal %s to unk list for dam %s' % (_m.animalID,myped[int(_m.damID)-1].animalID)
                myped[int(_m.damID)-1].unks[_m.animalID] = _m.animalID
#                 print '\tAdding animal %s to unk list for sire %s' % (_m.animalID,myped[int(_m.sireID)-1].animalID)
                myped[int(_m.sireID)-1].unks[_m.animalID] = _m.animalID
#         for _m in myped:
#             print 'Unk list for animal %s:\t%s' % (_m.animalID,_m.unks)
    except:
        print('[ERROR]: Unable to assign offspring in pyp_utils/assign_offspring().  This routine requires a renumbered pedigree!')
##
# reorder() renumbers a pedigree such that parents precede their offspring in the
# pedigree.  In order to minimize overhead as much as is reasonably possible,
# a list of animal IDs that have already been seen is kept.  Whenever a parent
# that is not in the seen list is encountered, the offspring of that parent is
# moved to the end of the pedigree.  This should ensure that the pedigree is
# properly sorted such that all parents precede their offspring.  myped is
# reordered in place.  reorder() is VERY slow, but I am pretty sure that it works
# correctly.
# @param myped A PyPedal pedigree object.
# @param filetag A descriptor prepended to output file names.
# @param io Indicates whether or not to write the reordered pedigree to a file (yes|no).
# @return A reordered PyPedal pedigree.
# @defreturn list
def reorder(myped,filetag='_reordered_',io='no'):
    """Renumber a pedigree such that parents precede their offspring in the
 pedigree.  In order to minimize overhead as much as is reasonably possible,
 a list of animal IDs that have already been seen is kept.  Whenever a parent
 that is not in the seen list is encountered, the offspring of that parent is
 moved to the end of the pedigree.  This should ensure that the pedigree is
 properly sorted such that all parents precede their offspring.  myped is
 reordered in place.

 reorder() is VERY slow, but I am pretty sure that it works correctly."""

    # This is crufty and therefore offensive.  Furthermore, it will only work when
    # animal IDs are integers.  Some solution to this problem needs to be found.  Perhaps a
    # strcmp()-type string method can be used for generalization...
    l = len(myped)
#     print 'Pedigree contains %s animals.' % (l)
    pedordered = 0  # the pedigree is not known to be ordered
    passnum = 0     # we are going to count how many passes through the pedigree are needed
                    # to sort it
                    
#     for i in range(l):
#         print '%s\t%s\t%s' % (myped[i].animalID, myped[i].sireID, myped[i].damID)
#     print '='*100

    while(1):
        #
        # Loop over the pedigree.  Whenever a parent follows their offspring in the
        # pedigree, move the child to the end of the pedigree.  Continue until all parents precede
        # their offspring.
        #
        #if ( passnum == 0 ) or ( passnum % 10 == 0 ):
        #print '-'*100
        #print '...%s' % (passnum)
            
        order = []
        _sorted_counter = 0
        _noparents_counter = 0
        
        for i in range(l):
            order.append(int(myped[i].animalID))
#         print order
            
        for i in range(l):
            if int(myped[i].sireID) > 0 and order.index(int(myped[i].sireID)) > order.index(int(myped[i].animalID)):
                _a = myped[i]
                # If the sire is after the animal in the index, insert the animal ahead of the sire.
                myped.insert(order.index(int(myped[i].sireID))+1, myped[i])
#                 print '\tMoving animal %s ahead of its sire (%s).' % ( myped[i].animalID, myped[i].sireID )
                # Add the animal's ID to the order list to update its location in the pedigree
                order.insert(order.index(int(myped[i].sireID))+1, int(myped[i].animalID))
                # Delete the animal's original (first) record in the pedigree file.
                del myped[i]
                # Delete the animal's original (first) record in the order list.
                del order[order.index(int(_a.animalID))]
            
            if int(myped[i].damID) > 0 and order.index(int(myped[i].damID)) > order.index(int(myped[i].animalID)):
                _a = myped[i]
                # If the dam is after the animal in the index, insert the animal ahead of the dam.
                myped.insert(order.index(int(myped[i].damID))+1, myped[i])
#                 print '\tMoving animal %s ahead of its dam (%s).' % ( myped[i].animalID, myped[i].damID )
                # Add the animal's ID to the order list to update its location in the pedigree
                order.insert(order.index(int(myped[i].damID))+1, int(myped[i].animalID))
                # Delete the animal's original (first) record in the pedigree file.
                del myped[i]
                # Delete the animal's original (first) record in the order list.
                del order[order.index(int(_a.animalID))]

#         print order
        for i in range(l):

            if int(myped[i].sireID) == 0 and int(myped[i].damID) == 0:
                #pedordered = 0
#                 print 'IDs\t%s\t%s\t%s\t' % ( int(myped[i].animalID), int(myped[i].sireID), int(myped[i].damID) ),
#                 if int(myped[i].sireID) == 0 and int(myped[i].damID) == 0:
#                     print 'Loc\t%s\t-\t-' % ( order.index(int(myped[i].animalID)) )
#                 else:
#                     print 'Loc\t%s\t%s\t%s' % ( order.index(int(myped[i].animalID)), order.index(int(myped[i].sireID)), order.index(int(myped[i].damID)) )
                _noparents_counter = _noparents_counter + 1
                pass
            elif int(myped[i].sireID) != 0 and order.index(int(myped[i].animalID)) < order.index(int(myped[i].sireID)):
                #pedordered = 0
#                 print 'IDs\t%s\t%s\t%s\t' % ( int(myped[i].animalID), int(myped[i].sireID), int(myped[i].damID) ),
#                 if int(myped[i].sireID) == 0 and int(myped[i].damID) == 0:
#                     print 'Loc\t%s\t-\t-' % ( order.index(int(myped[i].animalID)) )
#                 else:
#                     print 'Loc\t%s\t%s\t%s' % ( order.index(int(myped[i].animalID)), order.index(int(myped[i].sireID)), order.index(int(myped[i].damID)) )
                pass
            elif int(myped[i].damID) != 0 and order.index(int(myped[i].animalID)) < order.index(int(myped[i].damID)):
                #pedordered = 0
#                 print 'IDs\t%s\t%s\t%s\t' % ( int(myped[i].animalID), int(myped[i].sireID), int(myped[i].damID) ),
#                 if int(myped[i].sireID) == 0 and int(myped[i].damID) == 0:
#                     print 'Loc\t%s\t-\t-' % ( order.index(int(myped[i].animalID)) )
#                 else:
#                     print 'Loc\t%s\t%s\t%s' % ( order.index(int(myped[i].animalID)), order.index(int(myped[i].sireID)), order.index(int(myped[i].damID)) )
                pass
            else:
#                 print 'IDs\t%s\t%s\t%s\t' % ( int(myped[i].animalID), int(myped[i].sireID), int(myped[i].damID) ),
#                 if int(myped[i].sireID) == 0 and int(myped[i].damID) == 0:
#                     print 'Loc\t%s\t-\t-\t***' % ( order.index(int(myped[i].animalID)) )
#                 else:
#                     print 'Loc\t%s\t%s\t%s\t***' % ( order.index(int(myped[i].animalID)), order.index(int(myped[i].sireID)), order.index(int(myped[i].damID)) )
                _sorted_counter = _sorted_counter + 1

#         print 'Sorted: %s' % ( _sorted_counter )
#         print 'No parents: %s' % ( _noparents_counter )
#         print 'Length: %s' % ( l )
                                
        if _sorted_counter == ( l - _noparents_counter ):
            break
        else:
            passnum = passnum + 1

#     print '='*100
#     for i in range(l):
#         print '%s\t%s\t%s' % (myped[i].animalID, myped[i].sireID, myped[i].damID)

    if io == 'yes':
        # Write the reordered pedigree to a file and return the ordered pedigree.
        # Note that the reordered pedigree is currently only writte in the 'asd'
        # format, regardless of the format of the original file.
        a_outputfile = '%s%s%s' % (filetag,'_reordered','.ped')
        aout = open(a_outputfile,'w')
        aname = '# FILE: %s\n' % (a_outputfile)
        aout.write(aname)
        aout.write('# REORDERED pedigree produced by PyPedal.\n')
        aout.write('% asd\n')
        for l in range(len(myped)):
            line = '%s,%s,%s\n' % (myped[l].animalID,myped[l].sireID,myped[l].damID)
            aout.write(line)
        aout.close()
        
        del order, seen, kill
        
    return myped

##
# fast_reorder() renumbers a pedigree such that parents precede their offspring in
# the pedigree.  In order to minimize overhead as much as is reasonably possible,
# a list of animal IDs that have already been seen is kept.  Whenever a parent
# that is not in the seen list is encountered, the offspring of that parent is
# moved to the end of the pedigree.  This should ensure that the pedigree is
# properly sorted such that all parents precede their offspring.  myped is
# reordered in place.  fast_reorder() uses dictionaries to renumber the pedigree
# based on paddedIDs.
# @param myped A PyPedal pedigree object.
# @param filetag A descriptor prepended to output file names.
# @param io Indicates whether or not to write the reordered pedigree to a file (yes|no).
# @param debug Flag to indicate whether or not debugging messages are written to STDOUT.
# @return A reordered PyPedal pedigree.
# @defreturn list
def fast_reorder(myped,filetag='_new_reordered_',io='no',debug=0):
    """Renumber a pedigree such that parents precede their offspring in the
 pedigree.  In order to minimize overhead as much as is reasonably possible,
 a list of animal IDs that have already been seen is kept.  Whenever a parent
 that is not in the seen list is encountered, the offspring of that parent is
 moved to the end of the pedigree.  This should ensure that the pedigree is
 properly sorted such that all parents precede their offspring.  myped is
 reordered in place.

 reorder() is VERY slow, but I am pretty sure that it works correctly.  fast_reorder()
 appears to be VERY fast, but I am not sure if it works correctly all of the time or not.
 Use this procedure at your own risk!"""

    l = len(myped)
    idlist = []
    animalmap = {}
    ## <kludge>
    myped.reverse()
    ## </kludge>
    if debug == 1:
        print(('\tPedigree contains %s animals.' % (l)))
        print('\tMaking a dictionary of animal objects')
        print('\tMaking a list of padded animal IDs')
    for i in range(l):
        if debug == 1:
            print(('\tDEBUG\tID %s: %s = %s %s %s' % (i,myped[i].animalID,myped[i].paddedID,myped[i].sireID,myped[i].damID)))
        animalmap[myped[i].paddedID] = myped[i]
        idlist.append(int(myped[i].paddedID))
#    if debug:
#   print '='*80
#   print 'Printing unsorted ID list...'
#   print '%s' % (idlist)
#   print '='*80

    #print '\tSorting padded animal IDs'
    idlist.sort()
#    if debug == 1:
#   print '='*80
#        print 'Printing sorted ID list...'
#        print '%s' % (idlist)
#        print '='*80
    myped = []
    #print '\tReforming myped...'
    l = len(idlist)
    if debug == 1:
        print(('[DEBUG]: %s elements in idlist' % (l)))
        print('[DEBUG]: Printing reordered pedigree...')
    #print animalmap
    for i in range(len(idlist)):
        #print i,  ' ', idlist[i]
        #print idlist[i], animalmap[str(idlist[i])]
        myped.append(animalmap[str(idlist[i])])
    if debug == 1:
        print(('\t[DEBUG]:\tID %s: %s = %s' % (i,myped[i].animalID,myped[i].paddedID)))
    if io == 'yes':
        # Write the reordered pedigree to a file and return the ordered pedigree.
        # Note that the reordered pedigree is currently only written in the 'asd'
        # format, regardless of the format of the original file.
        a_outputfile = '%s%s%s' % (filetag,'_reord','.ped')
        aout = open(a_outputfile,'w')
        aname = '# FILE: %s\n' % (a_outputfile)
        aout.write(aname)
        aout.write('# REORDERED pedigree produced by PyPedal using fast_reorder().\n')
        aout.write('% asd\n')
        for l in range(len(myped)):
            line = '%s,%s,%s\n' % (myped[l].animalID,myped[l].sireID,myped[l].damID)
            aout.write(line)
        aout.close()
    return myped

##
# renumber() takes a pedigree as input and renumbers it such that the oldest
# animal in the pedigree has an ID of '1' and the n-th animal has an ID of 'n'.  If the
# pedigree is not ordered from oldest to youngest such that all offspring precede their
# offspring, the pedigree will be reordered.  The renumbered pedigree is written to disc in
# 'asd' format and a map file that associates sequential IDs with original IDs is also
# written.
# @param myped A PyPedal pedigree object.
# @param filetag A descriptor prepended to output file names.
# @param io Indicates whether or not to write the renumbered pedigree to a file (yes|no).
# @param outformat Flag to indicate whether or not ro write an asd pedigree (0) or a full pedigree (1).
# @param debug Flag to indicate whether or not progress messages are written to stdout.
# @return A reordered PyPedal pedigree.
# @defreturn list
def renumber(myped,filetag='_renumbered_',io='no',outformat='0',debug=0):
    """renumber() takes a pedigree as input and renumbers it such that the oldest
    animal in the pedigree has an ID of '1' and the n-th animal has an ID of 'n'.  If the
    pedigree is not ordered from oldest to youngest such that all offspring precede their
    offspring, the pedigree will be reordered.  The renumbered pedigree is written to disc in
    'asd' format and a map file that associates sequential IDs with original IDs is also
    written."""

    if debug == 1:
        print(('[DEBUG]: Pedigree of size %s passed to renumber()' % (len(myped))))
    #for i in range(len(myped)):
    #   print myped[i].animalID,
    #print

    # In the dictionary id_map, the old IDs are the keys and the
    # new IDs are the values.
    id_map = {}
    idnum = 1       # starting ID number for renumbered IDs
    for l in range(len(myped)):
        if debug == 1:
            if l == 0:
                print('[DEBUG]: Renumbering the pedigree...')
            if fmod(l,10000) == 0:
                print(('\t%s ' % (l)))
            print(('[DEBUG]: An:%s (%s)\tSire: %s\tDam: %s' % (myped[l].animalID,myped[l].paddedID,myped[l].sireID,myped[l].damID)))
        id_map[myped[l].animalID] = idnum
        #myped[l].animalID = id_map[myped[l].animalID]
        if debug == 1:
            print(('\t[DEBUG]: Renumbering animal from %s to %s (iter %s)' % (myped[l].animalID,idnum,l)))
        myped[l].renumberedID = idnum
        myped[l].animalID = idnum
        # We cannot forget to renumber parents, too!
        s = myped[l].sireID
        if s != '0' and s != 0:
        # This is a hack to deal with offspring that have birthdates which precede their parents'.
            try:
                if debug == 1:
                    print(('\t\t[DEBUG]: Renumbering sire from %s to %s' % (s,id_map[s])))
                myped[l].sireID = id_map[s]
            except:
                myped[l].sireID = 0
        d = myped[l].damID
        if d != '0' and d != 0:
        # This is a hack to deal with offspring that have birthdates which precede their parents'.
            try:
                if debug == 1:
                    print(('\t\t[DEBUG]: Renumbering dam from %s to %s' % (d,id_map[d])))
                myped[l].damID = id_map[d]
            except:
                myped[l].damID = 0
        idnum = idnum + 1
        #print 'DEBUG: animal ID = %s' % (myped[l].animalID)
        #print 'DEBUG: An:%s\tSire: %s\tDam: %s' % (myped[l].animalID,myped[l].sireID,myped[l].damID)
        #print
    if io == 'yes':
        # Write the renumbered pedigree to a file
        ped_outputfile = '%s%s%s' % (filetag,'_renum','.ped')
        pout = open(ped_outputfile,'w')
        pname = '# FILE: %s\n' % (ped_outputfile)
        pout.write(pname)
        pout.write('# RENUMBERED pedigree produced by PyPedal.\n')
        pout.write('% asd\n')
        for l in range(len(myped)):
            if outformat == '0' or outformat == 0:
                line = '%s,%s,%s\n' % (myped[l].animalID,myped[l].sireID,myped[l].damID)
            else:
                line = '%s,%s,%s,%s,%s,%s,%s\n' % (myped[l].animalID,myped[l].sireID,myped[l].damID,myped[l].by,
                    myped[l].sex,myped[l].fa,myped[l].gen)
            pout.write(line)
        pout.close()
    # Write the old ID -> new ID mapping to a file
    map_outputfile = '%s%s%s' % (filetag,'_id_map','.map')
    #print '[DEBUG]: ID map file name is %s' % (map_outputfile)
    mout = open(map_outputfile,'w')
    mname = '# FILE: %s\n' % (map_outputfile)
    mout.write(mname)
    mout.write('# Renumbered ID to Old ID mapping produced by PyPedal.\n')
    mout.write('# The lefthand column contains the original IDs.\n')
    mout.write('# The righthand column contains the renumbered IDs.\n')
    mout.write('# Old ID\tRenum ID\n')
    k = list(id_map.keys())
    v = list(id_map.values())
    for l in range(len(id_map)):
        line = '%s,%s\n' % (k[l],v[l])
        #print 'Old ID = %s,  New ID = %s' % (k[l],v[l])
        mout.write(line)
    mout.close()
    #print 'ID map in renumber():%s' % (id_map)
    return myped

##
# load_id_map() reads an ID map from the file generated by pyp_utils/renumber()
# into a dictionary.  There is a VERY similar function, pyp_io/id_map_from_file(), that
# is deprecated because it is much more fragile that this procedure.
# @param filetag A descriptor prepended to output file names that is used to determine the input file name.
# @return A dictionary whose keys are renumbered IDs and whose values are original IDs.
# @defreturn dictionary
def load_id_map(filetag='_renumbered_'):
    try:
        _infile = '%s%s%s' % (filetag,'_id_map','.map')
        #print '[DEBUG]: ID map infile name is %s' % (_infile)
        mapin = open(_infile,'r')
        idmap = {}
        while 1:
            line = mapin.readline()
            if not line:
                break
            else:
                line = string.strip(line[:-1])
                if line[0] == '#':
                    pass
                else:
                    _line = string.split(line,',')
                    if len(_line) != 2:
                        print(('[ERROR]: Invalid number of elements in line read from ID map file (%s)' % (_line)))
                        break
                    else:
                        idmap[int(_line[1])] = int(_line[0])
        mapin.close()
    except:
        print(('[ERROR]: Could not open the ID map file %s in load_id_map()!' % (_infile)))
        sys.exit(0)
    #print 'ID map in load_id_map():%s' % (idmap)
    return idmap

##
# delete_id_map() checks to see if an ID map for the given filetag exists.  If the file exists, it is
# deleted.
# @param filetag A descriptor prepended to output file names that is used to determine name of the file to delete.
# @return A flag indicating whether or not the file was successfully deleted (0|1)
# @defreturn integer
def delete_id_map(filetag='_renumbered_'):
    try:
        _infile = '%s%s%s' % (filetag,'_id_map','.map')
        if _infile in os.listdir('.'):
            os.remove(_infile)
        return 1
    except:
        return 0

##
# id_map_new_to_old() takes an ID from a renumbered pedigree and an ID map, and returns the original
# ID number.
# @param id_map A dictionary mapping renumbered animalIDs to original animalIDs.
# @param new_id A renumbered animalID.
# @return A dictionary whose keys are renumbered IDs and whose values are original IDs.
# @defreturn integer
def id_map_new_to_old(id_map,new_id):
    """Given an ID from a renumbered pedigree, return the original
    ID number."""
    old_id = id_map.get(new_id,0)
    return old_id

##
# trim_pedigree_to_year() takes pedigrees and removes all individuals who were not born
# in birthyear 'year'.
# @param myped A PyPedal pedigree object.
# @param year A birthyear.
# @return A pedigree containing only animals born in the given birthyear.
# @defreturn list
def trim_pedigree_to_year(myped,year):
    # trim_pedigree_to_year() takes pedigrees and removes all individuals
    # who were not born in birthyear 'year'.  The reduced (trimmed) pedigree
    # is returned.
    indices = []
    modped = myped[:]
    for l in range(len(modped)):
        #print 'DEBUG: %s, %s' % (year,modped[l].by)
        if int(modped[l].by) == int(year):
            pass
        else:
            #del modped[l]
            indices.append(l)
    indices.reverse()
    for i in range(len(indices)):
        del modped[indices[i]]
    #print 'DEBUG: l_orig: %s, l_trim: %s' % (len(myped),len(modped))
    return modped

##
# pedigree_range() takes a renumbered pedigree and removes all individuals
# with a renumbered ID > n.  The reduced pedigree is returned.  Assumes that
# the input pedigree is sorted on animal key in ascending order.
# @param myped A PyPedal pedigree object.
# @param n A renumbered animalID.
# @return A pedigree containing only animals born in the given birthyear.
# @defreturn list
def pedigree_range(myped,n):
    # pedigree_range() takes a renumbered pedigree and removes all individuals
    # with a renumbered ID > n.  The reduced pedigree is returned.  Assumes that
    # the input pedigree is sorted on animal key in ascending order.
    modped = []
    for i in range(n):
        modped.append(myped[i])
        return modped

##
# sort_dict_by_keys() returns a dictionary where the values in the dictionary
# in the order obtained by sorting the keys.  Taken from the routine sortedDictValues3
# in the "Python Cookbook", p. 39.
# @param mydict A non-empty Python dictionary.
# @return The input dictionary with keys sorted in ascending order.
# @defreturn dictionary
def sort_dict_by_keys(mydict):
    if len(mydict) == 0:
        return mydict
    else:
        keys = list(mydict.keys())
        keys.sort()
        return list(map(mydict.get, keys))      

##
# simple_histogram_dictionary() returns a dictionary containing a simple, text histogram.
# The input dictionary is assumed to contain keys which are distinct levels and values
# that are counts.
# @param mydict A non-empty Python dictionary.
# @param histchar The character used to draw the histogram (default is '*').
# @param histstep Used to determine the number of bins (stars) in the diagram.
# @return A dictionary containing the histogram by level.
# @defreturn dictionary
def simple_histogram_dictionary(mydict,histchar='*',histstep=5):
    hist_dict = {}
    hist_sum = 0.
    if histstep < 0 or histstep > 100:
        histstep = 5
    for k in list(mydict.keys()):
        hist_sum = hist_sum + mydict[k]
    #print '[DEBUG]: %s' % (hist_sum)
    for k in list(mydict.keys()):
        _freq = ( float(mydict[k]) / float(hist_sum) ) * 100.
        _v = around(_freq,0)
        _n_stars = int( around( (_v / float(histstep)),0 ) )
        #print '[DEBUG]: %s' % (_n_stars)
        if _n_stars > 0:
            hist_dict[k] = '%s%s' % (histchar*_n_stars,' '*(20-_n_stars))
        else:
            hist_dict[k] = '%s' % (' '*20)
    return hist_dict

##
# reverse_string() reverses the input string and returns the reversed version.
# @param mystring A non-empty Python string.
# @return The input string with the order of its characters reversed.
# @defreturn string
def reverse_string(mystring):
    if len(mystring) < 2:
        return mystring
    else:
        mystringreversed = []
        for l in range(len(mystring)):
            mystringreversed.append(mystring[l])
            mystringreversed.reverse().join()
        return mystringreversed

##
# new_preprocess() processes a pedigree file, which includes reading the animals
# into a list of animal objects, forming lists of sires and dams, and checking for
# common errors.
# @param inputfile Name of the file from which the pedigree is to be read.
# @param sepchar What character separates entries in the pedigree file (default is CSV).
# @param debug Flag to indicate whether or not progress messages are written to stdout.
# @return A list of Animal() objects; this is what PyPedal calls a pedigree.
    


# @defreturn list
# def new_preprocess(**kw):
#     """Preprocess a pedigree file, which includes reading the animals into a list, forming lists of sires and dams, and checking for common errors."""
#     lineCounter = 0     # count the number of lines in the pedigree file
#     animalCounter = 0   # count the number of animal records in the pedigree file
#     animals= []     # holds a list of Animal() objects
#     _animals = {}
#     males = {}      # holds a list of male IDs in the pedigree
#     females = {}        # holds a list of female IDs in the pedigree
#     unknowns = {}       # holds a list of animals of unknown sex
#     pedformat = ''      # stores the pedigree format string
#     infile=open(inputfile,'r')
#     while 1:
#         line = infile.readline()
#         if not line:
#             break
#         else:
#             if debug > 1:
#                 print(line)
#             line = string.strip(line[:-1])
#             lineCounter = lineCounter + 1
#             if line[0] == '#':
#                 pass
#             elif line[0] == '%':
#                 old_pedformat = string.strip(line[1:]) # this lets us specify the format of the pedigree file
#                 pass
#             else:
#                 if debug == 1:
#                     if fmod(animalCounter,10000) == 0:
#                         print(('%s ' % (animalCounter)))
#                 animalCounter = animalCounter + 1
#                 l = string.split(line,sepchar)
#                 # Some people *cough* Brad Heins *cough* insist on sending me pedigree
#                 # files vomited out by Excel, which pads cells in a column with spaces
#                 # to right-align them...
#                 for i in range(len(l)):
#                     l[i] = string.strip(l[i])
#                 if len(l) < 3:
#                     errorString = 'The record on line %s of file %s is too short - all records must contain animal, sire, and dam ID numbers (%s fields detected).\n' % (lineCounter,inputfile,len(l))
#                     print(('[ERROR]: %s' % (errorString)))
#                     break
#                 # now we have to deal with different pedigree data formats...
#                 #
#                 # 07/20/2004
#                 # Thoughts on fixing this mess
#                 # ----------------------------
#                 # 01. Define a set of single-digit codes to variable types:
#                 # 01a. a = animal
#                 # 01b. s = sire
#                 # 01c. d = dam
#                 # 01d. g = generation
#                 # 01e. x = sex
#                 # 01f. b = birth year in YYYY format (?)
#                 # 01g. f = inbreeding
#                 # 01h. t = alleles (NOTE: occupies two adjacent columns)
#                 # 01i. r = breed
#                 # 01j. n = name
#                 # 01k. y = birthyear in MM/DD/YYYY format (?)
#                 # 01l. l = alive (1) or dead (0)
#                 # o1m. e = age
#                 # 02. Read the format string
#                 # 03. Use len() to find the number of codes in the format string
#                 # 04. Check for duplicate codes -- throw error if necessary
#                 # 05. Populate a dictionary to map codes to columns
#                 # 06. Process datalines:
#                 # 06a.    Split the line based on the sepchar
#                 # 06b.    Map the data in the split dataline to the proper
#                 #     Animal() object __init__ keywords based using the
#                 #     dictionary from step 05.  This does imply that ALL
#                 #     arguments to the __init__() method must be keyword
#                 #     arguments.  That is not a big deal, but it will
#                 #     require some tweakage of the code to avoid breakage.
#                 # This method is a little more complicated than the current method
#                 # but it is much less clumsy and is more easily extensible.  Looking
#                 # at the 'b' and 'y' codes, it appears that I may have to think care-
#                 # fully about handling dates, which is always a can of worms.
#                 #
#                 # OK, now we are in new_peprocess, which is going to implement these suggested changes.
#                 # A variable, 'performat, is passed as a parameter that indicates the format of the
#                 # pedigree in the input file.  Note that the A PERIGREE FORMAT STRING IS NO LONGER
#                 # REQUIRED in the input file, and any found will be ignored.  The index of the single-
#                 # digit code in the format string indicates the column in which the corresponding
#                 # variable is found.  Duplicate values in the pedformat atring are ignored.
#                 pedformat_codes = ['a','s','d','g','x','b','f','t','r','n','y','l','e']
#                 critical_count = 0  # Number of critical errors encountered
#                 if not pedformat:
#                         pedformat = 'asd'
#                 if debug:
#                         print('[DEBUG]: Null pedigree format string assigned a default value in pyp_utils/new_preprocess().')
#                 # This is where we check the format string to figure out what we have in the input file.
#                 # Check for valid characters...
#                 _pedformat = []
#                 for _char in pedformat:
#                     if _char in pedformat_codes:
#                         _pedformat.append(_char)
#                     else:
#                         # Replace the invalid code with a period, which is ignored when the string is parsed.
#                         _pedformat.append('.')
#                         if debug:
#                             print(('[DEBUG]: Invalid variable type, %s, encountered in pedigree format string in pyp_utils/new_peprocess()' % (_char)))
#                 for _char in _pedformat:
#                     try:
#                         _animal = _performat.index('a')
#                     except ValueError:
#                         print(('[CRITICAL]: No animal identification code was specified in the pedigree format string %s!  This is a critical error and the program will halt.' % (_pedformat)))
#                         critical_count = critical_count + 1
#                     try:
#                         _sire = _performat.index('s')
#                     except ValueError:
#                         print(('[CRITICAL]: No sire identification code was specified in the pedigree format string %s!  This is a critical error and the program will halt.' % (_pedformat)))
#                         critical_count = critical_count + 1
#                     try:
#                         _dam = _performat.index('d')
#                     except ValueError:
#                         print(('[CRITICAL]: No dam identification code was specified in the pedigree format string %s!  This is a critical error and the program will halt.' % (_pedformat)))
#                         critical_count = critical_count + 1
#                     try:
#                         _generation = _pedformat.index('g')
#                     except ValueError:
#                         if debug:
#                             print(('[DEBUG]: No generation code was specified in the pedigree format string %a.  This program will continue.' % (_pedformat)))
#                     try:
#                         _sex = _pedformat.index('x')
#                     except ValueError:
#                         if debug:
#                             print(('[DEBUG]: No sex code was specified in the pedigree format string %a.  This program will continue.' % (_pedformat)))
#                     try:
#                         _by_yyyy = _pedformat.index('b')
#                     except ValueError:
#                         if debug:
#                             print(('[DEBUG]: No birth year (YYYY) code was specified in the pedigree format string %a.  This program will continue.' % (_pedformat)))
#                     try:
#                         _inbreeding = _pedformat.index('f')
#                     except ValueError:
#                         if debug:
#                             print(('[DEBUG]: No coeffcient of inbreeding code was specified in the pedigree format string %a.  This program will continue.' % (_pedformat)))
#                     # There is a potential issues with the alleles code -- there are two columns taken up by the allelotypes.  So, after we have the
#                     # column mapping done, we need to loop to move every column following the alleles over by one.  D'oh!
#                     try:
#                         _alleles = _pedformat.index('t')
#                     except ValueError:
#                         if debug:
#                             print(('[DEBUG]: No alleles code was specified in the pedigree format string %a.  This program will continue.' % (_pedformat)))
#                     try:
#                         _breed = _pedformat.index('r')
#                     except ValueError:
#                         if debug:
#                             print(('[DEBUG]: No breed code was specified in the pedigree format string %a.  This program will continue.' % (_pedformat)))
#                     try:
#                         _name = _pedformat.index('n')
#                     except ValueError:
#                         if debug:
#                             print(('[DEBUG]: No name code was specified in the pedigree format string %a.  This program will continue.' % (_pedformat)))
#                     try:
#                         _by_mmddyyyy = _pedformat.index('y')
#                     except ValueError:
#                         if debug:
#                             print(('[DEBUG]: No birth year (MM/DD/YYYY) code was specified in the pedigree format string %a.  This program will continue.' % (_pedformat)))
#                     try:
#                         _alive = _pedformat.index('l')
#                     except ValueError:
#                         if debug:
#                             print(('[DEBUG]: No alive/dead code was specified in the pedigree format string %a.  This program will continue.' % (_pedformat)))
#                     try:
#                         _age = _pedformat.index('e')
#                     except ValueError:
#                         if debug:
#                             print(('[DEBUG]: No age code was specified in the pedigree format string %a.  This program will continue.' % (_pedformat)))
#                 ###
#                 ### PUT SOME CODE HERE TO DEAL WITH MOVING POST-ALLELE COLUMNS OVER!!!
#                 ### This may be harder than I thought, but we are landing now...how
#                 ### about a dictionary to map variable types to columns?
#                 ###
#                 try:
#                     if _alleles:
#                         pass
#                 except NameError:
#                     pass
#                 if critical_count > 0:
#                     sys.exit(0)
#                 else:
#                     ###
#                     ### Put code here to instantiate a new Animal() object.
#                     ###
#                     #elif pedformat == 'asdxbf':
#                     #    an = Animal(l[0],l[1],l[2],sex=l[3],by=l[4],fa=l[5])

#                     # NOTE: we have an odd situation where animals may appear in both unknown and known
#                     # [sex] lists b/c the sex of sires and dams is inferred from their location in the
#                     # animal record.  Base animals without sex codes are assigned a sex of 'u' (unknown)
#                     # by default if no code is included in the pedigree file.  When those parents appear
#                     # later as parents, they will be placed in the appropriate list.  The program does
#                     # remove animals from the UNKNOWN list once they are placed in a sex-specific list.
#                     #
#                     # There is a problem with the current implementation here.  An "if animal in list"
#                     # statement is used, which is fine for small pedigrees.  It degrades very badly for
#                     # large pedigrees.  Hm...maybe a dictionary?  Dictionaries are insanely faster.  The
#                     # right tool...
#                     #
#                     # Do not insert duplicate males into the MALES list
#                     try:
#                         _i =  males[an.sireID]
#                     except KeyError:
#                         males[an.sireID] = an.sireID
#                     # Do not insert duplicate females into the FEMALES list
#                     try:
#                         _i =  females[an.damID]
#                     except KeyError:
#                         females[an.damID] = an.damID
#                     # Check the sex code to see which list an animal should be placed in
#                     # 'M' or 'm' codes for males
#                     if an.sex == 'M' or an.sex == 'm':
#                         try:
#                             _i =  males[an.animalID]
#                         except KeyError:
#                             males[an.animalID] = an.animalID
#                     # 'F' or 'f' codes for females
#                     elif an.sex == 'F' or an.sex == 'f':
#                         try:
#                             _i =  females[an.animalID]
#                         except KeyError:
#                             females[an.animalID] = an.animalID
#                     # Any other character is treated as unknown
#                     else:
#                         unknowns[an.animalID] = an.animalID
#                     # Make sure that sires are not also coded as dams
#                     try:
#                         _i = females[an.sireID]
#                         if _i != 0 and _i != '0':
#                             print(('[ERROR]: Animal %s is coded as a sire (male) for some animal records, but as a dam (female) for other animal records (check record %s - animal ID %s)' % (an.sireID,animalCounter,an.animalID)))
#                             break
#                     except:
#                         pass
#                     # Make sure that dams are not also coded as sires
#                     try:
#                         _i = males[an.damID]
#                         if _i != 0 and _i != '0':
#                             print(('[ERROR]: Animal %s is coded as a dam (female) for some animal records, but as a sire (male) for other animal records (check record %s - animal ID %s)' % (an.damID,animalCounter,an.animalID)))
#                             break
#                     except:
#                         pass

#                 # Infers the sex of an animal with unknown gender based on whether or not they later appear as a sire
#                 # or a dam in the pedigree file.
#                 try:
#                     _i = unknowns[an.sireID]
#                     del unknowns[an.sireID]
#                 except KeyError:
#                     pass
#                 try:
#                     _i = unknowns[an.damID]
#                     del unknowns[an.damID]
#                 except KeyError:
#                     pass

#                 # Suppose that base animals are not given an individual entry in the
#                 # pedigree file...it is necessary to catch that case and add an animal
#                 # object to the list for them.
#                 # First for sires...
#                 try:
#                     _i = _animals[an.sireID]
#                 except KeyError:
#                     if int(an.sireID) != 0:
#                         _an = Animal(an.sireID,'0','0')
#                         _animals[an.sireID] = an.sireID
#                         animals.append(_an)
#                 # ...and then for dams
#                 try:
#                     _i = _animals[an.damID]
#                 except KeyError:
#                     if int(an.damID) != 0:
#                         _an = Animal(an.damID,'0','0')
#                         _animals[an.damID] = an.damID
#                         animals.append(_an)
#                 animals.append(an)
#                 _animals[an.animalID] = an.animalID

#     # Make sure that known males have the proper sex code in their instance
#     for _m in males:
#         try:
#             if animals[int(_m)].sex == 'u':
#                 animals[int(_m)].sex = 'm'
#             # Add the animal's ID to the sire and dam's daughter lists
#             if animals[int(_m) - 1].sireID != 0 and animals[int(_m) - 1].animalID != 0:
#                 try:
#                     _md = animals[int(animals[int(_m) - 1].sireID) - 1].sons[_m]
#                 except KeyError:
#                     animals[int(animals[int(_m) - 1].sireID) - 1].sons[_m] = _m
#             if animals[int(_m) - 1].damID != 0 and animals[int(_m) - 1].animalID != 0:
#                 try:
#                     _md = animals[int(animals[int(_m) - 1].damID) - 1].sons[_m]
#                 except KeyError:
#                     animals[int(animals[int(_m) - 1].damID) - 1].sons[_m] = _m
#         except:
#             pass
#     # Make sure that known females have the proper sex code in their instance
#     for _f in females:
#         try:
#             if animals[int(_f)].sex == 'u':
#                 animals[int(_f)].sex = 'f'
#             # Add the animal's ID to the sire and dam's daughter lists
#             if animals[int(_f) - 1].sireID != 0 and animals[int(_f) - 1].animalID != 0:
#                 try:
#                     _fd = animals[int(animals[int(_f) - 1].sireID) - 1].daus[_f]
#                 except KeyError:
#                     animals[int(animals[int(_f) - 1].sireID) - 1].daus[_f] = _f
#             if animals[int(_f) - 1].damID != 0 and animals[int(_f) - 1].animalID != 0:
#                 try:
#                     _fd = animals[int(animals[int(_f) - 1].damID) - 1].daus[_f]
#                 except KeyError:
#                     animals[int(animals[int(_f) - 1].damID) - 1].daus[_f] = _f
#         except:
#             pass

#     for _u in unknowns:
#         try:
#             if animals[int(_u) - 1].sireID != 0 and animals[int(_u) - 1].animalID != 0:
#                 try:
#                     _ud = animals[int(animals[int(_u) - 1].sireID) - 1].unks[_u]
#                 except KeyError:
#                     animals[int(animals[int(_u) - 1].sireID) - 1].unks[_u] = _u
#             if animals[int(_u) - 1].damID != 0 and animals[int(_u) - 1].animalID != 0:
#                 try:
#                     _ud = animals[int(animals[int(_u) - 1].damID) - 1].unks[_u]
#                 except KeyError:
#                     animals[int(animals[int(_u) - 1].damID) - 1].unks[_f] = _u
#         except:
#             pass

#     print(('[DEBUG]: males ', males))
#     print(('[DEBUG]: females ', females))
#     print(('[DEBUG]: unknowns ', unknowns))

#     infile.close()
#     if debug:
#         print(('[MESSAGE]: %s animal records read from pedigree file %s'  %(animalCounter,inputfile)))
#         print(('[MESSAGE]: %s animal records created from the pedigree file' % (len(animals))))
#         print(('[MESSAGE]: %s unique sires found in the pedigree file' % (len(males))))
#         print(('[MESSAGE]: %s unique dams found in the pedigree file' % (len(females))))
#         print(('[MESSAGE]: %s unique animals of unknown gender found in the pedigree file' % (len(unknowns))))
#         print('')
#     return animals







 
    
##
# pyp_nice_time() returns the current date and time formatted as, e.g.,
# Wed Mar 30 10:26:31 2005.
# @return A string containg the formatted date and time.
# @defreturn string
def pyp_nice_time():
    import time
    return time.asctime(time.localtime(time.time()))