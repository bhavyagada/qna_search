import os
import json
import subprocess
import urllib.parse
from flask import Flask, render_template, request, abort

app = Flask(__name__)

#@app.errorhandler(404)
#def resource_not_found(e):
#    return jsonify(error=str(e)), 404

@app.route("/")
def hello_world():
    content = subprocess.run("ls -l", cwd=os.getcwd(), shell=True, capture_output=True, encoding='utf-8').stdout
    return render_template('index.html', content=content)

@app.route("/query", methods=['POST'])
def submit_query():
    if len(request.form.get('search_query')) < 1:
        abort(404, description="Search input cannot be empty!")
    elif request.form.get('index') == None:
        abort(404, description="Choose a index to search on!")
    else:
        query = request.form['search_query']
        index = request.form['index']
        if index == "PyLucene":
            response = eval(subprocess.run(f'python3 pylucene_query.py "{query}"', shell=True, stdout=subprocess.PIPE, encoding='utf-8').stdout)
            results = response["results"]
            for result in results:
                result["title"] = urllib.parse.unquote(result["title"])
                if "wikipedia" in result["url"]:
                    result["logo_text"] = "Wikipedia"
                elif "stackoverflow" in result["url"] or "stackexchange" in result["url"]:
                    result["logo_text"] = "Stackexchange"
                elif "reddit" in result["url"]:
                    result["logo_text"] = "Reddit"
                else:
                    result["logo_text"] = "Wikihow"
                if result["url"].endswith("/"):
                    result["str_url"] = "//".join(result["url"].split('/')[0:2]) + result["url"].split('/')[2] + " > " + " > ".join(result["url"].split('/')[3:-1])
                else:
                    result["str_url"] = "//".join(result["url"].split('/')[0:2]) + result["url"].split('/')[2] + " > " + " > ".join(result["url"].split('/')[3:])
        else:
            response = eval(subprocess.run(f'python3 bert_query.py "{query}"', shell=True, stdout=subprocess.PIPE, encoding='utf-8').stdout)
            real_results = response["results"]
            results = []
            for result in real_results:
                result_obj = {}
                url_key = next(iter(result["url"]))
                result_obj["url"] = result["url"][url_key]
                if result_obj["url"].endswith("/"):
                    result_obj["str_url"] = "//".join(result_obj["url"].split('/')[0:2]) + result_obj["url"].split('/')[2] + " > " + " > ".join(result_obj["url"].split('/')[3:-1])
                    result_obj["title"] = urllib.parse.unquote(result_obj["url"][:-1].split("/")[-1])
                else:
                    result_obj["str_url"] = "//".join(result_obj["url"].split('/')[0:2]) + result_obj["url"].split('/')[2] + " > " + " > ".join(result_obj["url"].split('/')[3:])
                    result_obj["title"] = urllib.parse.unquote(result_obj["url"].split("/")[-1])
            
                result_obj["score"] = result["score"]
                if "wikipedia" in result_obj["url"]:
                    result_obj["logo_text"] = "Wikipedia"
                elif "stackoverflow" in result_obj["url"] or "stackexchange" in result_obj["url"]:
                    result_obj["logo_text"] = "Stackexchange"
                elif "reddit" in result_obj["url"]:
                    result_obj["logo_text"] = "Reddit"
                else:
                    result_obj["logo_text"] = "Wikihow"
                results.append(result_obj)

        response_time = response["response_time"]
        total_results = len(results)
        return render_template('results.html', query=query, index=index, response_time=response_time, total_results=total_results, results=results)

if __name__ == "__main__":
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
