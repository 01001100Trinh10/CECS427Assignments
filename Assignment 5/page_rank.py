import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from urllib.parse import urljoin, urlparse

def argument_parser():
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
            lines = [line.strip() for line in f.readlines() if line.strip()]
            max_nodes = int(lines[0])
            domain = lines[1]
            seeds = lines[2:]
            return max_nodes, domain, seeds
    except Exception as e:
        print(f"Error reading crawler file: {e}")
        return None, None, None
    
def plot_loglog_degree(graph):
    degrees = [graph.degree(n) for n in graph.nodes()]
    values, counts = np.unique(degrees, return_counts=True)
    plt.figure()
    plt.loglog(values, counts, marker="o", linestyle="None")
    plt.title("Log-log plot of degree distribution")
    plt.xlabel("Degree")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()

class LinkSpider(scrapy.Spider):
    name = "link_spider"
    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 100,
        'DOWNLOAD_DELAY': 1.5,
        'DEPTH_LIMIT': 3,
        'LOG_ENABLED': True,
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, domain=None, start_urls=None, max_nodes=100, **kwargs):
        super().__init__(**kwargs)
        self.allowed_domains = [domain]
        self.start_urls = start_urls
        self.max_nodes = int(max_nodes)
        self.visited = set()
        self.graph = nx.DiGraph()

    def parse(self, response):
        if len(self.visited) >= self.max_nodes:
            raise CloseSpider('Max nodes reached')

        current_url = response.url
        if current_url in self.visited:
            return
        
        print(f"[{len(self.visited)}/{self.max_nodes}] Crawling: {current_url}")

        self.visited.add(current_url)
        self.graph.add_node(current_url)

        for link in response.css('a::attr(href)').getall():
            href = urljoin(current_url, link)
            parsed = urlparse(href)

            if parsed.netloc not in self.allowed_domains:
                continue
            if not href.endswith(('.html', '/')) or '#' in href:
                continue

            self.graph.add_edge(current_url, href)
            if href not in self.visited:
                yield scrapy.Request(href, callback=self.parse)

def run_crawler(domain, seeds, max_nodes):
    process = CrawlerProcess(settings={"USER_AGENT": "Mozilla/5.0"})

    # Holder to store graph from the spider
    spider_data = {}

    class TempSpider(LinkSpider):
        def closed(self, reason):
            spider_data["graph"] = self.graph

    process.crawl(TempSpider, domain=domain, start_urls=seeds, max_nodes=max_nodes)
    process.start()

    return spider_data.get("graph", nx.DiGraph())  # Return empty graph if not set

def main():
    args = argument_parser()
    graph = None

    if args.crawler:
        max_nodes, domain, seeds = read_file(args.crawler)
        parsed_domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        print(f"Starting crawl on domain: {parsed_domain} with {len(seeds)} seeds")
        graph = run_crawler(parsed_domain, seeds, max_nodes)
        if args.crawler_graph:
            nx.write_gml(graph, args.crawler_graph)
            print(f"Saved crawled graph to {args.crawler_graph}")
        plt.figure(figsize=(15, 15))

        pos = nx.spring_layout(graph, k=0.15, iterations=20)

        nx.draw_networkx_nodes(graph, pos, node_size=25, node_color='skyblue')
        nx.draw_networkx_edges(graph, pos, alpha=0.1)
        # nx.draw_networkx_labels(graph, pos, font_size=5)

        plt.title("Crawled Web Graph")
        plt.axis('off')
        plt.tight_layout()
        plt.show()

    if args.input:
        try:
            graph = nx.read_gml(args.input)
            print(f"Loaded {args.input}")
            plt.figure(figsize=(15, 15))
            pos = nx.spring_layout(graph, k=0.15, iterations=20)
            nx.draw_networkx_nodes(graph, pos, node_size=50, node_color='skyblue')
            nx.draw_networkx_edges(graph, pos, alpha=0.3)
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