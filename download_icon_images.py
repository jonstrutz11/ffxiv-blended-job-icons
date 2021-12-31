"""Use the XIV API to download all icon images for every job and save these
images as files locally. Also processes and saves some basic JSON data
describing each class/job and their actions."""

import json
import pathlib
import requests

from typing import List

THIS_FILE_DIR_PATH = pathlib.Path(__file__).parent.resolve()
BASE_URL = 'https://xivapi.com'


def get_all_class_job_info() -> List[dict]:
    """Get dictionary from the XIV API which contains class/job IDs, Names,
    and URL endpoints which can be used for more information on that class/job.

    Returns
    -------
    all_class_job_info : List[dict]
        Keys are 'ID' (primary key), 'Icon' (endpoint to class/job icon .png),
        'Name', and 'Url' (for more info on class/job).
    """
    global BASE_URL
    url = f'{BASE_URL}/ClassJob'
    r = requests.get(url)
    all_class_job_info = r.json()['Results']  # single page so don't worry about pagination
    return all_class_job_info


def get_additional_info_and_actions(cj_basic_info: dict) -> dict:
    """Get additional info as well as info on each action for a given class or
    job.
    
    Parameters
    ----------
    cj_basic_info : dict
        Dict with basic info for class/job. Must include 'Url' key which points
        to XIV API endpoint for ClassJob information.

    Returns
    -------
    cj_full_info : dict
        Dict with original info and additional info (actions, abbreviation).
    """
    cj_full_info = {}

    global BASE_URL
    url = f'{BASE_URL}{cj_basic_info["Url"]}'

    r = requests.get(url)

    cj_json = r.json()
    cj_action_ids = cj_json['GameContentLinks']['Action']['ClassJob']
    
    if 'Trait' in cj_json['GameContentLinks']:  # some classes have no traits (e.g. Lancer)
        cj_trait_ids = cj_json['GameContentLinks']['Trait']['ClassJob']
    else:
        cj_trait_ids = []

    if 'CraftAction' in cj_json['GameContentLinks']:  # crafting classes have 2 kinds of actions
        cj_craft_action_ids = cj_json['GameContentLinks']['CraftAction']['ClassJob']
    else:
        cj_craft_action_ids = None

    cj_abbrev = cj_json['Abbreviation']

    global THIS_FILE_DIR_PATH
    cj_action_icon_image_path = f'{THIS_FILE_DIR_PATH}/icons/action_icons/{cj_abbrev}'
    pathlib.Path(cj_action_icon_image_path).mkdir(parents=True, exist_ok=True)
    cj_trait_icon_image_path = f'{THIS_FILE_DIR_PATH}/icons/trait_icons/{cj_abbrev}'
    pathlib.Path(cj_trait_icon_image_path).mkdir(parents=True, exist_ok=True)

    cj_icon_image_path = f'{THIS_FILE_DIR_PATH}/icons/class_job_icons/{cj_abbrev}.png'
    r = requests.get(f'{BASE_URL}/{cj_basic_info["Icon"]}')
    with open(cj_icon_image_path, 'wb') as outfile:
        outfile.write(r.content)

    cj_actions = download_icon_images_and_info(cj_action_ids, 'Action', cj_action_icon_image_path, cj_abbrev)
    cj_craft_actions = download_icon_images_and_info(cj_craft_action_ids, 'CraftAction', cj_action_icon_image_path, cj_abbrev)
    cj_actions += cj_craft_actions
    cj_traits = download_icon_images_and_info(cj_trait_ids, 'Trait', cj_trait_icon_image_path, cj_abbrev)

    cj_full_info = cj_basic_info.copy()
    cj_full_info['Abbreviation'] = cj_abbrev
    cj_full_info['Icon Path'] = cj_icon_image_path
    cj_full_info['Actions'] = cj_actions
    cj_full_info['Traits'] = cj_traits


    return cj_full_info


def download_icon_images_and_info(game_content_ids: List[int], icon_type: str, icon_dir: str, cj_abbrev: str) -> List[dict]:
    """Download and get info for all requested actions or traits. Saves all
    action or trait icons as PNG files in requested directory.
    
    Parameters
    ----------
    game_content_ids : List[int]
        Primary keys of actions or traits in XIV API.
    icon_type : str
        'Action' or 'Trait'.
    icon_dir : str
        Path to directory to save icon images in.
    cj_abbrev : str
        Abbreviation of class or job.

    Returns
    -------
    gc_list :
        List of dictionaries. Each dictionary contains action or trait 'ID',
        'Name' and 'Icon Path' (where it is saved locally).
    """
    gc_list = []
    for gc_id in game_content_ids:
        # Get info for action
        r = requests.get(f'{BASE_URL}/{icon_type}/{gc_id}')
        gc_json = r.json()

        # some actions are deprecated and have 0 for this value
        if icon_type == 'Action' and not gc_json['IsPlayerAction']:
            continue
        elif icon_type == 'CraftAction' and not gc_json['ClassJob']:
            continue
        else:
            gc_icon_api_path = gc_json['Icon']
            gc_icon_local_path = f'{icon_dir}/{gc_id}.png'

            # Get image for action
            r = requests.get(f'{BASE_URL}/{gc_icon_api_path}')
            with open(gc_icon_local_path, 'wb') as outfile:
                outfile.write(r.content)

            gc_dict = {
                'ID': gc_id,
                'Name': gc_json['Name'],
                'Icon Path': gc_icon_local_path
            }

            gc_list.append(gc_dict)

    return gc_list


if __name__ == '__main__':
    pathlib.Path(f'{THIS_FILE_DIR_PATH}/class_job_info').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'{THIS_FILE_DIR_PATH}/icons').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'{THIS_FILE_DIR_PATH}/icons/class_job_icons').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'{THIS_FILE_DIR_PATH}/icons/action_icons').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'{THIS_FILE_DIR_PATH}/icons/trait_icons').mkdir(parents=True, exist_ok=True)

    all_class_job_info = get_all_class_job_info()
    for cj_basic_info in all_class_job_info:
        cj_full_info = get_additional_info_and_actions(cj_basic_info)
        
        cj_full_info_path = f'{THIS_FILE_DIR_PATH}/class_job_info/{cj_full_info["Abbreviation"]}.json'
        with open(cj_full_info_path, 'w') as outfile:
            json.dump(cj_full_info, outfile, indent=4)

        print(cj_full_info['Abbreviation'] + ' processed')
