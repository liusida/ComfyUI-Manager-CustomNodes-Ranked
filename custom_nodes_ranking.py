from tqdm import tqdm
import requests
import json
import time
import os

# Environment variable for GitHub Token, you can get your token here: https://github.com/settings/tokens/
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# URLs
CUSTOM_NODE_LIST_URL = 'https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main/custom-node-list.json'
OUTPUT_FILENAME = 'custom-node-list.json'
CACHE_FILENAME = '.star-count-cache.json'

def fetch_custom_node_list(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch the custom node list: HTTP {response.status_code}")

def get_star_count(repo_url, cache):
    # Use the cache to avoid unnecessary API calls
    if repo_url in cache:
        return cache[repo_url]

    api_url = f"https://api.github.com/repos/{'/'.join(repo_url.split('/')[-2:])}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
    
    response = requests.get(api_url, headers=headers)
    time.sleep(0.1)  # Respectful pause to avoid hitting GitHub API rate limit
    if response.status_code == 200:
        star_count = response.json().get('stargazers_count', 0)
        cache[repo_url] = star_count  # Update the cache
        return star_count
    else:
        print(f"Failed to fetch star count for {repo_url}: HTTP {response.status_code}")
        return 0

def load_cache():
    try:
        with open(CACHE_FILENAME, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}  # Return an empty cache if the file does not exist

def save_cache(cache):
    with open(CACHE_FILENAME, 'w', encoding='utf-8') as file:
        json.dump(cache, file, ensure_ascii=False, indent=4)

def print_awesome_list(data, top_n=20):
    print("## Awesome List of ComfyUI Manager Custom Nodes\n")
    print("Discover the most popular and community-endorsed custom nodes for ComfyUI Manager, "
          "meticulously ranked by their GitHub Stars as on April 1, 2024.\n")
    for i, node in enumerate(data['custom_nodes'][:top_n], 1):
        print(f"No. {i}: [{node['title']}] {node['reference']} (Star: {node['star']})\n")

def main():
    # Load cache
    cache = load_cache()

    print(f"Fetch the custom node list from {CUSTOM_NODE_LIST_URL}")
    data = fetch_custom_node_list(CUSTOM_NODE_LIST_URL)

    # Update star counts with caching and progress bar
    for node in tqdm(data['custom_nodes'], desc='Fetching star counts', unit='node'):
        star_count = get_star_count(node['reference'], cache)
        node['star'] = star_count
        save_cache(cache)  # Save cache after each API call to preserve progress

    # Sort the custom nodes by star count
    data['custom_nodes'].sort(key=lambda x: x['star'], reverse=True)

    # Write the updated and sorted data to the output file
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    
    # Print the Awesome List to console
    print_awesome_list(data)

    print(f"Ranked custom node list written to {OUTPUT_FILENAME}")

if __name__ == "__main__":
    main()
