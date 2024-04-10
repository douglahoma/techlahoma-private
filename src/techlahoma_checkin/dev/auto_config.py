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
parameter_files = {
    k: Path(v) for k, v in vars(parameter_files).items()
}

for old_file_obj in parameter_files.values():
    if (not old_file_obj.exists()):
        raise FileNotFoundError()
    
    new_file_name = (
        old_file_obj.name
            if ("blank_" not in old_file_obj.name)
                else old_file_obj.name.split("_")[1]
    )
    new_file_path = "{}/{}".format(
        MOD_ROOT_FOLDER,
        new_file_name
    )
    new_file_obj = Path(new_file_path)

    if (not new_file_obj.exists()):
        new_file_obj.write_text(
            old_file_obj.read_text()
        )
        print("'{}' SUCESSFULLY SENT INTO PRODUCTION".format(
            old_file_obj.name, new_file_obj.name
        ))
        continue

    print("'{}' IS ALREADY ON THE SERVER...".format(new_file_obj.name))