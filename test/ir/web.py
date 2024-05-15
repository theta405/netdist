# Imports

from flask import Flask, request, render_template, jsonify
from sys import path
from pathlib import Path
from core import configs, modules, customDict


# Constants

ROOT = Path.cwd()
TEMPLATES = ROOT/"templates"


# Miscellaneous

path.append(str(ROOT.parents[0]))
app = Flask(__name__,  template_folder = str(TEMPLATES))


# Routing

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search/<string:system>", methods = ("POST",))
def search(system):
    if system in modules:
        receive = customDict(request.values)
        result = modules[system].execute(receive)
        result["page_size"] = configs[system].page_size
        return jsonify(result)


@app.route("/system/<string:operation>", methods = ("POST",))
def system(operation):
    receive = customDict(request.values)
    result = getattr(modules.system, operation)(receive)
    return jsonify(result)


# Main

def main():
    app.run("0.0.0.0", 10300, True)


if __name__ == "__main__":
    main()