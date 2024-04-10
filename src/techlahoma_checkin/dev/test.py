#!/usr/bin/python3

#!/usr/bin/python3

import argparse
import os

from pathlib import Path

THIS_FOLDER = Path(
    os.path.dirname(
        os.path.realpath(__file__)
    )
)
MOD_ROOT_FOLDER = THIS_FOLDER.parent

parser = argparse.ArgumentParser(
    prog='./auto_config.py',
    description="Deployment script to postion '.env' and 'config.json'",
    epilog='Text at the bottom of help'
)
parser.add_argument('-e', '--env', default=f"{THIS_FOLDER}/blank_.env")
parser.add_argument('-c', '--config', default=f"{THIS_FOLDER}/blank_config.json")

parameter_files = parser.parse_args()

print(parameter_files)