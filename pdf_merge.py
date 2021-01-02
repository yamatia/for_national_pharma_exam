"""
国家試験問題の配布が必須、一般理論などで分割されているので、
表紙を除いて結合する
"""

import os
from PyPDF2 import PdfFileReader, PdfFileWriter

def main():
    path = input('input path:~/raw_data')
    
    print(os.listdir(path))
    
    for folder in os.listdir(path):
        if not os.path.isdir('{}/{}'.format(path,folder)):
            continue
        writer = PdfFileWriter()
        input_list = []

        print('{}/{}'.format(path,folder))

        for exam in os.listdir('{}/{}'.format(path,folder)):
            input_list.append(open('{}/{}/{}'.format(path,folder,exam),mode='rb'))

        
        for reader in map(PdfFileReader,input_list):
            for page in range(1,reader.getNumPages()):
                writer.addPage(reader.getPage(page))
        
        output_pdf = open('{}/{}.pdf'.format(path,folder),mode='wb')
        writer.write(output_pdf)
        output_pdf.close()
        
        for f in input_list:
            f.close()

if __name__=='__main__':
    main()