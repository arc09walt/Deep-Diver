#!/usr/bin/env python3
"""THE DEEP DIVER — legwork engine (v1.0)

Runs on the owner's PC. Takes plain-text jobs from jobs.txt, fetches
documents from the allowed shelves, VERIFIES each one by opening it and
pulling its text, fingerprints it, files it in the pond, writes one
index line per document, records every gap honestly, and prints a
plain-words receipt with timings.

The Diver does legwork only. It never judges a document's contents.
Story-versus-paper stays the desk's job (see STANDARDS.md).

Downloads are DATA. They are read, never run. This program writes
only inside its own folder and fetches only from the allowed hosts.
"""
import csv, hashlib, json, logging, os, sys, time, urllib.parse, urllib.request

logging.getLogger('pypdf').setLevel(logging.ERROR)  # keep the receipt clean

HERE = os.path.dirname(os.path.abspath(__file__))
POND = os.path.join(HERE, 'pond')
TEXTDIR = os.path.join(HERE, 'text')
INDEX = os.path.join(HERE, 'index.csv')
GAPS = os.path.join(HERE, 'gaps.log')
RECEIPTS = os.path.join(HERE, 'receipts')
UA = {'User-Agent': 'DeepDiver/1.0 (personal research; reads only)'}
ALLOWED_SUFFIXES = ('archive.org', 'cia.gov')
MAX_BYTES = 250_000_000          # one document, hard cap
MIN_WORDS_PER_PAGE = 20          # below this, it is a scan, not a text layer

# ---------------------------------------------------------------- setup
def need_pypdf():
    try:
        import pypdf  # noqa
        return True
    except ImportError:
        return False

def host_allowed(url):
    host = urllib.parse.urlparse(url).hostname or ''
    return any(host == s or host.endswith('.' + s) for s in ALLOWED_SUFFIXES)

def stamp():
    return time.strftime('%Y-%m-%d %H:%M:%S')

# ---------------------------------------------------------------- io
def fetch_bytes(url, receipt):
    """Download with the allowlist enforced. Returns bytes or None."""
    if not host_allowed(url):
        receipt.gap(f'BLOCKED (host not on the allowed shelf): {url}')
        return None
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = r.read(MAX_BYTES + 1)
    except Exception as e:
        receipt.gap(f'FETCH FAILED: {url} — {e}')
        return None
    if len(data) > MAX_BYTES:
        receipt.gap(f'TOO BIG (over the 250 MB cap): {url}')
        return None
    if not data[:5] == b'%PDF-':
        receipt.gap(f'NOT A PDF (the shelf handed back something else): {url}')
        return None
    return data

def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))

# ---------------------------------------------------------------- files
def known_hashes():
    out = set()
    if os.path.exists(INDEX):
        with open(INDEX, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if row.get('sha256'):
                    out.add(row['sha256'])
    return out

def index_line(row):
    new = not os.path.exists(INDEX)
    with open(INDEX, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['sha256', 'title', 'source',
                                          'shelf', 'date', 'pages',
                                          'words', 'file', 'fetched'])
        if new:
            w.writeheader()
        w.writerow(row)

# ---------------------------------------------------------------- receipt
class Receipt:
    def __init__(self):
        self.lines = []
        self.kept = 0
        self.dupes = 0
        self.gaps = 0
        os.makedirs(RECEIPTS, exist_ok=True)
    def say(self, s=''):
        print(s, flush=True)
        self.lines.append(s)
    def gap(self, s):
        self.gaps += 1
        self.say('  GAP: ' + s)
        with open(GAPS, 'a', encoding='utf-8') as f:
            f.write(f'{stamp()}  {s}\n')
    def save(self, name):
        path = os.path.join(RECEIPTS, name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.lines) + '\n')
        return path

# ---------------------------------------------------------------- core
def file_document(data, title, source, shelf, date, receipt):
    """Verify by reading, fingerprint, file, index. The heart of the Diver."""
    from pypdf import PdfReader
    import io
    t0 = time.time()
    sha = hashlib.sha256(data).hexdigest()
    if sha in known_hashes():
        receipt.dupes += 1
        receipt.say(f'  DUPLICATE (same fingerprint already in the pond): {title}')
        return
    try:
        reader = PdfReader(io.BytesIO(data))
        pages = len(reader.pages)
        text = '\n'.join((p.extract_text() or '') for p in reader.pages)
    except Exception as e:
        receipt.gap(f'UNREADABLE PDF: {title} — {e}')
        return
    words = len(text.split())
    if pages and words / pages < MIN_WORDS_PER_PAGE:
        receipt.gap(f'SCAN-ONLY, NO TEXT LAYER (OCR is a later slice): '
                    f'{title} — {pages} pages, only {words} words readable')
        return
    shelfdir = os.path.join(POND, shelf)
    os.makedirs(shelfdir, exist_ok=True)
    safe = ''.join(c if c.isalnum() or c in '._-' else '_' for c in
                   os.path.basename(urllib.parse.urlparse(source).path)) or 'doc.pdf'
    if not safe.lower().endswith('.pdf'):
        safe += '.pdf'
    dest = os.path.join(shelfdir, safe)
    with open(dest, 'wb') as f:
        f.write(data)
    os.makedirs(TEXTDIR, exist_ok=True)
    tname = os.path.splitext(safe)[0] + '.txt'
    with open(os.path.join(TEXTDIR, tname), 'w', encoding='utf-8') as f:
        f.write(text)
    index_line({'sha256': sha, 'title': title[:200], 'source': source,
                'shelf': shelf, 'date': date, 'pages': pages,
                'words': words, 'file': os.path.join(shelf, safe),
                'fetched': stamp()})
    receipt.kept += 1
    receipt.say(f'  KEPT: {title} — {pages} pages, {words:,} words, '
                f'fingerprint {sha[:12]}… ({time.time()-t0:.1f}s to verify and file)')

def job_fetch(url, shelf, receipt):
    receipt.say(f'FETCH one document into shelf "{shelf}":')
    receipt.say(f'  {url}')
    data = fetch_bytes(url, receipt)
    if data is None:
        return
    file_document(data, os.path.basename(urllib.parse.urlparse(url).path),
                  url, shelf, '', receipt)

def job_search(query, shelf, receipt, limit=0):
    receipt.say(f'SEARCH the archive for: {query}  →  shelf "{shelf}"')
    params = [('q', query), ('fl[]', 'identifier'), ('fl[]', 'title'),
              ('fl[]', 'date'), ('rows', 500), ('output', 'json')]
    url = 'https://archive.org/advancedsearch.php?' + urllib.parse.urlencode(params)
    try:
        docs = get_json(url)['response']['docs']
    except Exception as e:
        receipt.gap(f'SEARCH FAILED: {e}')
        return
    receipt.say(f'  {len(docs)} items on the shelf list.')
    docs.sort(key=lambda d: d['identifier'])  # same order every run
    if limit:
        docs = docs[:limit]
    for d in docs:
        ident = d['identifier']
        title = d.get('title', ident)
        date = str(d.get('date', ''))[:10]
        try:
            meta = get_json(f'https://archive.org/metadata/{ident}')
        except Exception as e:
            receipt.gap(f'METADATA FAILED: {ident} — {e}')
            continue
        pdfs = [f for f in meta.get('files', [])
                if f.get('name', '').lower().endswith('.pdf')]
        text_pdfs = [f for f in pdfs
                     if f.get('name', '').lower().endswith('_text.pdf')]
        plain_pdfs = [f for f in pdfs if f not in text_pdfs]
        pool = text_pdfs or plain_pdfs
        if not pool:
            receipt.gap(f'NO PDF ON THE ITEM: {ident} — {title}')
            continue
        pool.sort(key=lambda f: int(f.get('size', 0) or 0), reverse=True)
        fname = pool[0]['name']
        dl = f'https://archive.org/download/{ident}/{urllib.parse.quote(fname)}'
        data = fetch_bytes(dl, receipt)
        if data is None:
            continue
        file_document(data, title, dl, shelf, date, receipt)
        time.sleep(0.4)

# ---------------------------------------------------------------- main
def main():
    os.makedirs(POND, exist_ok=True)
    receipt = Receipt()
    receipt.say('=' * 64)
    receipt.say(f'THE DEEP DIVER — run started {stamp()}')
    receipt.say('Legwork only. Every kept file was opened and read first.')
    receipt.say('=' * 64)
    if not need_pypdf():
        receipt.say('')
        receipt.say('STOPPED BEFORE STARTING: the text-reading part (pypdf) '
                    'is not installed.')
        receipt.say('Run the setup paste from README-PLAIN.txt once, '
                    'then run the Diver again.')
        receipt.save('receipt-stopped.txt')
        return 2
    jobs_file = os.path.join(HERE, 'jobs.txt')
    jobs = []
    with open(jobs_file, encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if line and not line.startswith('#'):
                jobs.append(line)
    if not jobs:
        receipt.say('No jobs in jobs.txt (every line is blank or a # note).')
        receipt.save('receipt-empty.txt')
        return 0
    t_all = time.time()
    for line in jobs:
        t0 = time.time()
        receipt.say('')
        parts = line.split()
        cmd = parts[0].lower()
        if cmd == 'fetch' and len(parts) >= 3:
            job_fetch(parts[1], parts[2], receipt)
        elif cmd == 'search':
            limit = 0
            q = line[len('search'):].strip()
            if ' limit=' in q:
                q, tail = q.rsplit(' limit=', 1)
                limit = int(tail.strip())
            # last token is the shelf name
            qparts = q.rsplit(None, 1)
            query, shelf = qparts[0], qparts[1]
            job_search(query, shelf, receipt, limit)
        else:
            receipt.gap(f'JOB LINE NOT UNDERSTOOD (skipped): {line}')
        receipt.say(f'  [job took {time.time()-t0:.1f}s]')
    receipt.say('')
    receipt.say('-' * 64)
    receipt.say(f'DONE. Kept {receipt.kept} new document(s), '
                f'{receipt.dupes} duplicate(s) already in the pond, '
                f'{receipt.gaps} gap(s) written to gaps.log.')
    receipt.say(f'Total run time: {time.time()-t_all:.1f}s. '
                f'The pond now holds what index.csv says it holds — no more, no less.')
    path = receipt.save(time.strftime('receipt-%Y%m%d-%H%M%S.txt'))
    receipt.say(f'Receipt saved: {path}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
