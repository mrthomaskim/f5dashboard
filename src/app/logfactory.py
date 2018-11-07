import logging


def create(name):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(name)s %(message)s')
    fh = logging.FileHandler('/tmp/application.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(fh)

    logger.setLevel(logging.DEBUG)

    return logger
