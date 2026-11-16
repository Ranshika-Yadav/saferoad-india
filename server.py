#!/usr/bin/env python3
"""SafeRoad India demo app. Standard-library Python, SQLite, admin token."""
import os, json, sqlite3, re, datetime, secrets, hmac, time, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent
DB=Path(os.environ.get('SAFEROAD_DB',str(ROOT/'saferoad.db')))
PORT=int(os.environ.get('PORT','8000'))
ADMIN_TOKEN=os.environ.get('ADMIN_TOKEN','')
LOCK=threading.Lock(); HITS={}
def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB,timeout=15)
    c.execute('CREATE TABLE IF NOT EXISTS submissions (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL, city TEXT, role TEXT, interest TEXT, message TEXT NOT NULL, created_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT "new")')
    c.execute('CREATE TABLE IF NOT EXISTS pledges (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, created_at TEXT NOT NULL)')
    c.commit();return c
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','strict-origin-when-cross-origin');self.send_header('X-Frame-Options','DENY');super().end_headers()
    def reply(self,status,data):
        raw=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def authorized(self):
        auth=self.headers.get('Authorization','');return bool(ADMIN_TOKEN) and hmac.compare_digest(auth,'Bearer '+ADMIN_TOKEN)
    def do_GET(self):
        route=urlparse(self.path).path
        if route=='/api/admin/submissions':
            if not self.authorized():return self.reply(401,{'error':'Unauthorized'})
            with connect() as c: rows=c.execute('SELECT id,category,name,email,city,role,interest,message,created_at,status FROM submissions ORDER BY id DESC LIMIT 500').fetchall()
            keys=['id','category','name','email','city','role','interest','message','created_at','status'];return self.reply(200,{'items':[dict(zip(keys,r)) for r in rows]})
        if route=='/api/admin/stats':
            if not self.authorized():return self.reply(401,{'error':'Unauthorized'})
            with connect() as c:
                groups=dict(c.execute('SELECT category,COUNT(*) FROM submissions GROUP BY category').fetchall());pledges=c.execute('SELECT COUNT(*) FROM pledges').fetchone()[0]
            return self.reply(200,{'categories':groups,'pledges':pledges})
        if route.startswith('/api/'):return self.reply(404,{'error':'Not found'})
        if route.endswith('.db') or route.endswith('.sqlite') or route.startswith('/.') or route.endswith('.py') or route.endswith('.zip') or route.endswith('.md') or route.endswith('.log'):
            return self.reply(404,{'error':'Not found'})
        return super().do_GET()
    def do_POST(self):
        route=urlparse(self.path).path
        if route not in ('/api/contact','/api/volunteer','/api/report','/api/campaign','/api/pledge','/api/admin/update','/api/admin/delete'):return self.reply(404,{'error':'Not found'})
        if route.startswith('/api/admin/') and not self.authorized():return self.reply(401,{'error':'Unauthorized'})
        ip=self.client_address[0];now=time.monotonic()
        with LOCK:
            recent=[x for x in HITS.get(ip,[]) if now-x<60]
            if len(recent)>=30:return self.reply(429,{'error':'Too many requests. Try again later.'})
            recent.append(now);HITS[ip]=recent
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size<2 or size>12000:return self.reply(413,{'error':'Invalid request size'})
            data=json.loads(self.rfile.read(size))
            if not isinstance(data,dict):raise ValueError()
            if route.startswith('/api/admin/'):
                ident=int(data.get('id',0))
                if ident<=0:return self.reply(400,{'error':'Invalid record ID'})
                with connect() as c:
                    if route.endswith('/delete'):c.execute('DELETE FROM submissions WHERE id=?',(ident,))
                    else:
                        status=str(data.get('status',''))
                        if status not in ('new','in_review','resolved'):return self.reply(400,{'error':'Invalid status'})
                        c.execute('UPDATE submissions SET status=? WHERE id=?',(status,ident))
                return self.reply(200,{'success':True})
            if route=='/api/pledge':
                name=str(data.get('name','')).strip()
                if not 2<=len(name)<=100 or not data.get('consent'):return self.reply(400,{'error':'Enter a name and confirm the pledge.'})
                with connect() as c:cur=c.execute('INSERT INTO pledges(name,created_at) VALUES(?,?)',(name,datetime.datetime.now(datetime.timezone.utc).isoformat()));ident=cur.lastrowid
                return self.reply(201,{'success':True,'id':f'SR-{ident:06d}'})
            category=route.rsplit('/',1)[-1]
            f={k:str(data.get(k,'')).strip()[:2000] for k in ('name','email','city','role','interest','message','location','hazard')}
            if not data.get('consent'):return self.reply(400,{'error':'Please confirm consent.'})
            if category=='report':
                if not f['city'] or not f['location'] or not f['hazard'] or len(f['message'])<10:return self.reply(400,{'error':'Complete the hazard report.'})
                f['name']='Community reporter';f['interest']=f['hazard'];f['role']=f['location']
            else:
                if not 2<=len(f['name'])<=120:return self.reply(400,{'error':'Enter a valid name.'})
                if category=='campaign':f['message']='Campaign interest: '+f['interest']
                if category=='volunteer' and not f['city']:return self.reply(400,{'error':'City required.'})
                if len(f['message'])<3:return self.reply(400,{'error':'Enter a message.'})
            if (category!='report' or f['email']) and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',f['email']):return self.reply(400,{'error':'Enter a valid email.'})
            with connect() as c:c.execute('INSERT INTO submissions(category,name,email,city,role,interest,message,created_at) VALUES(?,?,?,?,?,?,?,?)',(category,*(f[k] for k in ('name','email','city','role','interest','message')),datetime.datetime.now(datetime.timezone.utc).isoformat()))
            return self.reply(201,{'success':True,'message':'Submission received. Thank you!'})
        except (ValueError,TypeError,UnicodeDecodeError,json.JSONDecodeError):return self.reply(400,{'error':'Invalid request.'})
        except Exception as e:
            print('Server error:',type(e).__name__);return self.reply(500,{'error':'Server error.'})
if __name__=='__main__':
    with connect():pass
    if not ADMIN_TOKEN:print('WARNING: ADMIN_TOKEN not set. Admin API disabled.')
    print(f'SafeRoad India listening on port {PORT}')
    ThreadingHTTPServer(('0.0.0.0',PORT),Handler).serve_forever()
