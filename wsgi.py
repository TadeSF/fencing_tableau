from main import app
import logging
if __name__ == "__main__":
    app.run()

    handler = logging.FileHandler('flask.log')
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)