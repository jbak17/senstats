from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import sys

#Fuction to convert pdf file to text document.
def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text
#
# import pyPdf;
# def convert_pdf(document):
#     #fo = open(document[:-4], 'w');
#     pdf = pyPdf.PdfFileReader(open(document, 'rb'));
#     for page in pdf.pages:
#         print page.extractText()
#         #fo.write(page.extractText());
#     #fo.close();
#
if __name__ == '__main__':
    cmd = sys.argv[1]
    print cmd
    fo = open(str(cmd), 'w');
    fo.write(convert_pdf_to_txt(cmd));
    fo.close();
