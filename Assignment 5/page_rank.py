import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from urllib.parse import urljoin, urlparse

def argument_parser():
    # Arguments passed by the user
    parser = argparse.ArgumentParser()
    parser.add_argument("--crawler", type=str, help="Input seed file for crawling")
    parser.add_argument("--input", type=str, help="graph specification")
    parser.add_argument("--loglogplot", action="store_true", help="Generates log-log plot of the degree distribution of the graph")
    parser.add_argument("--crawler_graph", type=str, help="Saves the processed graph to out_graph.gml")
    parser.add_argument("--pagerank_values", type=str, help="adds the pagerank values")
    return parser.parse_args()

def read_file(filename):
    try:
        with open(filename, 'r') as f:
            # Reads the first 2 as the max nodes and domains respectively. Everything else are seed urls
            lines = [line.strip() for line in f.readlines() if line.strip()]
            max_nodes = int(lines[0])
            domain = lines[1]
            seeds = lines[2:]
            return max_nodes, domain, seeds
    except Exception as e:
        print(f"Error reading crawler file: {e}")
        return None, None, None
    
def plot_loglog_degree(graph):
    # Simple loglog plot based on the degree distribution
    degrees = [graph.degree(n) for n in graph.nodes()]
    values, counts = np.unique(degrees, return_counts=True)
    plt.figure()
    plt.loglog(values, counts)
    plt.title("Log-log plot of degree distribution")
    plt.xlabel("Degree")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()

# Class for the web crawler
class LinkSpider(scrapy.Spider):
    name = "link_spider"
    # Settings to help traverse through the urls
    custom_settings = {
        'DOWNLOAD_DELAY': 1.0,
        'USER_AGENT': 'Mozilla/5.0 (compatible; PageRankCrawler/1.0)',
        'DEPTH_LIMIT': 3,
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, domain, start_urls=None, max_nodes=0, graph=None, *args,**kwargs):
        # Constructor intialization
        super(LinkSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = [domain]
        self.start_urls = start_urls
        self.max_nodes = int(max_nodes)
        self.visited = 0
        self.crawled_nodes = set()
        self.graph = graph if not None else nx.DiGraph()

    def parse(self, response):
        
        # Base case that exits once we hit our max node limit
        if self.visited >= self.max_nodes:
            raise CloseSpider('Reached max pages limit')

        # Parses url
        parsed_url = urlparse(response.url)
        normalized_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

        # If we already visited the url, go back
        if normalized_url in self.crawled_nodes:
            return
        
        # If not html, go back
        type = response.headers.get('Content-Type', b'').decode('utf-8')
        if 'text/html' not in type:
            return

        # Adds current node to the graph and into the visited nodes
        self.graph.add_node(normalized_url)
        self.crawled_nodes.add(normalized_url)
        self.visited += 1

        # Starts crawling
        print(f"[{self.visited}/{self.max_nodes}] Crawling: {normalized_url}")
        for link in response.css('a::attr(href)').getall():
            link = response.urljoin(link)
            parsed_link = urlparse(link)

            # Skips over non-http links
            if parsed_link.scheme not in ('http', 'https'):
                continue

            # Strips the domain for comparison
            target_domain = self.allowed_domains[0].lower().lstrip('www.')
            link_domain = parsed_link.netloc.lower().lstrip('www.')

            # Check if link is within the same domain or subdomain
            if not (link_domain == target_domain or link_domain.endswith("." + target_domain)):
                continue

            # Checks if it's html. If not, skip
            if '.' in os.path.basename(parsed_link.path):
                ext = os.path.splitext(parsed_link.path)[1].lower()
                if ext not in ('', '.html', '.htm'):
                    continue

            # Normalize the link
            normalized_link = parsed_link.scheme + "://" + parsed_link.netloc + parsed_link.path

            # Only add an edge if the target page is already in the graph
            if normalized_link in self.graph:
                self.graph.add_edge(normalized_url, normalized_link)

            # Only schedule to crawl uncrawled pages
            if self.visited < self.max_nodes and normalized_link not in self.crawled_nodes:
                yield scrapy.Request(normalized_link, callback=self.parse)


def run_crawler(domain, seeds, max_nodes):
    graph = nx.DiGraph()
    process = CrawlerProcess()
    # Holder to store graph from the spider
    process.crawl(LinkSpider, domain=domain, start_urls=seeds, max_nodes=max_nodes, graph=graph)
    process.start()
    graph.remove_edges_from(nx.selfloop_edges(graph))
    return graph

def main():
    args = argument_parser()
    graph = None

    if args.crawler:
        max_nodes, domain, seeds = read_file(args.crawler)
        parsed_domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        print(f"Max Nodes: {max_nodes}")
        print(f"Starting crawl on domain: {parsed_domain} with {len(seeds)} seeds")
        graph = run_crawler(parsed_domain, seeds, max_nodes)
        if args.crawler_graph:
            nx.write_gml(graph, args.crawler_graph)
            print(f"Saved crawled graph to {args.crawler_graph}")
        # plt.figure(figsize=(15, 15))

        # pos = nx.spring_layout(graph, k=0.15, iterations=20)

        # nx.draw_networkx_nodes(graph, pos, node_size=30, node_color='dodgerblue')
        # nx.draw_networkx_edges(graph, pos, alpha=0.1)
        # nx.draw_networkx_labels(graph, pos, font_size=5)

        # plt.title("Crawled Web Graph")
        # plt.axis('off')
        # plt.tight_layout()
        # plt.show()

    if args.input:
        try:
            graph = nx.read_gml(args.input)
            print(f"Loaded {args.input}")
            plt.figure(figsize=(6, 8))

            pos = nx.spring_layout(graph, k=0.15, iterations=20)

            nx.draw_networkx_nodes(graph, pos, node_size=50, node_color='lightblue')
            nx.draw_networkx_edges(graph, pos, alpha=0.25)
            nx.draw_networkx_labels(graph, pos, font_size=5)

            plt.title("Crawled Web Graph")
            plt.axis('off')
            plt.tight_layout()
            plt.show()
        except FileNotFoundError:
            print(f"Error: file {args.input} not found.")

    if graph is None:
        print("No graph data loaded. Exiting.")
        return
    
    if args.loglogplot:
        plot_loglog_degree(graph)

    if args.pagerank_values:
        pr = nx.pagerank(graph)
        with open(args.pagerank_values, 'w') as f:
            for node, value in sorted(pr.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{node} {value}\n")
        print(f"Saved PageRank values to {args.pagerank_values}")

if __name__ == "__main__":
    main()