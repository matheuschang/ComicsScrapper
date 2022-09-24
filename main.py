import requests, os, sys
from bs4 import BeautifulSoup,SoupStrainer
import asyncio
import time 

global s
headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.206'}

class Scrapper():
    def __init__(self, searchQ):
        self.searchQ = searchQ
        self.selectedComics = []
        self.totalPages = 0
        self.pages = {}
        self.pagenum = 1
        self.URL = f'https://getcomics.info/page/{self.pagenum}/?s={self.searchQ}'
    
    def nextPage(self):
        self.pagenum +=1
        if self.pagenum > self.totalPages:
            self.URL = f'https://getcomics.info/page/{self.pagenum}/?s={self.searchQ}'

    def previousPage(self):
        self.pagenum-=1
    
    def goToPage(self, num):
        self.pagenum = num

    def changeComic(self, searchQ):
    
        self.totalPages = 0
        self.pagenum = 1
        self.pages = {}
        self.searchQ = searchQ
        self.URL = f'https://getcomics.info/page/{self.pagenum}/?s={self.searchQ}'

def loadFoundComics(headers=headers):
    if s.pagenum > s.totalPages:
       
        page = requests.get(s.URL, headers = headers, allow_redirects=False)
        soup = BeautifulSoup(page.content, 'html.parser')
        result =soup.find_all("h1", {"class": "post-title"})
        comics = []
        for r in result:
            comic = r.find("a")
            comics.append({"title" : comic.get_text(), "link" : comic["href"]})
        
        
        if len(comics) > 0:
            s.totalPages+=1
            s.pages[s.pagenum] = comics
        else:
            print("===== No more results availabel =====")
            s.previousPage()
            
        
        


    print("SELECT THE COMIC YOU WISH TO DOWNLOAD:\n")
    for i in range(len(s.pages[s.pagenum])):
        print(f"{'[' +( str(i) if i > 9 else '0'+str(i)) + ']':>4} - {s.pages[s.pagenum][i]['title']:>4}")
    print(f"Current page: {s.pagenum}.")

    if s.totalPages > 1 and s.pagenum > 1:
        print(f"\n{'[Z]':>4} - {'Previous results.':>4}")
    else:
        print()
    print(f"{'[X]':>4} - {'More results.':>4}")
    print(f"{'[C]':>4} - {'Search another comic?':>4}")
    print(f"{'[S]':>4} - {'Show Download Queue.':>4}")
    print(f"{'[D]':>4} - {'Download Queue.':>4}")
    print(f"{'[V]':>4} - {'Exit':>4}")
        
    op = input("\nOption: ")

    return op

def getDownloadLink(URL,headers=headers):
    page = requests.get(URL, headers = headers, allow_redirects=False)
    downloads = []
    for link in BeautifulSoup(page.content, 'html.parser', parse_only=SoupStrainer('a')):
        if link.has_attr('href'):
            if '/getcomics.info/links.php/' in link['href'] and link.get_text() in ['Main Server', 'Download Now']:
                downloads.append(link['href'])
    return downloads

def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)
    return wrapped

@background
def download(url, title):
    print(f"Downloading '{title}'...")
    r = requests.get(url)
    with open(f"{title}.cbr", "wb") as f:
        f.write(r.content)
    print(f"Finished {title}.")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


print("WELCOME TO COMIC SCRAPPER\n\tPlease type the name of the desired comic.\n")
os.makedirs(os.getcwd() + '\\comics', exist_ok=True)
os.chdir(os.getcwd() + '\\comics')
comic = input("Search comic: ")
s = Scrapper(comic)

op  = loadFoundComics()
while(op.isalnum()):
    if op.upper() == 'X':
        s.nextPage()
        print("\n\n\tPLEASE WAIT...\n\n")
        clear()
        op = loadFoundComics()
        
    elif op.upper() == 'C':
        clear()
        r = input("\nSearch comic: ")
        s.changeComic(r)
        op = loadFoundComics()

    elif (op.upper() == 'V'):
        print("\nThanks!")
        sys.exit()

    elif (op.upper() == 'R'):
        clear()
        s.goToPage(1)
        op = loadFoundComics()
    
    elif (op.upper() == 'D'):
        print(f"\nDownloading {len(s.selectedComics)} comics.")
        print("Starting Downloads...")

        for i in range(len(s.selectedComics)):
            urls =  getDownloadLink((s.selectedComics[i]['link']))
    
            for u in urls:
                indexC = f'_{i}' if len(urls) > 1 else ''
                download(u, s.selectedComics[i]['title']+ indexC)
            
        sys.exit()
    
    elif (op.upper() == 'Z' and s.pagenum > 1):
        clear()
        s.previousPage()
        op = loadFoundComics()

    elif op.upper() == 'S':
        clear()
        print("\n\nYour queue:\n")
        if len(s.selectedComics) > 0:
            for i in range(len(s.selectedComics)):
                print(f"{'(' +( str(i) if i > 9 else '0'+str(i)) + ')':>4} - {s.selectedComics[i]['title']}")
        else:
            print("No comics added to queue.")
        
        input("\nTap enter to continue.")
        op = 'R'
    
    elif (op.isnumeric()):
        op = int(op)
        if op < len(s.pages[s.pagenum]):
            print("\nChoose an option:")
            print(f"{'[X]':>4} - {'Download.':>4}")
            print(f"{'[C]':>4} - {'Add to queue.':>4}")
            op2 = input("\nOption: ")
            if op2.upper() == 'X':
                print(f"Starting Download of '{s.pages[s.pagenum][op]['title']}'...")
                urls =  getDownloadLink(s.pages[s.pagenum][op]['link'])
                indexC = f'_{i}' if len(urls) > 1 else ''
                for i in range(len(urls)):
                    download(urls[i], s.pages[s.pagenum][op]['title'] + indexC)
                    
                sys.exit()
       
            
            elif op2.upper() == 'C':
                s.selectedComics.append(s.pages[s.pagenum][op])
                print(f"Added '{s.pages[s.pagenum][op]['title']}' to queue")
                op = 'R'
                time.sleep(1)

        else:
            print("\nInvalid option! Finishing program...")  
            sys.exit()

        
    else:
        print("\nInvalid option! Please select one of the options above.")
        op = input("\nOption: ")




