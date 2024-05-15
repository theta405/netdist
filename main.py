from modules.front_end import FlaskThread
from time import sleep


flask_target = FlaskThread()
flask_target.start()


sleep(1)


del flask_target