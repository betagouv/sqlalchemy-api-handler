from logging import basicConfig, \
                    getLogger, \
                    CRITICAL, \
                    DEBUG, \
                    ERROR, \
                    INFO, \
                    WARNING, \
                    log
import os

from sqlalchemy_api_handler.utils.attr_dict import AttrDict

LOG_LEVEL = int(os.environ.get('LOG_LEVEL', INFO))

basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=LOG_LEVEL,
                    datefmt='%Y-%m-%d %H:%M:%S')


# this is so that we can have log.debug(XXX) calls in the app
# without XXX being evaluated when not at debug level
# this allows args to log.debug & co. to be lambdas that will
# get called when the loglevel is right
# cf. datascience/offers, in which the data printed in
# debug calls is costly to compute.
def api_logging(level, *args):
    if getLogger().isEnabledFor(level):
        evaled_args = map(lambda a: a() if callable(a) else a,
                          args)
        log(level, *evaled_args)


logger = AttrDict()
logger.critical = lambda *args: api_logging(CRITICAL, *args)
logger.debug = lambda *args: api_logging(DEBUG, *args)
logger.error = lambda *args: api_logging(ERROR, *args)
logger.info = lambda *args: api_logging(INFO, *args)
logger.warning = lambda *args: api_logging(WARNING, *args)
