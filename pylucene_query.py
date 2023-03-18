
import logging, sys
logging.disable(sys.maxsize)

import os
import sys
import time
import json
import lucene
from pprint import pprint
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity

def sort_by_score(json):
    try:
        return int(json['score'])
    except:
        return 0


def retrieve(storedir, query, k):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    parser = QueryParser('Body', StandardAnalyzer())
    parsed_query = parser.parse(query)

    topDocs = searcher.search(parsed_query, k).scoreDocs
    
    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "score": hit.score,
            "title": doc.get("Title"),
            "url": doc.get("Url"),
            "body": doc.get("Body")[0:200]
        })
    return topkdocs

def get_query_results():
    query = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    t = 0
    
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    index_dir = "pylucene_index_dir/"
    file_names = os.listdir(index_dir)

    total_list = []

    for name in file_names:
        start_time = time.time()
        topK = retrieve(index_dir+name, query, k)
        end_time = time.time() - start_time
        t += end_time
        topK.sort(key=sort_by_score, reverse=True)
        total_list += topK[0:3]

    total_list.sort(key=sort_by_score, reverse=True)

    if len(total_list) > 0:
        return {"response_time": round(t, 4), "results":total_list}
    else:
        return {"response_time": round(t, 4), "results":[]}

if __name__ == "__main__":
    print(get_query_results())
