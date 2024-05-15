from flask import Flask, request, render_template, jsonify
from sys import path
from pathlib import Path
from threading import Thread


ROOT = Path(__file__).parents[1]
TEMPLATES = ROOT/"templates"
path.append(str(ROOT))


class FlaskThread(Thread):
    def __init__(self):
        super().__init__()
        self.__app = Flask(__name__,  template_folder = str(TEMPLATES))
        self.__setup_routes()


    def run(self):
        self.__app.run("0.0.0.0", 5000)


    def __setup_routes(self):
        @self.__app.route("/")
        def home():
            return "HELLO"