#!/usr/bin/python
"""
This program will return the hours of a public hearing in a .txt file, assuming that Hansard has used standard wordings naming committees.
This program will not work for a sub-committee.
"""
import datetime
import glob
import os
import re
import string
import subprocess
import sys
import PyPDF2
from pdf_to_txt import convert_pdf_to_txt
import outstrings
import zipfile
from bs4 import BeautifulSoup

#iterates over files and calls helper functions.
def hearings(path):
    '''
    Iterates over all .doc, .txt, and .pdf files in the directory path.
    Calls helper functions to find duration, committee types and witness numbers.
    '''
    #dictionaries for recording statistics
    locations = {'ACT': 0, 'WA': 0, 'NT': 0, 'SA': 0, 'QLD': 0, 'NSW': 0, 'VIC': 0, 'TAS': 0}
    leg_cttee = {'type': 'Legislation', 'hearings': 0, 'duration': 0, 'witnesses': 0, 'locations': locations.copy(), 'hansard': 0 };
    ref_cttee = {'type': 'References', 'hearings': 0, 'duration': 0, 'witnesses': 0, 'locations': locations.copy(), 'hansard': 0 };

    printer = outstrings.Outstrings() #create Outstrings ojbect with the functionality of different print outputs

    #gather relevant files from directory
    files = list ( set ( glob.glob (path+'/*.pdf') + glob.glob (path+'/*.docx') ) )

    for item in files:
        if item[-3:] == 'pdf':
            stats = pdf_reader(item)
        elif item[-3:] == 'ocx':
            stats = docx_reader(item) #returns tuple (ctteeType, duration, pages, location, witnesses)
        else:
            print 'Unable to identify file type of', item

        if stats[0] == 'Legislation':
            leg_cttee['hearings'] += 1
            leg_cttee['duration'] += stats[1]
            leg_cttee['hansard'] += stats[2]
            leg_cttee['locations'][stats[3]] += 1
            leg_cttee['witnesses'] += stats[4]
        else:
            ref_cttee['hearings'] += 1
            ref_cttee['duration'] += stats[1]
            ref_cttee['hansard'] += stats[2]
            ref_cttee['locations'][stats[3]] += 1
            ref_cttee['witnesses'] += stats[4]

    #print results
    printer.publicHearingOutString(leg_cttee)
    printer.publicHearingOutString(ref_cttee)

def pdf_reader(PDF_file):
    pages = hansard_page_count(PDF_file)
    #conver to PDF to collect remaining data.
    conv_to_txt(PDF_file)
    path = PDF_file[:-3] + 'txt'
    ctteeType = cttee_type(path)
    duration = hearing_duration(path)
    location = hearing_location(path)
    witnesses = witness_count(path)

    return (ctteeType, duration, pages, location, witnesses)

def docx_reader(docx_file):
    ctteeType, pages, witnesses = getPagesAndCtteeType(docx_file)
    duration = 0
    location = None

    nf = word_to_txt(docx_file, 'txt')
    duration = hearing_duration(nf)
    location = hearing_location(nf)

    return (ctteeType, duration, pages, location, witnesses)

def conv_to_txt(path):
    '''
    Converts all pdf and word documents to txt.
    Returns None.
    '''
    #convert all files to txt for later processing.
    if path[-3:] == 'pdf':
        try:
            newpath = path[:-3] + 'txt'
            fo = open(newpath, 'w');
            fo.write(convert_pdf_to_txt(path));
            fo.close();
            #print '{} was converted to txt.'.format(path)
            #print 'found pdf'
        except Exception as e:
            print 'Unable to convert %s to pdf'.format(path)
    elif path[-3:] == 'doc' or 'ocx':
        try:
            txtPath = path[:-4] + '.txt'
            fo = open(txtPath, 'w');
            fo.write(convert_pdf_to_txt(pdfPath));
            fo.close();
        except Exception as e:
            print 'Unable to convert %s to pdf'.format(path)
    else:
        print 'Unknown file type'
        print 'conv_to_txt function problem'
    return fo

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
                line = line.lower()
                #looks for lines that start with a capital C and include a time.
                if re.search('references committee', line):
                    cttee = 'References'
                    break
                elif re.search('legislation committee', line):
                    cttee = 'Legislation';
                    break
                else:
                    continue
    return cttee

def hearing_location(txt_file):
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
    with open(txt_file) as f:
        for line in f:
            line = line.rstrip();
            line = line.lstrip();
            line = line.upper()
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

def witness_count(path):
    '''
    Takes a file of format .txt and counts the number of witnesses at a public hearing and returns an int.
    '''
    witnesses = 0
    witness_list = []
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

def hearing_duration(path):
    '''
    Takes a path to a .txt file.
    Returns a string indicating how much time the hearing in the relevant folder ran for.
    '''
    times = []
    with open(path) as f:
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
        return time_total

def word_to_txt(path, export_format):
    '''
    Takes a doc file path (/*/*/.../*.doc) and converts to the designated file type
    Inputs are strings
    returns a path to the newly created  file (/*/*/.../*.export_format)
    # '''
    temp_string = path.split('.');
    inputDirectory = temp_string[0];
    cmd = 'unoconv -f  {} {}'.format(export_format, path)
    os.system(cmd)
    newpath = inputDirectory + '.' + export_format
    print '{} converted to {}.'.format(path, newpath)
    return newpath

def hansard_page_count(PDF_file):
    '''
    takes a pdf file and returns an integer sum of the number of pages.
    '''
    pages = 0
    inputFile = PyPDF2.PdfFileReader(PDF_file)
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

def get_files(dir, type):
    '''
    Helper function to gather files.
    dir = directory path string
    Type = Takes a string of either 'doc', 'docx', 'txt' or 'pdf'
    Returns list of paths to those files.
    '''
    types = ['doc', 'docx', 'pdf', 'txt']
    assert type in types
    files = glob.glob ( dir + '/*.' + type)
    #print files
    return files

def getPagesAndCtteeType(path):
    '''
    Accepts the path to a docx file.
    Calculates the type of committee, number of pages of evidence and number of witnesses.
    Returns tuple with (cttee type, number of pages, number of witnesses)
    '''
    # open zipfile
    zf = zipfile.ZipFile(path)
    data = {'cttee_type' : None, 'pages' : 0, 'witnesses': 0}

    #get page numbers
    app = zf.read('docProps/app.xml')
    pages = re.findall('<Pages>[0-9]+<', app)
    try:
        pagestr = pages[0]
    except Exception as e:
        'Unable to establish number of pages for {}'.format(path)
    trans = string.maketrans("","")
    nodigs = trans.translate(trans, string.digits)
    outString = pagestr.translate(trans, nodigs)
    data['pages'] = int(outString) - 4 #subtract 4 to account for Hansard styling.

    #get cttee type
    custom = zf.read('docProps/custom.xml')
    app = zf.read('docProps/custom.xml')
    cttee = re.findall('(Legislation|References)', app)
    try:
        data['cttee_type'] = cttee[0]
    except:
        'Unable to establish committee type for {}'.format(path)

    #get number of witnesses. item4 contains data on witnesses.
    try:
        witnesses = zf.read('customXml/item4.xml')
        soup = BeautifulSoup(witnesses, 'lxml')
        witList = len(soup.find_all('t:name'))
        data['witnesses'] = witList
    except Exception as e:
        'Unable to establish number of witnesses for {}'.format(path)

    return (data['cttee_type'], data['pages'], data['witnesses'],)

if __name__ == '__main__':
    #print count_subs(get_files())
    # hearings(sys.argv[1])
    hearings('/home/jarrod/workspace/senstats/test_docs/activeTest')
