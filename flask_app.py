import math
from settings import *
from flask import Flask, render_template
from kvm_func import inspector

def HumanReadFormat(size: int):
    if size > 0:
        pwr = math.floor(math.log(size, 1024))
        suff = ["KB", "MB", "GB", "TB", "PB"]
        return f"{size / 1024 ** pwr:.0f}{suff[pwr]}"
    else:
        return "0KB"
    

    
app = Flask(__name__)
@app.route("/", methods=["GET"])
def kvm_inspect():
    return render_template('index.html', inspect=inspector(LISTOFNODES), CpuForOs=CpuForOs, MemoryForOs=MemoryForOs, HumanReadFormat=HumanReadFormat)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=False)











