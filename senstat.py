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
import classes
import zipfile
from bs4 import BeautifulSoup
from itertools import chain

#iterates over files and calls helper functions.
def hearings(input_path, cttee_type):
    '''
    Iterates over all .doc, .txt, and .pdf files in the input path. cttee_type is an integer: 1 leg, 2 ref, 3 both.
    Calls helper functions to find duration, committee types and witness numbers.
    '''
    #dictionaries for recording statistics
    locations = {'ACT': 0, 'WA': 0, 'NT': 0, 'SA': 0, 'QLD': 0, 'NSW': 0, 'VIC': 0, 'TAS': 0}
    leg_cttee = {'type': 'Legislation', 'hearings': 0, 'duration': 0, 'witnesses': 0, 'locations': locations.copy(), 'hansard': 0 };
    ref_cttee = {'type': 'References', 'hearings': 0, 'duration': 0, 'witnesses': 0, 'locations': locations.copy(), 'hansard': 0 };
    #create objects holding functions to work with inputs
    printer = classes.Outstrings()

    files = collect_files(input_path, cttee_type)

    for item in files:
        if item[-3:] == 'pdf':
            print item
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
    if cttee_type == 1:
        return printer.publicHearingOutString(leg_cttee)
    elif cttee_type == 2:
        return printer.publicHearingOutString(ref_cttee)
    else:
        return printer.publicHearingOutString(leg_cttee) + '\n' + printer.publicHearingOutString(ref_cttee)

def path_builder(path, cttee_type):
    '''
    Takes an integer identifying type of committee from GUI.
    Returns a list of files from the committee's hearing folder.
    '''
    path_type = {'1': 'leg', '2': 'ref'}
    ct_toString = str(cttee_type)
    path_to_hearings = path + '/' + path_type[ct_toString] + '/' + 'hearings'
    #print path_to_hearings
    files = list ( set ( glob.glob (path_to_hearings + '/*.pdf') + glob.glob (path_to_hearings+'/*.docx') ) )
    return files

def collect_files(path, cttee_type, function = None):
    '''
    Takes a string path and int cttee type and returns a list of files for further processing.
    '''
    files = []
    cttee_type = cttee_type
    #gather relevant files from directory
    #if only one committee is required request path_builder() to return a list of files for that committee. If both committees are required call path_builder for each.
    if cttee_type == 1 or cttee_type == 2:
        files.append(path_builder(path, cttee_type))
    else:
        files.append(path_builder(path, 1))
        files.append(path_builder(path, 2))
    #flatten file list to ensure items are strings rather than lists.
    files = list(chain.from_iterable(files))
    print files
    return files

def pdf_reader(PDF_file):
    #create objects to work with input file
    pdfTool = classes.PDFTools()
    converter = classes.Converter()
    txtTools = classes.TxtTools()

    pages = pdfTool.hansard_page_count(PDF_file)
    #conver to PDF to collect remaining data.
    converter.conv_to_txt(PDF_file)
    path = PDF_file[:-3] + 'txt'
    ctteeType = txtTools.cttee_type(path)
    duration = txtTools.hearing_duration(path)
    location = txtTools.hearing_location(path)
    witnesses = txtTools.witness_count(path)

    return (ctteeType, duration, pages, location, witnesses)

def docx_reader(docx_file):
    wordTool = classes.WordTools()
    ctteeType, pages, witnesses = getPagesAndCtteeType(docx_file)
    duration = 0
    location = None

    nf = word_to_txt(docx_file, 'txt')
    duration = hearing_duration(nf)
    location = hearing_location(nf)

    return (ctteeType, duration, pages, location, witnesses)

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

#txt file tools
#word file tools
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

#PDF file tools
def hansard_page_count(PDF_file):
    '''
    takes a pdf file and returns an integer sum of the number of pages.
    '''
    pages = 0
    inputFile = PyPDF2.PdfFileReader(PDF_file)
    pages += inputFile.getNumPages()
    pages -= 4 #taking into account the leading pages in Hansard pdfs.
    return pages


#main
def main(path, cttee, function, output = 1):
    '''
    Main function for senstat. Controls input from the GUI.
    Path is a string to a directory in the proscribed format.
    Cttee is an int describing leg (1), ref (2) or both (3).
    Function is a tuple (hearing, private, submission). 1 is a request, 0 is ignore.
    Output is either to the screen (1) or to a file (2). Output is yet to be implemented. Do not change default until implementation complete!
    '''
    pass
    if output ==1: #print to screen.
        outString = ''
        if function[1] == 1: #hearing request
            pass
        if output == 2: #private meetings request
            pass
        if output == 3: #submissions request
            pass
        return outString


if __name__ == '__main__':
    # hearings(sys.argv[1])
    print hearings('/home/jarrod/workspace/senstats/economics', 2)
