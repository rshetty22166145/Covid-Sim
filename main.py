from app import App
import logging
import datetime

logging.basicConfig(filename='./logs/CovSim' +
                             str(datetime.datetime.now().date()) + '.log',
                    level=logging.DEBUG)

logging.info("----------------------------")

if __name__ == "__main__":
    # Create App
    app = App()

    # Start app
    app.start()
