import pymysql
import csv
import sys
import io
from itertools import repeat
import urllib
from config import MYDB, PWD
from application import db
from application.models import *
import glob

def line_to_escape_tuple(a_line):
    data = []
    for i in a_line:
        try:
            d = urllib.quote_plus(i.decode('utf8', 'ignore'))
            data.append(d)
        except:
            b = urllib.quote_plus(i.decode('ascii', 'ignore'))
            data.append(b)
    return tuple(data)

class TsvHandler(object):
         def __init__(self):
                  self.metadata = "meta/finalmeta.csv"
                  self.dic = "Etymologies.txt"
         def dictionary_com_list(self):
                  with open (self.dic, "r") as myfile:
                           count = 1
                           #insert statement
                           for line in csv.reader(myfile, dialect="excel-tab"):
                               d_data = line_to_escape_tuple(line)
                               k = ("term_id", "term", "year")
                               ins = Dictionary_com()
                               setattr(ins, k[0], None)
                               setattr(ins, k[1], d_data[0])
                               setattr(ins, k[2], d_data[1])
                                   #try:
                               #slower than raw psycopg2 but will work with sqlite, mysql, or posgresql
                               db.session.add(ins)
                               if count % 1000 == 0:
                                   print count
                               count +=1
                               db.session.commit()

         def build_metadata(self):
                  with open (self.metadata, "r") as myfile:
                           count = 1
                           k = ["docid", "recordid", "oclc", "locnum", "author", "imprint", "date", "birthdate", "firstpub",
                           "enumcron", "subjects", "title", "nationality", "gender", "genretags"]
                           for m_line in csv.reader(myfile):
                               if count == 1:
                                   headers = m_line
                               else:
                                   m_data = line_to_escape_tuple(m_line)
                                   ins = Metadata()
                                   ins.id = None
                                   for i, j in enumerate(m_data):
                                       #print(m_data)
                                       #print(i, k[i], j)
                                       setattr(ins, k[i], j)
                                       db.session.add(ins)
                                       db.session.commit()
                               count += 1
                               if count % 1000 == 0:
                                   print(count)

         def build_counts(self):
             Counts.query.delete()
             #read folder
             files = glob.glob("newdata/*.tsv")
             #loop ids
             count = 1
             for i in files:
                 #for each id, read csv and bulk insert
                 docid = urllib.quote_plus(i.replace("newdata/", "").replace(".tsv", "").replace(".fic", ""))
                 #convert to work_id

                 try:
                     work_id = db.session.query(Metadata).filter(Metadata.docid==docid).one()
                 except:
                     work_id = None
                 f = open(i)
                 for row in csv.reader(f, dialect="excel-tab"):
                 #every tuple becomes a dictionary with k for keys
                     try:
                         ins = Counts()
                         ins.counts_id = None
                         ins.work_id = work_id.id
                         ins.doc_id = work_id.docid
                         ins.type = row[0]
                         ins.type_count = row[1]
                         db.session.add(ins)
                         db.session.commit()
                     except:
                         pass
                 if count % 100 == 0:
                    print ("Finished processing ", count, " out of ", len(files), " files")
                 count +=1
