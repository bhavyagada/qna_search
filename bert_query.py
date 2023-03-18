import sys
import bert
import json
import time

def get_item(indices, resultScores):
    index_lookup = "index_lookup.json"
    contents = []
    result = []
    score_index = 0
    with open(index_lookup, "r+") as f:
        contents = json.load(f)
    if len(contents) > 0:
        for i in indices:
            if(i < len(contents)):
                m = {}
                m["url"] = contents[i]
                m["score"] = resultScores[score_index]
                score_index += 1
                result.append(m)
    return result

def main():
    query = "sample query"
    if(len(sys.argv) >= 2):
        query = sys.argv[1]
    start = time.time()
    resultIndex, resultScores = bert.query_index(query)
    if len(resultIndex) == 1 and resultIndex[0] == -1:
        t = time.time() - start
        return {"response_time": round(t, 4), "results":[]}
    else:
        results = get_item(resultIndex, resultScores)
        t = time.time() - start
        return {"response_time": round(t, 4), "results":results}

if __name__ == "__main__":
    print(main())
