'''
    Credit to Weichao Qiu: qiuwch at gmail dot com
    A script to compare different cites of a paper
'''
import subprocess
import json
import pdb
# import pandas as pd
import argparse
import os
import sys

from tqdm import tqdm

hypersim_id = '84c40cf28afdf84ec6941d92cacd49fed3c7ef9a'
seven_id = '00f2a152454db273b0d6831b6550beb37a135890'
nerf_id = '428b663772dba998f5dc6a24488fff1858a0899f'
scannet_id = 'e52e37cd91366f07df1f98e88f87010f494dd16e'
fvs_id = "49fae04a4e9383080788759f63dba75c86bd21b0"
replica_id = "60f511eef446120fe59563ee976f948d5e3f9064"
nerfw_id = "691eddbfaebbc71f6a12d3c99d5c155042459434"
nuscenes = "9e475a514f54665478aac6038c262e5a6bac5e64"
mode_seeking = "cec3bffdb0968cd820863005af54cc519704c24a"
def load_json(in_file):
    with open(in_file, 'r') as f:
        return json.load(f)

def download_json(url, out_file):
    subprocess.run(['wget', url, '-O', out_file])

def all_locate_paper_info_and_savecsv(dirs,paper_id):
    def get_paper_info(item):
        item = item['citingPaper']
        return {
            'title': item['title'],
            'year': item['year'],
            'paperId': item['paperId'],
            'url': f'https://semanticscholar.org/paper/{item["paperId"]}',
            'venue': item['venue'],
        }
    
    data = []
    for offset in range(0, 2000, 100):
        in_file = os.path.join(dirs, paper_id, f'{paper_id}_{offset}.json')
        page_data = load_json(in_file)
        data += page_data['data']

    paper_list = [get_paper_info(v) for v in data]
    # convert None in 'year' to 0
    paper_list = [{k: v if v is not None else 0 for k, v in item.items()} for item in paper_list]
    paper_list = sorted(paper_list, key=lambda x: x['year'])

    cur_paper_cite_info_file_name = os.path.join(dirs, paper_id, 'cite_info.csv')
    with open(cur_paper_cite_info_file_name, 'w') as f:
        for p in paper_list:
            # print(f'{p["year"]} {p["title"] :80s} {p["url"]}')
            line = f'{p["year"]}, {p["title"] :80s}, {p["venue"] :80s}, {p["url"]}\n'
            f.write(line)

def get_given_paper_info(paperID, dirs):

    if os.path.exists(dirs + paperID):
        pass
    else: # dowanload the paper if it is not downloaded
        os.makedirs(os.path.join(dirs, paperID))
        cur_paper_pwd = os.path.join(dirs, paperID)
        for offset in tqdm(range(0, 2000, 100)):
            url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?offset={offset}&fields=title,authors,year,venue'
            out_file = f'{paperID}_{offset}.json'
            download_json(url, os.path.join(cur_paper_pwd, out_file))
        all_locate_paper_info_and_savecsv(dirs, paperID)

def load_cite(paper_id, dirs):

    def get_paper_info(item):
        item = item['citingPaper']
        return {
            'title': item['title'],
            'year': item['year'],
            'paperId': item['paperId'],
            'url': f'https://semanticscholar.org/paper/{item["paperId"]}',
            'venue': item['venue'],
        }
    
    data = []
    for offset in range(0, 2000, 100):
        in_file = os.path.join(dirs, paper_id, f'{paper_id}_{offset}.json')
        page_data = load_json(in_file)
        data += page_data['data']


    paper_list = [get_paper_info(v) for v in data]
    return paper_list

def get_paper_info_by_paperId(paper_id):
    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,authors,year'
    out_file = f'{paper_id}.json'
    download_json(url, out_file)
    with open(out_file, 'r') as f:
        paper_info = json.load(f)
    if True:
        os.remove(out_file)
    return paper_info


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--paper_id', nargs="+" ,type=str, default=None)
    args.add_argument("--download_directory", default="./", type=str)
    args.add_argument('--download_only', action='store_true')
    args = args.parse_args()
    # for convince, we only consider two papers
    if args.paper_id is None:
        print("Please specify a paper id")
        sys.exit(1)
    
    print("Download cite information")
    for paper_id in args.paper_id:
        get_given_paper_info(paper_id, args.download_directory)
    print("Download cite information finished")
    
    if args.download_only:
        pass
    else:
        paper_db = {}
        # download_cite(scannet_id)

        nerf_cites = load_cite(args.paper_id[0], args.download_directory)
        seven_cites = load_cite(args.paper_id[1], args.download_directory)
        # scannet_cites = load_cite(scannet_id)

        for p in nerf_cites + seven_cites:
            paper_db[p['paperId']] = p

        nerf_keys = [v['paperId'] for v in nerf_cites]
        seven_keys = [v['paperId'] for v in seven_cites]
        # scannet_keys = [v['paperId'] for v in scannet_cites]

        # common = [v for v in nerf_keys if v in seven_keys]
        common = [v for v in nerf_keys if v in seven_keys]
        papers = [paper_db[k] for k in common]

        for p in papers:
            if type(p['year']) != int:
                p['year'] = 0

        papers = sorted(papers, key = lambda x: x['year'])
        print(len(common))

        # get paper name from paper id
        paper_one_name = get_paper_info_by_paperId(args.paper_id[0])['title']
        paper_two_name = get_paper_info_by_paperId(args.paper_id[1])['title']

        compare_file_name = f'{paper_one_name}_vs_{paper_two_name}.csv'
        with open(compare_file_name, 'w') as f:
            for p in papers:
                # print(f'{p["year"]} {p["title"] :80s} {p["url"]}')
                line = f'{p["year"]}, {p["title"] :80s}, {p["venue"] :80s}, {p["url"]}\n'
                f.write(line)