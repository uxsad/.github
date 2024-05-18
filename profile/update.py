#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re

import sys
import argparse

def setup_args():
    parser = argparse.ArgumentParser(description="Update dynamic file chunks")
    parser.add_argument("infile", type=argparse.FileType("r"), default=sys.stdin, nargs='?')
    parser.add_argument("outfile", type=argparse.FileType("w"), default=sys.stdout, nargs='?')
    return parser.parse_args()


def get_publications():
    URL = "https://ivu.di.uniba.it/projects/serene.html"

    res = requests.get(URL)
    page = BeautifulSoup(res.content, "html.parser", from_encoding='UTF-8')
    target = page.find('h2',string='Publications')
    content = []
    for sib in target.find_next_siblings():
        if sib.name=="h2":
            break
        elif sib.name != "h3" and sib.name != "p":
            content.append(sib.findAll("li"))
    content = [x for l in content for x in l]

    publications = BeautifulSoup("<ol />", "html.parser")
    publications.ol.append(BeautifulSoup("\n".join(str(x) for x in content), "html.parser"))
    return publications
    #print(page)

def replace_dynamic_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        rf'<!\-\- {marker} start \-\->.*<!\-\- {marker} end \-\->',
        re.DOTALL,
    )
    if not inline:
        chunk = f'\n{chunk}\n'
    chunk = f'<!-- {marker} start -->{chunk}<!-- {marker} end -->'
    return r.sub(chunk, content)


if __name__ == "__main__":
    args = setup_args()
    pubs = get_publications()
    content=args.infile.read()
    print(replace_dynamic_chunk(content, "publications", pubs), file=args.outfile)
    
