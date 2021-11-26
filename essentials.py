import logging


def Logger():
    Log_Format = "%(levelname)s %(asctime)s - %(message)s"

    logging.basicConfig(filename="logfile.log",
                        # filemode="a",
                        format=Log_Format,
                        level=logging.ERROR)

    return logging.getLogger()
