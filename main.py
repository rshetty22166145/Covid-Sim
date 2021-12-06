from app import App
import logging
import datetime

logging.basicConfig(filename='./logs/CovSim' +
                             str(datetime.datetime.now()) + '.log',
                    level=logging.DEBUG)

if __name__ == "__main__":
    # Create App
    app = App()

    # Start app
    app.start()
