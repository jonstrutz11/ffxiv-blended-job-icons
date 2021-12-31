"""For each class/job, blend all action and trait images."""

import json
import os
import pathlib

from PIL import Image
from typing import List

THIS_FILE_DIR_PATH = pathlib.Path(__file__).parent.resolve()


for cj_json_filename in os.listdir(THIS_FILE_DIR_PATH / 'class_job_info'):
    cj_json_path = THIS_FILE_DIR_PATH / 'class_job_info' / cj_json_filename
    
    with open(cj_json_path, 'r') as infile:
        cj_info = json.load(infile)

    cj_abbrev = cj_info['Abbreviation']
    blended_image = Image.open(THIS_FILE_DIR_PATH / 'icons_blended' / 'actions_only' / f'{cj_info["Abbreviation"]}.png')

    print('Overlaying image for', cj_abbrev)

    cj_icon = Image.open(THIS_FILE_DIR_PATH / 'icons' / 'class_job_icons' / f'{cj_info["Abbreviation"]}.png')
    cj_icon = cj_icon.resize((40, 40))
    blended_image.paste(cj_icon, (0, 0), cj_icon)

    cj_bi_out_path = THIS_FILE_DIR_PATH / 'icons_blended' / 'actions_only_w_overlay' / f'{cj_info["Abbreviation"]}.png'
    blended_image.save(cj_bi_out_path)
