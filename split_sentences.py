'''
Created on Oct 14, 2019

@author: jzc1104

Splits paragraphs into sentences

'''

import csv,nltk,sys
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


if __name__ == '__main__':
    
    
    if len(sys.argv)>1:
        input_filename=sys.argv[1]
        output_filename=sys.argv[2]
    else:
        #input_filename="transcripts/190423_Henry_Per2.csv"
        #output_filename="transcripts/19023_Henry_Per2_split.csv"
        input_filename="test.csv"
        output_filename="testcsv_split.csv"
        
    
    new_transcript_lines=[]
    line_index=1
    
    timestamp_tag=1
    speaker_tag=0
    transcript_tag=2
    
    with open(input_filename,encoding="utf-8") as csv_file:
        csvreader = csv.reader(csv_file, delimiter=",")
        
        for line in csvreader:
            if len(line)<4:
                print("LESS THAN 4 COLUMNS:",line_index,line)
                continue
            if line[timestamp_tag]=="" and line[speaker_tag]=="" and line[transcript_tag]=="":continue
            
            sents=nltk.tokenize.sent_tokenize(line[transcript_tag])
            
            line[speaker_tag]=line[speaker_tag][:-1] #Speaker field always ends with ":", here we remove it
            new_sent=[line_index, line[timestamp_tag],line[speaker_tag],sents[0]]
            line_index+=1
            new_transcript_lines.append(new_sent)
            for sent in sents[1:]:
                new_sent=[line_index,"","",sent]
                line_index+=1
                new_transcript_lines.append(new_sent)
            
    headers=["Line","Time_Stamp","Speaker","Transcript"]
            
    with open(output_filename, 'w', encoding = 'utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=",")
        writer.writerow(headers)
        writer.writerows(new_transcript_lines)