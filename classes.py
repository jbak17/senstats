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

class Outstrings(object):
    """
    Module contains a list of functions to format strings for different senate stat purposes
    """
    def __init__(self):
        pass

    def publicHearingOutString(self, cttee_dictionary):
        '''
        Takes a dictionary and returns a string with:
            -number of meetings by state
            -number of witnesses
            -durations of hearings
        '''
        #cttee_type
        ct = 'Senate {} Committee'.format(cttee_dictionary['type'])
        ln = '='*15
        br = '\n'
        #hearings
        hearing = 'There were  {}  hearings'.format(cttee_dictionary['hearings'])
        #states
        state = cttee_dictionary['locations']
        #duration
        time = self.time_to_str(cttee_dictionary['duration'])
        timeout= 'The total duration of these hearings was  {}'.format(time)

        #witnesses
        wit = '{}  people appeared before the committee as witnesses'.format(cttee_dictionary['witnesses'])
        #hansard pages
        pg = '{}  pages of evidence were gathered in Hansard'.format(cttee_dictionary['hansard'])
        return ct + br + ln + br + hearing + br + str(state) + br + timeout + br + wit + br + pg + br + ln

    def time_to_str(self, seconds):
        '''
        convert the number of seconds into a user-readable format.
        Takes number of seconds
        Returns human readable string in HH:MM:SS
        '''
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        out_time = '%d:%02d:%02d' % (h, m, s)
        #return duration
        return out_time

    def submissionsOutString(self, arg):
        '''
        Takes a tuple of number of submissions and number of page and returns string
        '''
        pass

    # locations = {'ACT': 0, 'WA': 1, 'NT': 0, 'SA': 0, 'QLD': 2, 'NSW': 0, 'VIC': 0, 'TAS': 0}
    # leg_cttee = {'type': 'Legislation', 'hearings': 0, 'duration': 1, 'witnesses': 23, 'locations': locations.copy(), 'hansard': 200 };
    # publicHearingOutString(leg_cttee)

class Converter(object):
    '''
    Class to hold all the converter functions for senstats
    '''
    def __init__(self):
        pass

    def conv_to_txt(self, path):
        '''
        Converts all pdf and word documents to txt.
        Returns new path to converted object.
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
                return newpath
            except Exception as e:
                print 'Unable to convert %s to pdf'.format(path)

        elif path[-3:] == 'doc' or 'ocx':
            try:
                self.wordtoPDFtoTxt(path)   #this will create a pdf and a txt copy of the file in the directory.
                newpath = path[:-3] + 'txt'
                return newpath
            except Exception as e:
                print 'Unable to convert %s to pdf'.format(path)

    def conv_from_word(self, path, export_format):
        '''
        Takes a doc file path (/*/*/.../*.doc) and converts to the designated file type
        Inputs are strings
        returns a path to the newly created  file (/*/*/.../*.export_format)
        # '''
        try:
            temp_string = path.split('.');
            inputDirectory = temp_string[0]; #gets directory
            cmd = 'unoconv -f  {} {}'.format(export_format, path)
            os.system(cmd)
            newpath = inputDirectory + export_format
            #print '{} converted to {}.'.format(path, newpath)
            return newpath
        except Exception as e:
            print 'Unable to convert %s to %s'.format(path, export_format)

    def buildPath(self, path, new_extension):
        temp_string = path.split('.');
        inputDirectory = temp_string[0]; #gets directory
        newpath = inputDirectory + '.' + new_extension;
        return newpath

    def wordtoPDFtoTxt(self, path):
        '''
        converts a word document to pdf and then into txt
        returns a path to the txt file
        '''
        pdf = self.conv_from_word(path, 'pdf')
        newpath = buildPath(path, 'txt')
        fo = open(newpath, 'w');
        fo.write(convert_pdf_to_txt(pdf));
        fo.close();
        return newpath

class WordTools(object):
    '''
    Holds tools for working on .docx documents.
    Has the following functions:
        Convert .docx to .txt
        Extract page numbers from .docx
        Extract committee type from .docx


    '''
    def __init__(self, path):
        try:
            self.path = path
            self.zf = zipfile.ZipFile(path)
        except Exception as e:
            print 'Unable to open file: {}'.format(path)

    def word_to_txt(self, path, export_format):
        '''
        Takes a doc file path (/*/*/.../*.doc) and converts to the designated file type
        Inputs are strings
        returns a path to the newly created  file (/*/*/.../*.export_format)
         '''
        self.temp_string = path.split('.');
        self.inputDirectory = temp_string[0];
        self.cmd = 'unoconv -f  {} {}'.format(export_format, path)
        os.system(self.cmd)
        self.newpath = self.inputDirectory + '.' + export_format
        print '{} converted to {}.'.format(path, self.newpath)
        return self.newpath

    def getPages(self, zf):
        '''
        Accepts the path to a zipfile.
        Calculates the number of pages of evidence.
        Returns an integer of the number of pages
        '''
        self.app = zf.read('docProps/app.xml')
        self.pages = re.findall('<Pages>[0-9]+<', self.app)
        try:
            self.pagestr = self.pages[0]
        except Exception as e:
            print 'Unable to establish number of pages for {}'.format(zf)
        self.trans = string.maketrans("","")
        self.nodigs = self.trans.translate(self.trans, string.digits)
        self.outString = self.pagestr.translate(self.trans, self.nodigs)
        return int(outString) - 4 #subtract 4 to account for Hansard styling.

    def getWitnesses(self, zf):
        '''
        Accepts a path to zipfile
        Returns an integer of the number of witnesses that appeared
        '''
        #get number of witnesses. item4 contains data on witnesses.
        try:
            self.witnesses = zf.read('customXml/item4.xml')
            self.soup = BeautifulSoup(witnesses, 'lxml')
            self.witList = len(soup.find_all('t:name'))
            return int(self.witList)
        except Exception as e:
            'Unable to establish number of witnesses for {}'.format(zf)

    def getType(self, zf):
        '''
        Accepts the handle to a zipfile
        Returns a string of committee type: Legislation or References
        '''
        self.custom = zf.read('docProps/custom.xml')
        self.app = zf.read('docProps/custom.xml')
        self.cttee = re.findall('(Legislation|References)', self.app)
        try:
            self.data = cttee[0]
        except:
            'Unable to establish committee type for {}'.format(zf)
        return self.data

class PDFTools(object):
    def __init__():
        pass

    def hansard_page_count(self, PDF_file):
        '''
        takes a pdf file.
        Returns an integer sum of the number of pages.
        '''
        pages = 0
        inputFile = PyPDF2.PdfFileReader(PDF_file)
        pages += inputFile.getNumPages()
        pages -= 4 #taking into account the leading pages in Hansard pdfs.
        return pages

class SubmissionTools(object):
    def __init__(self):
        pass
    def count_subs(self, files):
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
