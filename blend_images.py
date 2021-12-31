"""For each class/job, blend all action and trait images."""

import json
import os
import pathlib

from PIL import Image
from typing import List

THIS_FILE_DIR_PATH = pathlib.Path(__file__).parent.resolve()

PARENT_CLASSES = {
    'PLD': 'GLA',
    'WAR': 'MRD',
    'BRD': 'ARC',
    'MNK': 'PGL',
    'DRG': 'LNC',
    'ROG': 'NIN', 
    'WHM': 'CNJ',
    'SCH': 'ARC',
    'BLM': 'THM',
    'SMN': 'ARC'
}


def blend_images(img_paths: List[str]) -> Image:
    """Blend multiple images into a single image, weighting each image equally.
    
    Parameters
    ----------
    img_paths : List[str]
        List of filepaths to image files.

    Returns
    -------
    blended_image : PIL.Image
        Blended image.
    """
    blended_image = None
    for i, img_path in enumerate(img_paths):
        img = Image.open(img_path)
        if not blended_image:
            blended_image = img
        else:
            blended_image = Image.blend(blended_image, img, 1 / (i + 1))
    return blended_image


for cj_json_filename in os.listdir(THIS_FILE_DIR_PATH / 'class_job_info'):
    cj_json_path = THIS_FILE_DIR_PATH / 'class_job_info' / cj_json_filename
    
    with open(cj_json_path, 'r') as infile:
        cj_info = json.load(infile)

    cj_abbrev = cj_info['Abbreviation']

    print('Blending images for', cj_abbrev)

    parent_info = None
    if cj_abbrev in PARENT_CLASSES:
        parent_class = PARENT_CLASSES[cj_abbrev]
        parent_json_path = THIS_FILE_DIR_PATH / 'class_job_info' / f'{parent_class}.json'
        with open(parent_json_path, 'r') as infile:
            parent_info = json.load(infile)

    cj_img_paths = []
    for action in cj_info['Actions']:
        cj_img_paths.append(action['Icon Path'])
    if parent_info:  # i.e. has a parent class
        for action in parent_info['Actions']:
            cj_img_paths.append(action['Icon Path'])

    # for trait in cj_info['Traits']:
    #     cj_img_paths.append(trait['Icon Path'])
    # if parent_info:  # i.e. has a parent class
    #     for trait in parent_info['Traits']:
    #         cj_img_paths.append(trait['Icon Path']) 

    blended_image = blend_images(cj_img_paths)

    cj_bi_out_path = THIS_FILE_DIR_PATH / 'icons_blended' / 'actions_only' / f'{cj_info["Abbreviation"]}.png'
    blended_image.save(cj_bi_out_path)
