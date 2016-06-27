"""
This program will return the hours of a public hearing in a .txt file, assuming that Hansard has used standard wordings naming committees.
This program will not work for a sub-committee.
"""
import datetime
import glob
import os
import re
import string
import sys
import PyPDF2

#iterates over files and calls helper functions.
def scraper(path):
    '''
    Iterates over all .doc, .txt, and .pdf files in the directory path.
    Calls helper functions to find duration, committee types and witness numbers.
    '''
    #dictionaries for recording statistics
    leg_cttee = {'hearings': 0, 'duration': 0, 'witnesses': 0};
    ref_cttee = {'hearings': 0, 'duration': 0, 'witnesses': 0};
    locations = {'ACT': 0, 'WA': 0, 'NT': 0, 'SA': 0, 'QLD': 0, 'NSW': 0, 'VIC': 0, 'TAS': 0}

    #gather relevant files from directory
    files = list ( set ( glob.glob (path+'/*.txt') + glob.glob (path+'/*.pdf') + glob.glob (path+'/*.doc*') ) )
    #print files

    for file in files:
        if file[-3:] == 'txt':
            print file
            print 'found txt'
        elif file[-3:] == 'pdf':
            print file
            print 'found pdf'
        elif file[-3:] == 'doc' or 'ocx':
            print file
            print 'found doc'
            word_to_txt(file)

def cttee_type(file):
    '''
    Takes a file of format .txt and identifies if the committee is legislation, reference, or sub-committee.
    Returns the type of committee as string.
    '''
    cttee = None;
    sub_cttee = False
    with open(file) as f:
        while cttee == None:
            for line in f:
                line = line.rstrip()
                #looks for lines that start with a capital C and include a time.
                if re.search('REFERENCES COMMITTEE', line):
                    cttee = 'References'
                    break
                elif re.search('LEGISLATION COMMITTEE', line):
                    cttee = 'Legislation';
                    break
                else:
                    continue
    return cttee

def hearing_location(path):
    '''
    Determines which state or territory the hearing was held in.
    Takes a path to a txt file.
    Returns a string with the state or territory.
    If the location wasn't in the dictionary of locations, the function will return a string of the location in city form.
    '''
    #Dictionary to convert hearing city to state.
    states = {'SYDNEY': 'NSW', 'NEWCASTLE': 'NSW', 'MELBOURNE': 'VIC', 'GEELONG': 'VIC', 'BENDIGO': 'VIC', 'CANBERRA': 'ACT', 'ADELAIDE': 'SA', 'PERTH': 'WA', 'HOBART': 'TAS', 'DARWIN': 'NT'}
    location = None;
    start = False;
    retString = None;
    with open(path) as f:
        for line in f:
            line = line.rstrip();
            line = line.lstrip();
            #looks for a line that commences with one or more upper case letters followed by a comma, and ends with a number.
            #if the criteria are met witnesses are incremented. Based on how Hansard lays out the witness list.
            #loop breaks once hearing commences.
            if re.search('BY AUTHORITY OF', line):
                break
            if re.search('(?:MON|TUES|WEDNES|THURS|FRI)DAY', line):
                start = True
                continue
            if start:
                if re.search('[A-Z]+?', line):
                    location = line
                    break
    try:
        retString = states[location];
    except KeyError:
        retString = '{} unable to be assigned to State/Territory. \n Please manually add location to relevant state tally. \n Please inform administrator so program can be updated.'.format(location)
    return retString

# files = ['030816.txt', '060115.txt', '070715.txt'] #~134 witnesses at estimates
# def test_location(paths):
#     for f in paths:
#         location = hearing_location(f)
#         print 'file: {} \n{}'.format(f, location)
#         print '\n'
# test_location(files)

def witness_count(path):
    '''
    Takes a file of format .txt and counts the number of witnesses at a public hearing and returns an int.
    '''
    witnesses = 0
    witness_list = []
    print path
    with open(path) as f:
        for line in f:
            line = line.rstrip();
            #looks for a line that commences with one or more upper case letters followed by a comma, and ends with a number.
            #if the criteria are met witnesses are incremented. Based on how Hansard lays out the witness list.
            #loop breaks once hearing commences.
            if re.search('Committee.+[0-9][0-9]:[0-9][0-9]', line):
                break
            if re.search('(?:M|D)(r|rs|iss|s)\s[A-Z].+,', line):
                temp = line[0:20]
                if temp not in witness_list:
                    witness_list.append(temp)
                    witnesses += 1;
                # print 'line: {}'.format(line)
                # print 'temp: {}'.format(temp)
    return witnesses

#consider each text file in directory and print start, finish and suspension times.
def hearing_duration(path):
    '''
    Takes a path and iterates over the files in that folder ending in .txt.
    Function returns a string indicating how much time the hearing in the relevant folder ran for.
    '''
    for file in glob.glob((path+'/*.txt')):
        times = []
        with open(file) as f:
            for line in f:
                line = line.rstrip()
                #looks for lines that start with a capital C and include a time.
                if re.search('Committee.+[0-9][0-9]:[0-9][0-9]', line):
                    times.append(line)
                #looks for lines that start with a capital P and include a time.
                if re.search('Proceedings suspended.+[0-9][0-9]:[0-9][0-9]', line):
                    times.append(line)

            #extract times from lines and place into array.
            times_clean = []
            for line in times:
                temp = line.split()
                for i in temp:
                    if re.search('^[0-9].+?', i):
                        times_clean.append(i.translate(string.maketrans("",""), string.punctuation))
            #print times_clean      #degugging print statement

            #calculate durations
            try:
                assert True, len(times_clean) % 2 == 0
            except AssertionEror as e:
                raise 'An incorrect number of times were found, program cannot guarantee accuracy of reported times.'
            time_total = 0
            duration = []
            while len(times_clean) != 0:
                start = times_clean.pop(0)
                end = times_clean.pop(0)
                duration.append(datetime.timedelta(minutes=int(end[-2:]), hours=int(end[:2])) - datetime.timedelta(minutes=int(start[-2:]), hours=int(start[:2])))

            for i in duration:
                time_total += i.total_seconds()
            #convert the number of seconds into a user-readable format.
            m, s = divmod(time_total, 60)
            h, m = divmod(m, 60)
            out_time = '%d:%02d:%02d' % (h, m, s)

            #return duration
            return 'Hearing {} ran for {}.'.format(file, out_time)

def word_to_txt(path):
    '''
    Takes a doc file path (/*/*/.../*.doc) and converts to a txt file
    returns a path to the newly created txt file (/*/*/.../*.txt)
    # '''
    temp_string = path.split('.');
    inputDirectory = temp_string[0];
    cmd = 'unoconv -f  txt ' + path
    os.system(cmd)
    newpath = inputDirectory + '.txt'
    #print '{} converted to {}.'.format(path, newpath)
    return newpath

def hansard_page_count(files):
    '''
    takes list of files and returns an integer sum of the number of pages.
    '''
    pages = 0
    for in_file in files:
        inputFile = PyPDF2.PdfFileReader(in_file)
        pages += inputFile.getNumPages()
        pages -= 4 #taking into account the leading pages in Hansard pdfs.

    return pages

def count_subs(files):
    '''
    Input: Takes a list of .pdf files' paths
    Returns: a tuple (number of submissions, number of pages)
    Attachments are counted as page numbers, but not in the submission count.
    '''
    countedSubs = [] #array to hold titles, if an attachment has the same number the count won't be incremented
    pages = 0
    for sub in files:
        #extract the file name from the directory root
        directory = sub.split('/')
        file_name = directory[-1]
        #print file_name
        re_sub = re.compile('\d+')
        submission_num = re_sub.findall(file_name)

        if len(submission_num)  >  0:                  #check a valid number was found
            index = int(submission_num[0])         #cast to integer
            if index not in countedSubs:
                countedSubs.append(index)

        #count pages
        try:
            inputFile = PyPDF2.PdfFileReader(sub)
            pages += inputFile.getNumPages()
        except:
            print "Unable to process {}".format(sub)
            continue
    return (len(countedSubs), pages,)

def get_files():
    '''
    Helper function for testing.
    Set path below to gather files for use elsewhere.
    '''
    files = glob.glob ('/home/jarrod/workspace/senstats/*.pdf')
    #print files
    return files

print count_subs(get_files())
#scraper(sys.argv[1])
