import os
import logging.config
import yaml


def setup_logging(
    default_path='log_config.yaml',
    default_level=logging.INFO,
    env_key='LOG_DIR'
):

    path = default_path
    if not os.path.exists(path):
        logging.basicConfig(level=default_level)
        return

    with open(path, 'rt') as f:
        config = yaml.safe_load(f)

    log_dir = os.getenv(env_key, '/src/logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, 'app.log')

    if 'handlers' in config and 'file' in config['handlers']:
        config['handlers']['file']['filename'] = log_file_path

    logging.config.dictConfig(config)


setup_logging()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
