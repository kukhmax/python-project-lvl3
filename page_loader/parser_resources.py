#!usr/bin/env python3

import os
import requests
import re
from pathlib import Path
from urllib.parse import urlparse
from page_loader.utilities import get_resourсe_url
from typing import Any, List, Tuple

SRC, IMG, SCRIPT, HREF, LINK = 'src', 'img', 'script', 'href', 'link'


def download_resources(url: str, soup: Any, dir: str) -> Any:  # noqa C901
    """Downloads scripts and links from a HTML file and replaces their paths

        Args:
            url(str): url of the page we want to download
            soup(Any): content of html file
            dir(str): path to directory where local resources are saved

        Retruns:
            path_to_html(str): path to the modified html file
    """
    list_of_links = get_links(soup)
    for link in list_of_links:
        link_to_resource = get_resourсe_url(url, link[0])
        if link_to_resource:
            response = requests.get(link_to_resource)
            suffix = Path(link_to_resource).suffix.lower()
            netloc = urlparse(link_to_resource).netloc
            path = urlparse(link_to_resource).path

            if suffix == ".png" or suffix == ".jpg":
                file_name = re.sub(r'\-(?=(png|jpg)$)', '.',
                                   re.sub(r"[^a-zA-Z0-9]+", '-',
                                          f'{netloc}{path}'))

            if not suffix:
                path += '.html'
            tmp = re.sub(r'[^a-zA-Z0-9]+', '-',
                         f'{netloc}{path}').rsplit('-', 1)
            file_name = f'{tmp[0]}.{tmp[1]}'
            path_to_resource = os.path.join(dir, file_name)
            if link[1] == SCRIPT or link[1] == IMG:
                soup.find(src=link[0])[SRC] = path_to_resource
            elif link[1] == LINK:
                soup.find(href=link[0])[HREF] = path_to_resource
            print('\x1b[3m\x1b[32m✓', end=' ')
            print('\x1b[1m\x1b[37m', link_to_resource)
            with open(path_to_resource, 'wb') as file:
                file.write(response.content)
    return soup


def get_links(soup: Any) -> List[Tuple[Any, str]]:
    """Get list of links to resources"""
    img_list = [(img.get(SRC), IMG) for img in soup(IMG) if soup(IMG)]
    script_list = [
        (img.get(SRC), SCRIPT) for img in soup(SCRIPT) if soup(SCRIPT)
    ]
    link_list = [
        (img.get(HREF), LINK) for img in soup(LINK) if soup(LINK)
    ]
    return img_list + script_list + link_list
