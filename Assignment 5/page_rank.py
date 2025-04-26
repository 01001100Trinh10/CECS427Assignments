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
    plt.loglog(values, counts)
    plt.title("Log-log plot of degree distribution")
    plt.xlabel("Degree")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()

class LinkSpider(scrapy.Spider):
    name = "link_spider"
    custom_settings = {
        'DOWNLOAD_DELAY': 1.0,
        'DEPTH_LIMIT': 3,
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, domain=None, start_urls=None, max_nodes=0, **kwargs):
        super().__init__(**kwargs)
        self.allowed_domain = domain.replace("www.", "")
        self.start_urls = start_urls
        self.max_nodes = int(max_nodes)
        self.visited = set()
        self.frontier = set(start_urls)
        self.graph = nx.DiGraph()

    def start_requests(self):
        for url in self.frontier:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        if not self._is_html_response(response):
            return

        normalized_url = self._normalize_url(response.url)
        if normalized_url in self.visited or len(self.visited) >= self.max_nodes:
            return

        print(f"[{len(self.visited)}/{self.max_nodes}] Crawling: {normalized_url}")
        self.visited.add(normalized_url)
        self.frontier.discard(normalized_url)
        self.graph.add_node(normalized_url)

        links = response.css('a::attr(href)').getall()
        for link in links:
            href = urljoin(normalized_url, link)
            href = self._normalize_url(href)

            if not self._is_valid_url(href):
                continue

            # Only queue if we haven’t visited, it’s valid, and we're under max_nodes
            if href not in self.visited and href not in self.frontier and len(self.visited) + len(self.frontier) < self.max_nodes:
                self.frontier.add(href)
                yield scrapy.Request(
                    href,
                    callback=self.parse,
                    dont_filter=True  # ensures even query variations are crawled
                )

            # Add edge only if it's in the allowed domain and ends in a valid extension
            if self._url_likely_html(href):
                self.graph.add_edge(normalized_url, href)

    def _url_likely_html(self, url):
        parsed = urlparse(url)
        path = parsed.path.lower()
        valid_extensions = ('.html', '.htm', '')  # allow paths with no extension too
        return path.endswith(valid_extensions) or path.endswith('/')
    
    def _normalize_url(self, url):
        parsed = urlparse(url)
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return clean_url.rstrip('/')

    def _is_valid_url(self, url):
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        path = parsed.path.lower()

        # Only crawl pages from the same domain, with http/https, and likely HTML content
        valid_extensions = ('.html', '.htm', '')  # Allow empty extension too
        disallowed_extensions = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.svg', '.ico', '.mp4', '.webp')

        return (
            domain == self.allowed_domain
            and parsed.scheme in ["http", "https"]
            and not any(path.endswith(ext) for ext in disallowed_extensions)
            and path.endswith(valid_extensions) or path.endswith('/')
        )
    
    def _is_html_response(self, response):
        content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
        return 'text/html' in content_type

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
        print(f"Max Nodes: {max_nodes}")
        print(f"Starting crawl on domain: {parsed_domain} with {len(seeds)} seeds")
        graph = run_crawler(parsed_domain, seeds, max_nodes)
        if args.crawler_graph:
            nx.write_gml(graph, args.crawler_graph)
            print(f"Saved crawled graph to {args.crawler_graph}")
        plt.figure(figsize=(15, 15))

        pos = nx.spring_layout(graph, k=0.15, iterations=20)

        nx.draw_networkx_nodes(graph, pos, node_size=20, node_color='dodgerblue')
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
            plt.figure(figsize=(18, 18))
            pos = nx.spring_layout(graph, k=0.1, iterations=20)
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