import logging
import random
import typing

def build_logger(config):
    """
    Creates a logger
    @param logger_name what to name the logger
    """
    # Extract config parameters
    logger_name = config["log"]["name"]
    log_level = config["log"]["level"].upper()
    # Set up a logger
    logger = logging.getLogger(logger_name)
    # Convert the log level to an enum
    logger.setLevel(logging.getLevelName(log_level))
    log_handler = logging.StreamHandler()
    log_formatter = logging.Formatter("%(filename)s %(asctime)s %(levelname)s %(funcName)s:%(lineno)d  %(message)s")
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    return logger


# TODO: Run the tester and get http/https support for each site
def load_alexa_lazy(filename, schema: str = None):
    """
    Loads URLs from a file format similar to the alexa top 1m
    Returns URLs lazily
    @param filename path to the dataset
    @param schema optional URI schema to add to each entry
                  example: http://, https://, ftp://, magnet:
    @yields urls from the dataset
    """
    prefix = None
    # If no schema is given, set the prefix to be empty
    if schema is None:
        prefix = ""
    # If schema is given with :// or :, use it as the prefix
    elif schema.endswith("://") or schema.endswith(":"):
        prefix = schema
    elif schema.isalnum():
        prefix = "{}://".format(schema)
    else:
        raise Exception("Invalid schema string")
    # Read the file
    with filename.open("r") as alexa_file:
        for url in alexa_file.readlines():
            # Extract and prefix the url
            yield prefix + url.rstrip().split(",")[1]

# TODO: Run the tester and get http/https support for each site
def load_alexa(filename, schema: str = None, shuffle: bool = False):
    """
    Loads URLs from a file format similar to the alexa top 1m
    
    @param filename path to the dataset
    @param schema optional URI schema to add to each entry
                  example: http://, https://, ftp://, magnet:
    @yields urls from the dataset
    """
    # Load the entire dataset
    urls = list(load_alexa_lazy(filename, schema))
    # If told to shuffle
    if shuffle:
        random.shuffle(urls)
    # Return the dataset
    return urls
    
