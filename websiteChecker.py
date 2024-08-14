import argparse
import requests
from bs4 import BeautifulSoup
import urllib.parse
import psutil
import time

def fetch_page(url):
    """
    Fetch the page from the url
    PRE : url should be a string of an url
    POST : Return the content of the url as string and None if the request fail
    RAISE : requests.RequestException if trouble with the http request for the page
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

def count_links(soup):
    """
    Count the links on the page
    PRE : soup is a BeautifulSoup object
    POST : Return a tuple of the number of clickable links as an integer and of href links
    """
    links = soup.find_all('a', href=True)
    return len(links), [link['href'] for link in links]

def count_images(soup):
    """
    Count the images on the page
    PRE : soup is a BeautifulSoup object
    POST : Return a tuple of the number of images as an integer and the src of each image
    """
    images = soup.find_all('img', src=True)
    return len(images), [img['src'] for img in images]

def display_statistics(count, details, type_):
    """
    Display the statistics
    PRE : count should be a int, details a list of strings and type_ a string
    POST : Print the number of type_ requested and if details is not null, print the details
    """
    print(f"Number of {type_}: {count}")
    if details:
        print("\nDetails:")
        for i, detail in enumerate(details, start=1):
            print(f"{i}. {detail}")

def save_to_file(filename, count, details, type_):
    """
    Save the data on a file
    PRE : filename is a filename with his path, count an integer, details a list of string and type_ a string
    POST : Write the data in the file and print a confirmation message
    """
    with open(filename, 'w') as file:
        file.write(f"Number of {type_}: {count}\n")
        if details:
            file.write(f"\nDetails:\n")
            for i, detail in enumerate(details, start=1):
                file.write(f"{i}. {detail}\n")
    print(f"Results saved to {filename}")

def print_system_resources():
    """
    Print the current system resource usage
    POST : Print cpu, memory, disk and network usage
    """
    print("\nSystem Resource Usage:")
    print(f"CPU usage: {psutil.cpu_percent()}%")
    print(f"Memory usage: {psutil.virtual_memory().percent}%")
    print(f"Disk usage: {psutil.disk_usage('/').percent}%")
    print(f"Network I/O: {psutil.net_io_counters().bytes_sent / 1024:.2f} KB sent, {psutil.net_io_counters().bytes_recv / 1024:.2f} KB received")

def main():
    parser = argparse.ArgumentParser(description='Count and analyze links or images on a web page.')
    parser.add_argument('url', help='The URL of the web page to analyze.')
    parser.add_argument('-l', '--link', action='store_true', help='Count the number of clickable links.')
    parser.add_argument('-p', '--picture', action='store_true', help='Count the number of images.')
    parser.add_argument('-s', '--save', help='Save the results to a file.')
    parser.add_argument('-d', '--detailed', action='store_true', help='Display detailed information about links or images.')
    parser.add_argument('--stats', action='store_true', help='Display additional statistics such as link URLs and image sizes.')
    parser.add_argument('-r','--ressources', action='store_true', help='Display system resources usage before and after the page processing.')

    args = parser.parse_args()
    
    if args.link and args.picture:
        print("Please choose either --link or --picture, not both.")
        return
    
    if not args.link and not args.picture:
        args.link = True 

    if args.ressources:
        print("Before fetching the page:")
        print_system_resources()
        start_time = time.time()

    page_content = fetch_page(args.url)
    if not page_content:
        return

    if args.ressources:
        print("\nAfter fetching the page:")
        print_system_resources()
        print(f"Time taken to fetch the page: {time.time() - start_time:.2f} seconds")

    soup = BeautifulSoup(page_content, 'html.parser')
    
    if args.link:
        count, details = count_links(soup)
        if not args.detailed:
            print(f"Number of clickable links: {count}")
        else:
            display_statistics(count, details, 'clickable links')
        if args.stats:
            unique_links = set(urllib.parse.urljoin(args.url, link) for link in details)
            print(f"\nUnique link URLs:\n{', '.join(unique_links)}")
    
    elif args.picture:
        count, details = count_images(soup)
        if not args.detailed:
            print(f"Number of images: {count}")
        else:
            display_statistics(count, details, 'images')
        if args.stats:
            for img in details:
                try:
                    img_url = urllib.parse.urljoin(args.url, img)
                    response = requests.head(img_url)
                    print(f"Image URL: {img_url} | Size: {response.headers.get('Content-Length', 'unknown')} bytes")
                except requests.RequestException as e:
                    print(f"Error getting image size for {img}: {e}")

    if args.save:
        save_to_file(args.save, count, details, 'clickable links' if args.link else 'images')

    if args.ressources:
        print("\nAfter processing the page:")
        print_system_resources()

if __name__ == '__main__':
    main()
