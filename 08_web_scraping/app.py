"""Extract page title, headings and links from a local HTML file or public URL."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.robotparser import RobotFileParser

AGENT='CourseLearningScraper/1.0'
LIMIT=2_000_000

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Redirect detected. Review the destination and request its URL directly.')

urlopen=build_opener(NoRedirect()).open

class PageParser(HTMLParser):
    def __init__(self,base):
        super().__init__(convert_charrefs=True); self.base=base; self.title=[]; self.headings=[]; self.links=[]; self.capture=None; self.parts=[]; self.href=None
    def handle_starttag(self,tag,attrs):
        if tag in ('title','h1','h2','h3','a') and self.capture is None:
            self.capture=tag; self.parts=[]; self.href=dict(attrs).get('href')
    def handle_data(self,data):
        if self.capture: self.parts.append(data)
    def handle_endtag(self,tag):
        if tag!=self.capture: return
        text=' '.join(''.join(self.parts).split())
        if tag=='title': self.title.append(text)
        elif tag.startswith('h'): self.headings.append({'level':tag,'text':text})
        elif self.href:
            url=urljoin(self.base,self.href)
            if urlsplit(url).scheme in ('http','https'): self.links.append({'text':text,'url':url})
        self.capture=None; self.parts=[]
    def result(self):
        unique=[]; seen=set()
        for link in self.links:
            key=(link['text'],link['url'])
            if key not in seen: seen.add(key); unique.append(link)
        return {'title':' '.join(self.title),'headings':self.headings,'links':unique}

def parse(html,base='https://example.com/'):
    page=PageParser(base); page.feed(html); return page.result()

def download(url):
    parts=urlsplit(url)
    if parts.scheme not in ('http','https') or not parts.netloc or parts.username or parts.password:
        raise ValueError('Use a public http(s) URL without credentials.')
    robot_url=f'{parts.scheme}://{parts.netloc}/robots.txt'
    try:
        with urlopen(Request(robot_url,headers={'User-Agent':AGENT}),timeout=10) as response:
            robots_text=response.read(LIMIT+1)
        if len(robots_text)>LIMIT: raise ValueError('robots.txt is too large.')
        robot=RobotFileParser(); robot.parse(robots_text.decode('utf-8',errors='replace').splitlines())
    except Exception as error:
        raise ValueError('Could not verify robots.txt. Use a permitted local HTML sample instead.') from error
    if not robot.can_fetch(AGENT,url): raise ValueError('robots.txt disallows this URL.')
    with urlopen(Request(url,headers={'User-Agent':AGENT}),timeout=10) as response:
        if response.geturl()!=url: raise ValueError('Redirect detected. Review the destination and request its URL directly.')
        if 'html' not in response.headers.get('Content-Type','').lower(): raise ValueError('Response is not HTML.')
        raw=response.read(LIMIT+1)
        if len(raw)>LIMIT: raise ValueError('Page exceeds 2 MB limit.')
        return raw.decode(response.headers.get_content_charset() or 'utf-8',errors='replace')

def main():
    p=argparse.ArgumentParser(description=__doc__); source=p.add_mutually_exclusive_group(required=True)
    source.add_argument('--file',type=Path); source.add_argument('--url'); p.add_argument('--base',default='https://example.com/'); p.add_argument('--output',type=Path)
    args=p.parse_args()
    try:
        html=args.file.read_text(encoding='utf-8') if args.file else download(args.url)
        result=json.dumps(parse(html,args.url or args.base),indent=2,ensure_ascii=False)
        if args.output: args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(result+'\n',encoding='utf-8')
        print(result)
    except (OSError,ValueError) as error: p.exit(1,f'Error: {error}\n')

if __name__=='__main__': main()
