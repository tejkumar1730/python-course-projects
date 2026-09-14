"""Serve the local audio reader. Open http://127.0.0.1:8005."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from pathlib import Path
import argparse

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--port',type=int,default=8005)
    args=p.parse_args()
    handler=partial(SimpleHTTPRequestHandler,directory=str(Path(__file__).parent))
    server=ThreadingHTTPServer(('127.0.0.1',args.port),handler)
    print(f'Audio reader: http://127.0.0.1:{args.port} (Ctrl+C to stop)',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__': main()
