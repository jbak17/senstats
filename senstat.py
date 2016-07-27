#!/usr/bin/python
"""
This program will return the hours of a public hearing in a .txt file, assuming that Hansard has used standard wordings naming committees.
This program will not work for a sub-committee.
"""
import glob
import os
import re
import string
import subprocess
import sys
import PyPDF2
from pdf_to_txt import convert_pdf_to_txt
import classes
from itertools import chain

#iterates over files and calls helper functions.
def hearings(input_path, cttee_type):
    '''
    cttee_type is an integer: 1 leg, 2 ref, 3 both.
    input_path is a string to a folder containing Hansards.
    Returns...
    '''
    #dictionaries for recording statistics
    locations = {'ACT': 0, 'WA': 0, 'NT': 0, 'SA': 0, 'QLD': 0, 'NSW': 0, 'VIC': 0, 'TAS': 0}
    leg_cttee = {'type': 'Legislation', 'hearings': 0, 'duration': 0, 'witnesses': 0, 'locations': locations.copy(), 'hansard': 0 };
    ref_cttee = {'type': 'References', 'hearings': 0, 'duration': 0, 'witnesses': 0, 'locations': locations.copy(), 'hansard': 0 };
    #create objects holding functions to work with inputs
    printer = classes.Outstrings()
    cleaner = classes.Janitor()

    files = collect_files(input_path)
    print 'The following files were found: {}'.format(files)

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

    #clean up .txt files created
    cleaner.delete_txt(input_path)
    print 'Gathering results from hearings()...'
    outString = None
    if cttee_type == 1:
        outString= printer.publicHearingOutString(leg_cttee)
    elif cttee_type == 2:
        outString = printer.publicHearingOutString(ref_cttee)
    else:
        outString = printer.publicHearingOutString(leg_cttee) + '\n' + printer.publicHearingOutString(ref_cttee)
    return outString

def path_builder(path, cttee_type, function):
    '''
    Takes an integer identifying type of committee from GUI.
    function must be 'hearings', 'private', or 'subs'
    Returns a list of files from the committee's hearing folder.
    '''
    assert function in ['hearings', 'private', 'subs']
    path_type = {'1': 'leg', '2': 'ref'}
    ct_toString = str(cttee_type)
    path_to_function = path + '/' + path_type[ct_toString] + '/' + function
    return path_to_function

def collect_files(path):
    '''
    Takes a string path and string function.
    returns a list of files for further processing.
    '''
    files = list ( set ( glob.glob (path + '/*.pdf') + glob.glob (path +'/*.docx') ) )
    print files
    return files

def pdf_reader(PDF_file):
    '''
    Reads a PDF Hansard file to extract hearing related statistics.
    Returns a tuple (Type, duration, pages, location, number of witnesses)
    '''
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
    '''
    Reads a .docx Hansard file to extract hearing related statistics.
    Returns a tuple (Type, duration, pages, location, number of witnesses)
    '''
    #objects to access utilities in classes.py
    wordTool = classes.WordTools(docx_file)
    txtTool = classes.TxtTools()

    ctteeType, pages, witnesses = wordTool.getType(), wordTool.getPages(), wordTool.getWitnesses()
    #convert file to text to extract duration and location
    nf = wordTool.word_to_txt(docx_file, 'txt')
    duration = txtTool.hearing_duration(nf)
    location = txtTool.hearing_location(nf)

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

def main(path, cttee, function, submissions = False, output = 1):
    '''
    Main function for senstat. Controls input from the GUI.
    Path is a string to a directory in the proscribed format.
    Cttee is an int describing leg (1), ref (2) or both (3).
    Function is a tuple (hearing, private, submission). 1 is a request, 0 is ignore.
    Output is either to the screen (1) or to a file (2). Output is yet to be implemented. Do not change default until implementation complete!
    '''
    stringifier = classes.Outstrings()
    if output ==1: #print to screen.
        outStrings = ''
        if function[0] == 1: #hearing request
            print 'Public hearing request received. \n Committee type = {}'.format(cttee)
            if cttee == 1 or cttee == 2:#not both
                hearing_path = path_builder(path, cttee, 'hearings')
                outStrings += hearings(hearing_path, cttee)
            # elif cttee == 2:    #ref
            #     hearing_path = path_builder(path, cttee, 'hearings')
            #     #print hearing_path
            #     return hearings(hearing_path, cttee)
            elif cttee == 3:    #both
                pass
            else:
                print 'Unknown committee identifying integer.'
        if function[1] == 1: #private meetings request
            pass
        if function[2] == 1: #submissions request
            subs = list(submissions)
            submissionReader = classes.SubmissionTools()
            data = submissionReader.count_subs(subs)
            print data
            subString = stringifier.submissionsOutString(data)
            outStrings += subString 
    return outStrings

if __name__ == '__main__':
    # hearings(sys.argv[1])
    print hearings('/home/jarrod/workspace/senstats/economics', 2)
