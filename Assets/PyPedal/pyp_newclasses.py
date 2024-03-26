#####
#NOTES: PETER BUSCHE
    # 1)Only 3 small change, each marked with PETERBUSCHE-changed
        # got rid of import statements: pyp_demog, pyp_io
        # commented out error with "PedigreeInputFileNameError"
        # changed file() to open()
####



##
# pyp_newclasses contains the new class structure that will be a part of PyPedal 2.0.0Final.
# It includes a master class to which most of the computational routines will be bound as
# methods, a NewAnimal() class, and a PedigreeMetadata() class.
##

import logging
import numpy
import os
import string
import sys


# Import the other pieces of PyPedal.  This will probably go away as most of these are rolled into
# NewPedigree as methods.
# import pyp_demog          #NO FUNCTIONS FROM THIS IMPORT ARE EVER USED
# import pyp_io             #NO FUNCTIONS FROM THIS IMPORT ARE EVER USED
from Assets.PyPedal import pyp_metrics
from Assets.PyPedal import pyp_nrm
from Assets.PyPedal import pyp_utils

##
# The NewPedigree class is the main data structure for PyP 2.0.0Final.
class NewPedigree:
    def __init__(self,kw):
        """Initialize a new Pedigree."""
        # Handle the Main Keywords.
        # if 'pedfile' not in kw: raise PedigreeInputFileNameError      #PETERBUSCHE-changed
        if 'pedformat' not in kw: kw['pedformat'] = 'asd'
        if 'pedname' not in kw: kw['pedname'] = 'Untitled'
        if 'messages' not in kw: kw['messages'] = 'verbose'
        if 'renumber' not in kw: kw['renumber'] = 0
        if 'pedigree_is_renumbered' not in kw: kw['pedigree_is_renumbered'] = 0
        if 'set_generations' not in kw: kw['set_generations'] = 0
        if 'set_ancestors' not in kw: kw['set_ancestors'] = 0
        if 'set_alleles' not in kw: kw['set_alleles'] = 0
        if 'sepchar' not in kw: kw['sepchar'] = ' '
        if 'alleles_sepchar' not in kw: kw['alleles_sepchar'] = '/'
        if 'counter' not in kw: kw['counter'] = 1000
        if 'slow_reorder' not in kw: kw['slow_reorder'] = 1
        if 'missing_parent' not in kw: kw['missing_parent'] = '0'
        kw['filetag'] = string.split(kw['pedfile'],'.')[0]
        if len(kw['filetag']) == 0:
            kw['filetag'] = 'untitled_pedigree'
        self.kw = kw

        # Initialize the Big Main Data Structures to null values
        self.pedigree = []                         # We may start storing animals in a dictionary rather than in a list.  Maybe,
        self.metadata = {}                         # Metadata will also be stored in a dictionary.
        self.idmap = {}                            # Used to map between original and renumbered IDs.
        self.backmap = {}                          # Used to map between renumbered and original IDs.
        # Maybe these will go in a configuration file later
        self.starline = '*'*80
        # Start logging!
        if 'logfile' not in self.kw: self.kw['logfile'] = '%s.log' % ( self.kw['filetag'] )
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
            filename=self.kw['logfile'],
            filemode='w')
        logging.info('Logfile %s instantiated.',self.kw['logfile'])
        
    ##
    # load() wraps several processes useful for loading and preparing a pedigree for use in an
    # analysis, including reading the animals into a list of animal objects, forming lists of sires and dams,
    # checking for common errors, setting ancestor flags, and renumbering the pedigree.
    # @param renum Flag to indicate whether or not the pedigree is to be renumbered.
    # @param alleles Flag to indicate whether or not pyp_metrics/effective_founder_genomes() should be called for a single round to assign alleles.
    # @return None
    # @defreturn None
    def load(self):
        logging.info('Preprocessing %s',self.kw['pedfile'])
        if self.kw['messages'] == 'verbose':
            print(('[INFO]: Preprocessing %s' % (self.kw['pedfile'])))
        self.preprocess()
        if self.kw['renumber'] == 1:
            self.renumber()
        if self.kw['set_generations']:
            logging.info('Assigning generations')
            if self.kw['messages'] == 'verbose':
               print(('\t[INFO]: Assigning generations at %s' % ( pyp_utils.pyp_nice_time() )))
            self.pedigree = pyp_utils.set_generation(self.pedigree)
        if self.kw['set_ancestors']:
            logging.info('Setting ancestor flags')
            if self.kw['messages'] == 'verbose':
                print(('\t[INFO]: Setting ancestor flags at %s' % ( pyp_utils.pyp_nice_time() )))
            self.pedigree = pyp_utils.set_ancestor_flag(self.pedigree)
        if self.kw['set_alleles']:
            logging.info('Gene dropping to compute founder genome equivalents')
            if self.messages == 'verbose':
                print(('\t[INFO]: Gene dropping at %s' % ( pyp_utils.pyp_nice_time() )))
            pyp_metrics.effective_founder_genomes(self.pedigree)
        if not self.kw['renumber']:
            logging.info('Assigning offspring')
            pyp_utils.assign_offspring(self.pedigree)
            logging.info('Creating pedigree metadata object')
        if self.kw['messages'] == 'verbose':
            print('[INFO]: Creating pedigree metadata object')
        self.metadata = PedigreeMetadata(self.pedigree,self.kw)
        self.metadata.printme()

    ##
    # save() writes a PyPedal pedigree to a user-specified file.  The saved pedigree includes
    # all fields recognized by PyPedal, not just the original fields read from the input pedigree
    # file.
    # @param filename The file to which the pedigree should be written.
    # @param outformat The format in which the pedigree should be written: 'o' for original (as read) and 'l' for long version (all available variables).
    # @param idformat Write 'o' (original) or 'r' (renumbered) animal, sire, and dam IDs.
    # @return A save status indicator (0: failed, 1: success)
    # @defreturn integer
    def save(self,filename='',outformat='o',idformat='o'):
        #
        # This is VERY important: never overwrite the user's data if it looks like an accidental
        # request!  If the user does not pass a filename to save() save the pedigree to a file
        # whose name is derived from, but not the same as, the original pedigree file.
        #
        if filename == '':
            filename = '%s_saved.ped' % ( self.kw['filetag'] )
            if self.kw['messages'] == 'verbose':
                print(('[WARNING]: Saving pedigree to file %s to avoid overwriting %s.' % ( filename, self.kw['pedfile'] )))
            logging.warning('Saving pedigree to file %s to avoid overwriting %s.',filename,self.kw['pedfile'])
        try:
            ofh = open(filename,'w')        #PETERBUSCHE-changed
            if self.kw['messages'] == 'verbose':
                print(('[INFO]: Opened file %s for pedigree save at %s.' % ( filename, pyp_utils.pyp_nice_time() )))
            logging.info('Opened file %s for pedigree save at %s.',filename, pyp_utils.pyp_nice_time())
            
            if outformat == 'l':
                # We have to form the new pedformat.
                _newpedformat = 'asdgx'
                if 'y' in self.kw['pedformat']:
                    _newpedformat = '%sy' % ( _newpedformat )
                else:
                    _newpedformat = '%sb' % ( _newpedformat )
                _newpedformat = '%sfrnle' % (_newpedformat )
            else:
                _newpedformat = self.kw['pedformat']
            
            # Write file header.
            ofh.write('# %s created by PyPedal at %s\n' % ( filename, pyp_utils.pyp_nice_time() ) )
            ofh.write('# Current pedigree metadata:\n')
            ofh.write('#\tpedigree file: %s\n' % (filename) )
            ofh.write('#\tpedigree name: %s\n' % (self.kw['pedname']) )
            ofh.write('#\tpedigree format: \'%s\'\n' % ( _newpedformat) )
            if idformat == 'o':
                ofh.write('#\tNOTE: Animal, sire, and dam IDs are RENUMBERED IDs, not original IDs!\n')
            ofh.write('# Original pedigree metadata:\n')
            ofh.write('#\tpedigree file: %s\n' % (self.kw['pedfile']) )
            ofh.write('#\tpedigree name: %s\n' % (self.kw['pedname']) )
            ofh.write('#\tpedigree format: %s\n' % (self.kw['pedformat']) )
            for _a in self.pedigree:
                if idformat == 'o':
                    _outstring = '%s %s %s' % \
                        (_a.originalID, self.pedigree[int(_a.sireID)-1].originalID, \
                        self.pedigree[int(_a.damID)-1].originalID )
                else:
                    _outstring = '%s %s %s' % (_a.animalID, _a.sireID, _a.damID )
                if 'g' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.gen )
                if 'x' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.sex )
                if 'y' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.bd )
                else:
                    _outstring = '%s %s' % ( _outstring, _a.by )
                if 'f' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.fa )
                if 'r' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.breed )
                if 'n' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.name )
                if 'l' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.alive )
                if 'e' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.age )
                ofh.write( '%s\n' % (_outstring) )
            ofh.close()
            if self.kw['messages'] == 'verbose':
                print(('[INFO]: Closed file %s after pedigree save at %s.' % ( filename, pyp_utils.pyp_nice_time() )))
            logging.info('Closed file %s after pedigree save at %s.',filename, pyp_utils.pyp_nice_time())
            return 1
        except:
            if self.kw['messages'] == 'verbose':
                print(('[ERROR]: Unable to open file %s for pedigree save!' % ( filename )))
            logging.error('Unable to open file %s for pedigree save.',filename)
            return 0

    ##
    # preprocess() processes a pedigree file, which includes reading the animals
    # into a list of animal objects, forming lists of sires and dams, and checking for
    # common errors.
    # @param None
    # @return None
    # @defreturn None
    def preprocess(self):
        """Preprocess a pedigree file, which includes reading the animals into a list, forming lists of sires and dams, and checking for common errors."""
        lineCounter = 0     # count the number of lines in the pedigree file
        animalCounter = 0   # count the number of animal records in the pedigree file
        pedformat_codes = ['a','s','d','g','x','b','f','r','n','y','l','e','A']
        critical_count = 0  # Number of critical errors encountered
        pedformat_locations = {} # Stores columns numbers for input data
        _sires = {}         # We need to track the sires and dams read from the pedigree
        _dams = {}          # file in order to insert records for any parents that do not
                            # have their own records in the pedigree file.
        # A variable, 'pedformat, is passed as a parameter that indicates the format of the
        # pedigree in the input file.  Note that A PERIGREE FORMAT STRING IS NO LONGER
        # REQUIRED in the input file, and any found will be ignored.  The index of the single-
        # digit code in the format string indicates the column in which the corresponding
        # variable is found.  Duplicate values in the pedformat atring are ignored.
        if not self.kw['pedformat']:
            self.kw['pedformat'] = 'asd'
            logging.error('Null pedigree format string assigned a default value.')
            if self.kw['messages'] == 'verbose':
                print('[ERROR]: Null pedigree format string assigned a default value.')
        # This is where we check the format string to figure out what we have in the input file.
        # Check for valid characters...
        _pedformat = []
        for _char in self.kw['pedformat']:
            if _char in pedformat_codes:
                _pedformat.append(_char)
            else:
                # Replace the invalid code with a period, which is ignored when the string is parsed.
                _pedformat.append('.')
                if self.kw['messages'] == 'verbose':
                    print(('[DEBUG]: Invalid format code, %s, encountered!' % (_char)))
                logging.error('Invalid column format code %s found while reading pedigree format string %s',_char,self.kw['pedformat'])
        for _char in _pedformat:
            try:
                pedformat_locations['animal'] = _pedformat.index('a')
            except ValueError:
                print(('[CRITICAL]: No animal identification code was specified in the pedigree format string %s!  This is a critical error and the program will halt.' % (_pedformat)))
                critical_count = critical_count + 1
            try:
                pedformat_locations['sire'] = _pedformat.index('s')
            except ValueError:
                print(('[CRITICAL]: No sire identification code was specified in the pedigree format string %s!  This is a critical error and the program will halt.' % (_pedformat)))
                critical_count = critical_count + 1
            try:
                pedformat_locations['dam'] = _pedformat.index('d')
            except ValueError:
                print(('[CRITICAL]: No dam identification code was specified in the pedigree format string %s!  This is a critical error and the program will halt.' % (_pedformat)))
                critical_count = critical_count + 1
            try:
                pedformat_locations['generation'] = _pedformat.index('g')
            except ValueError:
                pedformat_locations['generation'] = -999
                if self.kw['messages'] == 'all':
                    print(('[DEBUG]: No generation code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])))
            try:
                pedformat_locations['sex'] = _pedformat.index('x')
            except ValueError:
                pedformat_locations['sex'] = -999
                if self.kw['messages'] == 'all':
                    print(('[DEBUG]: No sex code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])))
            try:
                pedformat_locations['birthyear'] = _pedformat.index('b')
            except ValueError:
                pedformat_locations['birthyear'] = -999
                if self.kw['messages'] == 'all':
                    print(('[DEBUG]: No birth date (YYYY) code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])))
            try:
                pedformat_locations['inbreeding'] = _pedformat.index('f')
            except ValueError:
                pedformat_locations['inbreeding'] = -999
                if self.kw['messages'] == 'all':
                    print(('[DEBUG]: No coeffcient of inbreeding code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])))
            try:
                pedformat_locations['breed'] = _pedformat.index('r')
            except ValueError:
                pedformat_locations['breed'] = -999
                if self.kw['messages'] == 'all':
                    print(('[DEBUG]: No breed code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])))
            try:
                pedformat_locations['name'] = _pedformat.index('n')
            except ValueError:
                pedformat_locations['name'] = -999
                if self.kw['messages'] == 'all':
                    print(('[DEBUG]: No name code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])))
            try:
                pedformat_locations['birthdate'] = _pedformat.index('y')
            except ValueError:
                pedformat_locations['birthdate'] = -999
                if self.kw['messages'] == 'all':
                    print(('[DEBUG]: No birth date (MMDDYYYY) code was specified in the pedigree format string %s.  This program will continue.' % ( self.kw['pedformat'] )))
            try:
                pedformat_locations['alive'] = _pedformat.index('l')
            except ValueError:
                pedformat_locations['alive'] = -999
                if self.kw['messages'] == 'all':
                    print(('[DEBUG]: No alive/dead code was specified in the pedigree format string %s.  This program will continue.' % ( self.kw['pedformat'] )))
            try:
                pedformat_locations['age'] = _pedformat.index('e')
            except ValueError:
                    pedformat_locations['age'] = -999
                    if self.kw['messages'] == 'all':
                        print(('[DEBUG]: No age code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])))
            try:
                pedformat_locations['alleles'] = _pedformat.index('A')
            except ValueError:
                    pedformat_locations['alleles'] = -999
                    if self.kw['messages'] == 'all':
                        print(('[DEBUG]: No alleles code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])))
        if critical_count > 0:
            sys.exit(0)
        else:
            if self.kw['messages'] == 'verbose':
                print('[INFO]: Opening pedigree file')
            logging.info('Opening pedigree file')
            #infile = open(self.kw['pedfile'],'r')
            infile = self.kw['infile']
            while 1:
                line = infile.readline()
                if not line:
                    logging.warning('Reached end-of-line in %s after reading %s lines.', self.kw['pedfile'],lineCounter)
                    break
                else:
                    # 29 March 2005
                    # This causes problems b/c it eats the last column of the last record in a pedigree
                    # file.  I think I added it way back when to deal with some EOL-character annoyance,
                    # but I am not sure.  So...I am turning it off (for now).
                    #line = string.strip(line[:-1])
                    lineCounter = lineCounter + 1
                    if line[0] == '#':
                        logging.info('Pedigree comment (line %s): %s',lineCounter,string.strip(line))
                        pass
                    elif line[0] == '%':
                        self.kw['old_pedformat'] = string.strip(line[1:]) # this lets us specify the format of the pedigree file
                        logging.warning('Encountered deprecated pedigree format string (%s) on line %s of the pedigree file.',line,lineCounter)
                    # Thomas von Hassel sent me a pedigree whose last line was blank but for a tab.  In
                    # debugging that problem I realized that there was no check for null lines.  This 'elif'
                    # catches blank lines so that they are not treated as actuall records and logs them.
                    elif len(string.strip(line)) == 0:
                        logging.warning('Encountered an empty (blank) record on line %s of the pedigree file.',lineCounter)
                    else:
                        animalCounter = animalCounter + 1
                        if numpy.fmod(animalCounter,self.kw['counter']) == 0:
                            logging.info('Records read: %s ',animalCounter)
                        l = string.split(line,self.kw['sepchar'])
                        # Some people *cough* Brad Heins *cough* insist on sending me pedigree
                        # files vomited out by Excel, which pads cells in a column with spaces
                        # to right-align them...
                        for i in range(len(l)):
                            l[i] = string.strip(l[i])
                        if len(l) < 3:
                            errorString = 'The record on line %s of file %s is too short - all records must contain animal, sire, and dam ID numbers (%s fields detected).\n' % (lineCounter,self.kw['pedfile'],len(l))
                            print(('[ERROR]: %s' % (errorString)))
                            print(('[ERROR]: %s' % (line)))
                            sys.exit(0)
                        else:
                            an = NewAnimal(pedformat_locations,l,self.kw)
                            if int(an.sireID) != 0:
                                _sires[an.sireID] = an.sireID
                            if int(an.damID) != 0:
                                _dams[an.damID] = an.damID
                            self.pedigree.append(an)
                            self.idmap[an.animalID] = an.animalID
                            self.backmap[an.animalID] = an.animalID
            #
            # This is where we deal with parents with no pedigree file entry.
            #
            _null_locations = pedformat_locations
            for _n in list(_null_locations.keys()):
                _null_locations[_n] = -999
            _null_locations['animal'] = 0
            _null_locations['sire'] = 1
            _null_locations['dam'] = 2
#            print _null_locations
#            print 'INFO: _sires = %s' % (_sires)
#            print 'INFO: _dam = %s' % (_dams)
            for _s in list(_sires.keys()):
                try:
                    _i = self.idmap[_s]
                except KeyError:
                    an = NewAnimal(_null_locations,[_s,'0','0'],self.kw)
#                    an.printme()
                    self.pedigree.append(an)
                    self.idmap[an.animalID] = an.animalID
                    self.backmap[an.animalID] = an.animalID
                    logging.info('Added pedigree entry for sire %s' % (_s))
            for _d in list(_dams.keys()):
                try:
                    _i = self.idmap[_d]
                except KeyError:
                    an = NewAnimal(_null_locations,[_d,'0','0'],self.kw)
#                    an.printme()
                    self.pedigree.append(an)
                    self.idmap[an.animalID] = an.animalID
                    self.backmap[an.animalID] = an.animalID
                    logging.info('Added pedigree entry for dam %s' % (_d))
            #
            # Finish up.
            #
            logging.info('Closing pedigree file')
            infile.close()
            
    ##
    # renumber() updates the ID map after a pedigree has been renumbered so that all references
    # are to renumbered rather than original IDs.
    # @param None
    # @return None
    # @defreturn None
    def renumber(self):
        if self.kw['messages'] == 'verbose':
            print(('\t[INFO]: Renumbering pedigree at %s' % ( pyp_utils.pyp_nice_time() )))
            print(('\t\t[INFO]: Reordering pedigree at %s' % ( pyp_utils.pyp_nice_time() )))
        logging.info('Reordering pedigree')
        if 'b' in self.kw['pedformat'] or 'y' in self.kw['pedformat'] and not self.kw['slow_reorder']:
            self.pedigree = pyp_utils.fast_reorder(self.pedigree)
        else:
            self.pedigree = pyp_utils.reorder(self.pedigree)
        if self.kw['messages'] == 'verbose':
            print(('\t\t[INFO]: Renumbering at %s' % ( pyp_utils.pyp_nice_time() )))
        logging.info('Renumbering pedigree')
        self.pedigree = pyp_utils.renumber(self.pedigree)
        if self.kw['messages'] == 'verbose':
            print(('\t\t[INFO]: Updating ID map at %s' % ( pyp_utils.pyp_nice_time() )))
        logging.info('Updating ID map')
        self.updateidmap()
        if self.kw['messages'] == 'verbose':
            print(('\t[INFO]: Assigning offspring at %s' % ( pyp_utils.pyp_nice_time() )))
        logging.info('Assigning offspring')
        pyp_utils.assign_offspring(self.pedigree)
        self.kw['pedigree_is_renumbered'] = 1

    
    ##
    # updateidmap() updates the ID map after a pedigree has been renumbered so that all references
    # are to renumbered rather than original IDs.
    # @param None
    # @return None
    # @defreturn None
    def updateidmap(self):
        self.idmap = {}
        self.backmap = {}
        for _a in self.pedigree:
            try:
                self.idmap[_a.originalID] = _a.animalID
                self.backmap[_a.renumberedID] = _a.originalID
                #print '%s => %s' % ( _a.renumberedID, self.backmap[_a.renumberedID] )
            except KeyError:
                 pass
#         print self.idmap
#         print self.backmap

##
# The NewAnimal() class is holds animals records read from a pedigree file.
class NewAnimal:
    """A simple class to hold animals records read from a pedigree file."""
    ##
    # __init__() initializes a NewAnimal() object.
    # @param locations A dictionary containing the locations of variables in the input line.
    # @param data The line of input read from the pedigree file.
    # @return An instance of a NewAnimal() object populated with data
    # @defreturn object
    def __init__(self,locations,data,mykw):
        """Initialize an animal record."""
#         print locations
#         print data        
        if locations['animal'] != -999:
            self.animalID = string.strip(data[locations['animal']])
            self.originalID = string.strip(data[locations['animal']])
        if locations['sire'] != -999 and string.strip(data[locations['sire']]) != mykw['missing_parent']:
            self.sireID = string.strip(data[locations['sire']])
        else:
            self.sireID = '0'
        if locations['dam'] != -999 and string.strip(data[locations['dam']]) != mykw['missing_parent']:
            self.damID = string.strip(data[locations['dam']])
        else:
            self.damID = '0'
        if locations['generation'] != -999:
            self.gen = data[locations['generation']]
        else:
            self.gen = -999
        if locations['sex'] != -999:
            self.sex = string.strip(data[locations['sex']])
        else:
            self.sex = 'u'
        if locations['birthdate'] != -999:
            self.bd = string.strip(data[locations['birthdate']])
        else:
            self.bd = '01011900'
        if locations['birthyear'] != -999:
            self.by = int(string.strip(data[locations['birthyear']]))
            if self.by == 0:
                self.by = 1900
            #print self.animalID, self.by
            #print self.animalID, data
        elif locations['birthyear'] == -999 and locations['birthdate'] != -999:
            self.by = int(string.strip(data[locations['birthdate']]))
            self.by = self.by[:4]
        else:
#             if self.sireID == '0' and self.damID == '0':
#                 self.by = 1900
#             else:
#                 self.by = 1901
            self.by = 1900
        if locations['inbreeding'] != -999:
            self.fa = float(string.strip(data[locations['inbreeding']]))
        else:
            self.fa = 0.
        if locations['name'] != -999:
            self.name = string.strip(data[locations['name']])
        else:
            self.name = 'Unknown'
        if locations['breed'] != -999:
            self.breed = string.strip(data[locations['breed']])
        else:
            self.breed = 'Unknown'
        if locations['age'] != -999:
            self.age = int(string.strip(data[locations['age']]))
        else:
            self.age = -999
        if locations['alive'] != -999:
            self.alive = int(string.strip(data[locations['alive']]))
        else:
            self.alive = 0
        self.renumberedID = -999        
        self.igen = -999
        if self.sireID == '0' and self.damID == '0':
            self.founder = 'y'
        else:
            self.founder = 'n'
        self.paddedID = self.pad_id()
        #print self.animalID, self.paddedID
        self.ancestor = 0
        self.sons = {}
        self.daus = {}
        self.unks = {}
        # Assign alleles for use in gene-dropping runs.  Automatically assign two
        # distinct alleles to founders.
        if locations['alleles'] != -999:
            self.alleles = [string.split(data[locations['alleles']], self.kw['alleles_sepchar'])[0], \
                string.split(data[locations['alleles']],self.kw['alleles_sepchar'])[1]]
        else:
            if self.founder == 'y':
                _allele_1 = '%s%s' % (self.paddedID,'__1')
                _allele_2 = '%s%s' % (self.paddedID,'__2')
                self.alleles = [_allele_1,_allele_2]
            else:
                self.alleles = ['','']
        self.pedcomp = -999.9

    ##
    # printme() prints a summary of the data stored in the Animal() object.
    # @param self Reference to the current Animal() object
    def printme(self):
        """Print the contents of an animal record - used for debugging."""
        self.animalID = int(self.animalID)
        self.sireID = int(self.sireID)
        self.damID = int(self.damID)
        self.by = int(self.by)
        print(('ANIMAL %s RECORD' % (self.animalID)))
        print(('\tAnimal ID:\t%s' % (self.animalID)))
        print(('\tAnimal name:\t%s' % (self.name)))
        print(('\tSire ID:\t%s' % (self.sireID)))
        print(('\tDam ID:\t\t%s' % (self.damID)))
        print(('\tGeneration:\t%s' % (self.gen)))
        print(('\tInferred gen.:\t%s' % (self.igen)))
        print(('\tBirth Year:\t%s' % (self.by)))
        print(('\tSex:\t\t%s' % (self.sex)))
        print(('\tCoI (f_a):\t%s' % (self.fa)))
        print(('\tFounder:\t%s' % (self.founder)))
        print(('\tSons:\t\t%s' % (self.sons)))
        print(('\tDaughters:\t%s' % (self.daus)))
        print(('\tUnknowns:\t%s' % (self.unks)))
        print(('\tAncestor:\t%s' % (self.ancestor)))
        print(('\tAlleles:\t%s' % (self.alleles)))
        print(('\tOriginal ID:\t%s' % (self.originalID)))
        print(('\tRenumbered ID:\t%s' % (self.renumberedID)))
        print(('\tPedigree Comp.:\t%s' % (self.pedcomp)))
        print(('\tBreed:\t%s' % (self.breed)))
        print(('\tAge:\t%s' % (self.age)))
        print(('\tAlive:\t%s' % (self.alive)))
    ##
    # stringme() returns a summary of the data stored in the Animal() object
    # as a string.
    # @param self Reference to the current Animal() object
    def stringme(self):
        """Return the contents of an animal record as a string."""
        self.animalID = int(self.animalID)
        self.sireID = int(self.sireID)
        self.damID = int(self.damID)
        self.by = int(self.by)
        _me = ''
        _me = '%s%s' % ( _me, 'ANIMAL %s RECORD\n' % (self.animalID) )
        _me = '%s%s' % ( _me, '\tAnimal ID:\t%s\n' % (self.animalID) )
        _me = '%s%s' % ( _me, '\tAnimal name:\t%s\n' % (self.name) )
        _me = '%s%s' % ( _me, '\tSire ID:\t%s\n' % (self.sireID) )
        _me = '%s%s' % ( _me, '\tDam ID:\t\t%s\n' % (self.damID) )
        _me = '%s%s' % ( _me, '\tGeneration:\t%s\n' % (self.gen) )
        _me = '%s%s' % ( _me, '\tInferred gen.:\t%s\n' % (self.igen) )
        _me = '%s%s' % ( _me, '\tBirth Year:\t%s\n' % (self.by) )
        _me = '%s%s' % ( _me, '\tSex:\t\t%s\n' % (self.sex) )
        _me = '%s%s' % ( _me, '\tCoI (f_a):\t%s\n' % (self.fa) )
        _me = '%s%s' % ( _me, '\tFounder:\t%s\n' % (self.founder) )
        _me = '%s%s' % ( _me, '\tSons:\t\t%s\n' % (self.sons) )
        _me = '%s%s' % ( _me, '\tDaughters:\t%s\n' % (self.daus) )
        _me = '%s%s' % ( _me, '\tUnknowns:\t%s\n' % (self.unks) )
        _me = '%s%s' % ( _me, '\tAncestor:\t%s\n' % (self.ancestor) )
        _me = '%s%s' % ( _me, '\tAlleles:\t%s\n' % (self.alleles) )
        _me = '%s%s' % ( _me, '\tOriginal ID:\t%s\n' % (self.originalID) )
        _me = '%s%s' % ( _me, '\tRenumbered ID:\t%s\n' % (self.renumberedID) )
        _me = '%s%s' % ( _me, '\tPedigree Comp.:\t%s\n' % (self.pedcomp) )
        _me = '%s%s' % ( _me, '\tBreed:\t%s' % (self.breed) )
        _me = '%s%s' % ( _me, '\tAge:\t%s' % (self.age) )
        _me = '%s%s' % ( _me, '\tAlive:\t%s' % (self.alive) )
        return _me
    ##
    # trap() checks for common errors in Animal() objects
    # @param self Reference to the current Animal() object
    def trap(self):
        """Trap common errors in pedigree file entries."""
        if int(self.animalID) == int(self.sireID):
            print(('[ERROR]: Animal %s has an ID number equal to its sire\'s ID (sire ID %s).\n' % (self.animalID,self.sireID)))
        if int(self.animalID) == int(self.damID):
            print(('[ERROR]: Animal %s has an ID number equal to its dam\'s ID (dam ID %s).\n' % (self.animalID,self.damID)))
        if int(self.animalID) < int(self.sireID):
            print(('[ERROR]: Animal %s is older than its sire (sire ID %s).\n' % (self.animalID,self.sireID)))
        if int(self.animalID) < int(self.damID):
            print(('[ERROR]: Animal %s is older than its dam (dam ID %s).\n' % (self.animalID,self.damID)))
    ##
    # pad_id() takes an Animal ID, pads it to fifteen digits, and prepends the birthyear
    # (or 1950 if the birth year is unknown).  The order of elements is: birthyear, animalID,
    # count of zeros, zeros.
    # @param self Reference to the current Animal() object
    # @return A padded ID number that is supposed to be unique across animals
    # @defreturn integer
    def pad_id(self):
        """Take an Animal ID, pad it to fifteen digits, and prepend the birthyear (or 1900 if the birth year is unknown)"""
        l = len(self.animalID)
        pl = 15 - l - 1
        if pl > 0:
            zs = '0'*pl
            pid = '%s%s%s%s' % (self.by,zs,self.animalID,l)
        else:
            pid = '%s%s%s' % (self.by,self.animalID,l)
        return pid

##
# The PedigreeMetadata() class stores metadata about pedigrees.  Hopefully this will help improve performance in some procedures,
# as well as provide some useful summary data.
class PedigreeMetadata:
    """A class to hold metadata about pedigrees.  Hopefully this will help improve performance in some procedures, as well as
    provide some useful summary data."""
    ##
    # __init__() initializes a PedigreeMetadata object.
    # @param self Reference to the current Pedigree() object
    # @param myped A PyPedal pedigree.
    # @param kw A dictionary of options.
    # @return An instance of a Pedigree() object populated with data
    # @defreturn object
    def __init__(self,myped,kw):
        """Initialize a pedigree record."""
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Instantiating a new PedigreeMetadata() object...')
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Naming the Pedigree()...')
        self.name = kw['pedname']
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Assigning a filename...')
        self.filename = kw['pedfile']
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Attaching a pedigree...')
        self.myped = myped
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Setting the pedcode...')
        self.pedcode = kw['pedformat']
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Counting the number of animals in the pedigree...')
        self.num_records = len(self.myped)
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Counting and finding unique sires...')
        self.num_unique_sires, self.unique_sire_list = self.nus()
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Counting and finding unique dams...')
        self.num_unique_dams, self.unique_dam_list = self.nud()
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Setting renumber flag...')
        self.renumbered = kw['renumber']
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Counting and finding unique generations...')
        self.num_unique_gens, self.unique_gen_list = self.nug()
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Counting and finding unique birthyears...')
        self.num_unique_years, self.unique_year_list = self.nuy()
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Counting and finding unique founders...')
        self.num_unique_founders, self.unique_founder_list = self.nuf()
        if kw['messages'] == 'verbose':
            print('\t[INFO]:  Detaching pedigree...')
        self.myped = []
    ##
    # printme() prints a summary of the metadata stored in the Pedigree() object.
    # @param self Reference to the current Pedigree() object
    def printme(self):
        """Print the pedigree metadata."""
        print(('Metadata for  %s (%s)' % (self.name,self.filename)))
        print(('\tRecords:\t\t%s' % (self.num_records)))
        print(('\tUnique Sires:\t\t%s' % (self.num_unique_sires)))
        #print '\tSires:\t\t%s' % (self.unique_sire_list)
        print(('\tUnique Dams:\t\t%s' % (self.num_unique_dams)))
        #print '\tDams:\t\t%s' % (self.unique_dam_list)
        print(('\tUnique Gens:\t\t%s' % (self.num_unique_gens)))
        #print '\tGenerations:\t\t%s' % (self.unique_gen_list)
        print(('\tUnique Years:\t\t%s' % (self.num_unique_years)))
        #print '\tYear:\t\t%s' % (self.unique_year_list)
        print(('\tUnique Founders:\t%s' % (self.num_unique_founders)))
        #print '\tFounders:\t\t%s' % (self.unique_founder_list)
        print(('\tPedigree Code:\t\t%s' % (self.pedcode)))
    ##
    # stringme() returns a summary of the metadata stored in the pedigree as
    # a string.
    # @param self Reference to the current Pedigree() object
    def stringme(self):
        """Build a string from the pedigree metadata."""
        _me = ''
        _me = '%s%s' % ( _me, 'PEDIGREE %s (%s)\n' % (self.name,self.filename) )
        _me = '%s%s' % ( _me, '\tRecords:\t\t\t%s\n' % (self.num_records) )
        _me = '%s%s' % ( _me, '\tUnique Sires:\t\t%s\n' % (self.num_unique_sires) )
        _me = '%s%s' % ( _me, '\tUnique Dams:\t\t%s\n' % (self.num_unique_dams) )
        _me = '%s%s' % ( _me, '\tUnique Gens:\t\t%s\n' % (self.num_unique_gens) )
        _me = '%s%s' % ( _me, '\tUnique Years:\t\t%s\n' % (self.num_unique_years) )
        _me = '%s%s' % ( _me, '\tUnique Founders:\t%s\n' % (self.num_unique_founders) )
        _me = '%s%s' % ( _me, '\tPedigree Code:\t\t%s\n' % (self.pedcode) )
        return _me
    ##
    # fileme() writes the metada stored in the Pedigree() object to disc.
    # @param self Reference to the current Pedigree() object
    def fileme(self):
        """Save the pedigree metadata to a file."""
        outputfile = '%s%s%s' % (self.name,'_ped_metadata_','.dat')
        aout = open(outputfile,'w')
        line1 = 'PEDIGREE %s (%s)\n' % (self.name,self.filename)
        line2 = '\tRecords:\t%s\n' % (self.num_records)
        line3 = '\tUnique Sires:\t%s\n' % (self.num_unique_sires)
        line4 = '\tUnique Dams:\t%s\n' % (self.num_unique_dams)
        line5 = '\tPedigree Code:\t%s\n' % (self.pedcode)
        line6 = '\tUnique Founders:\t%s\n' % (self.num_unique_founders)
        line7 =  '\tUnique Gens:\t%s\n' % (self.num_unique_gens)
        line8 = '\tUnique Years:\t%s\n' % (self.num_unique_years)
        line9 = '='*80
        line10 = '\tUnique Sire List:\t%s\n' % (self.unique_sire_list)
        line11 = '\tUnique Dam List:\t%s\n' % (self.unique_dam_list)
        line12 = '\tUnique Gen List:\t%s\n' % (self.unique_gen_list)
        line13 = '\tUnique Year List:\t%s\n' % (self.unique_year_list)
        line14 = '\tUnique Founder List:\t%s\n' % (self.num_founder_list)
        aout.write(line1)
        aout.write(line2)
        aout.write(line3)
        aout.write(line4)
        aout.write(line5)
        aout.write(line6)
        aout.write(line7)
        aout.write(line8)
        aout.write(line9)
        aout.write(line10)
        aout.write(line11)
        aout.write(line12)
        aout.write(line13)
        aout.write(line14)
        aout.close()

    ##
    # nus() returns the number of unique sires in the pedigree along with a list of the sires
    # @param self Reference to the current Pedigree() object
    # @return The number of unique sires in the pedigree and a list of those sires
    # @defreturn integer-and-list
    def nus(self):
        """Count the number of unique sire IDs in the pedigree.  Returns an integer count and a Python list of the
        unique sire IDs."""
        siredict = {}
        for l in range(self.num_records):
            if int(self.myped[l].sireID) != 0:
                try:
                    _s = siredict[self.myped[l].sireID]
                except KeyError:
                    siredict[self.myped[l].sireID] = self.myped[l].sireID
        n = len(list(siredict.keys()))
        return n, list(siredict.keys())
    ##
    # nud() returns the number of unique dams in the pedigree along with a list of the dams
    # @param self Reference to the current Pedigree() object
    # @return The number of unique dams in the pedigree and a list of those dams
    # @defreturn integer-and-list
    def nud(self):
        """Count the number of unique dam IDs in the pedigree.  Returns an integer count and a Python list of the
        unique dam IDs."""
        damdict = {}
        for l in range(self.num_records):
            if int(self.myped[l].damID) != 0:
                try:
                    _d = damdict[self.myped[l].damID]
                except KeyError:
                    damdict[self.myped[l].damID] = self.myped[l].damID
        n = len(list(damdict.keys()))
        return n, list(damdict.keys())
    ##
    # nug() returns the number of unique generations in the pedigree along with a list of the generations
    # @param self Reference to the current Pedigree() object
    # @return The number of unique generations in the pedigree and a list of those generations
    # @defreturn integer-and-list
    def nug(self):
        """Count the number of unique generations in the pedigree.  Returns an integer count and a Python list of the
        unique generations."""
        gendict = {}
        for l in range(self.num_records):
            try:
                _g = gendict[self.myped[l].gen]
            except KeyError:
                gendict[self.myped[l].gen] = self.myped[l].gen
        n = len(list(gendict.keys()))
        return n, list(gendict.keys())
    ##
    # nuy() returns the number of unique birthyears in the pedigree along with a list of the birthyears
    # @param self Reference to the current Pedigree() object
    # @return The number of unique birthyears in the pedigree and a list of those birthyears
    # @defreturn integer-and-list
    def nuy(self):
        """Count the number of unique birth years in the pedigree.  Returns an integer count and a Python list of the
        unique birth years."""
        yeardict = {}
        for l in range(self.num_records):
            try:
                _y = yeardict[self.myped[l].by]
            except KeyError:
                yeardict[self.myped[l].by] = self.myped[l].by
        n = len(list(yeardict.keys()))
        return n, list(yeardict.keys())
    ##
    # nuf() returns the number of unique founders in the pedigree along with a list of the founders
    # @param self Reference to the current Pedigree() object
    # @return The number of unique founders in the pedigree and a list of those founders
    # @defreturn integer-and-list
    def nuf(self):
        """Count the number of unique founders in the pedigree."""
        founderdict = {}
        for l in range(self.num_records):
            if self.myped[l].founder == 'y':
                try:
                    _f = founderdict[self.myped[l].originalID]
                except KeyError:
                    founderdict[self.myped[l].originalID] = self.myped[l].originalID
        n = len(list(founderdict.keys()))
        return n, list(founderdict.keys())
        
##
# NewAMatrix provides an instance of a numerator relationship matrix as a numpy array of
# floats with some convenience methods.  The idea here is to provide a wrapper around a NRM
# so that it is easier to work with.  For large pedigrees it can take a long time to compute
# the elements of A, so there is real value in providing an easy way to save and retrieve a
# NRM once it has been formed.
class NewAMatrix:
    def __init__(self,kw):
        """Initialize a new numerator relationship matrix."""
        if 'messages' not in kw: kw['messages'] = 'verbose'
        self.kw = kw
        
    ##
    # fast_a_matrix() calls pyp_nrm/fast_a_matrix() to form a NRM from a pedigree.
    # @param pedigree The pedigree used to form the NRM.
    # @return A NRM on success, 0 on failure.
    # @defreturn integer
    def fast_a_matrix(self,pedigree):
        if self.kw['messages'] == 'verbose':
            print(('[INFO]: Forming A-matrix from pedigree at %s.' % ( pyp_utils.pyp_nice_time() )))
        logging.info('Forming A-matrix from pedigree')
        try:
            self.nrm = pyp_nrm.fast_a_matrix(pedigree)
            if self.kw['messages'] == 'verbose':
                print(('[INFO]: Formed A-matrix from pedigree at %s.' % ( pyp_utils.pyp_nice_time() )))
            logging.info('Formed A-matrix from pedigree')
        except:
            if self.kw['messages'] == 'verbose':
                print(('[ERROR]: Unable to form A-matrix from pedigree at %s.' % ( pyp_utils.pyp_nice_time() )))
            logging.error('Unable to form A-matrix from pedigree')
            return 0

    ##
    # fast_a_matrix_r() calls pyp_nrm/fast_a_matrix_r() to form a NRM from a pedigree.
    # @param pedigree The pedigree used to form the NRM.
    # @return A NRM on success, 0 on failure.
    # @defreturn integer
    def fast_a_matrix_r(self,pedigree):
        if self.kw['messages'] == 'verbose':
            print(('[INFO]: Forming A-matrix from pedigree at %s.' % ( pyp_utils.pyp_nice_time() )))
        logging.info('Forming A-matrix from pedigree')
        try:
            self.nrm = pyp_nrm.fast_a_matrix(pedigree)
            if self.kw['messages'] == 'verbose':
                print(('[INFO]: Formed A-matrix from pedigree at %s.' % ( pyp_utils.pyp_nice_time() )))
            logging.info('Formed A-matrix from pedigree')
        except:
            if self.kw['messages'] == 'verbose':
                print(('[ERROR]: Unable to form A-matrix from pedigree at %s.' % ( pyp_utils.pyp_nice_time() )))
            logging.error('Unable to form A-matrix from pedigree')
            return 0

    ##
    # load() uses the numpy Array Function "fromfile()" to load an array from a binary file.  If
    # the load is successful, self.nrm contains the matrix.
    # @param nrm_filename The file from which the matrix should be read.
    # @return A load status indicator (0: failed, 1: success).
    # @defreturn integer
    def load(self,nrm_filename):
        import math
        if self.kw['messages'] == 'verbose':
            print(('[INFO]: Loading A-matrix from file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )))
        logging.info('Loading A-matrix from file %s', nrm_filename)
        try:
            self.nrm = numpy.fromfile(nrm_filename,'Float64')
    #         print self.nrm.shape
    #         print self.nrm.shape[0]
    #         print int(math.sqrt(self.nrm.shape[0]))
            self.nrm = numpy.reshape( self.nrm, ( int(math.sqrt(self.nrm.shape[0])), int(math.sqrt(self.nrm.shape[0])) ) )
            if self.kw['messages'] == 'verbose':
                print(('[INFO]: A-matrix successfully loaded from file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )))
            logging.info('A-matrix successfully loaded from file %s', nrm_filename)
            return 1
        except:
            if self.kw['messages'] == 'verbose':
                print(('[ERROR]: Unable to load A-matrix from file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )))
            logging.error('Unable to load A-matrix from file %s', nrm_filename)
            return 0
        
    ##
    # save() uses the numpy method "tofile()" to save an array to a binary file.
    # @param nrm_filename The file to which the matrix should be written.
    # @return A save status indicator (0: failed, 1: success).
    # @defreturn integer
    def save(self,nrm_filename):
        if self.kw['messages'] == 'verbose':
            print(('[INFO]: Saving A-matrix to file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )))
        logging.info('Saving A-matrix to file %s', nrm_filename)
#         try:
        self.nrm.tofile(nrm_filename)
        if self.kw['messages'] == 'verbose':
            print(('[INFO]: A-matrix successfully saved to file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )))
        logging.info('A-matrix successfully saved to file %s', nrm_filename)
#             return 1
#         except:
#             if self.kw['messages'] == 'verbose':
#                 print '[ERROR]: Unable to save A-matrix to file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )
#             logging.error('Unable to save A-matrix to file %s', nrm_filename)
#             return 0
            
    ##
    # info() uses the info() method of numpy arrays to dump some information about the NRM.  This is
    # of use predominantly for debugging.
    # @param None
    # @return None
    # @defreturn None
    def info(self):
        try:
            self.nrm.info()
        except:
            pass