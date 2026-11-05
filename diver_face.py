#!/usr/bin/env python3
"""THE DEEP DIVER - the eternal window (face v1.2)

One dark window the owner sits at and hunts from: type the hunt, the
Diver knocks on the catalogues, brings back the candidates, the owner
picks, and the engine - dive.py, UNCHANGED, proven on Center
2026-11-05 - fetches, reads, fingerprints, files and receipts exactly
as it does from jobs.txt. This file is the face only. It imports the
engine and calls its heart (file_document) so the rules can never
drift apart.

Downloads are DATA. They are read, never run. Fetches stay on the
engine's allowed hosts. Colour schemes are switchable; new ones can
arrive as one-line MUSE1 colour lines, checked at the door - data,
never code (see STANDARDS.md and the how-to inside the Colours room).
"""
import importlib.util
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
import tkinter as tk
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
PREFS = os.path.join(HERE, 'face-prefs.json')

# ------------------------------------------------ the engine, imported
_spec = importlib.util.spec_from_file_location(
    'dive', os.path.join(HERE, 'dive.py'))
dive = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dive)

# ------------------------------------------------ colour wardrobe
BUILTIN_SCHEMES = [
    {'name': 'Plankton', 'wall': '#041E26', 'panel': '#07303C',
     'accent': '#57E6B8', 'accent2': '#FF9E7A', 'text': '#EAFBF3',
     'motes': ['#57E6B8', '#FF9E7A']},
    {'name': 'Jellyfish', 'wall': '#1B0F22', 'panel': '#2A1535',
     'accent': '#FF7AC1', 'accent2': '#59E3FF', 'text': '#FDEFF7',
     'motes': ['#FF7AC1', '#59E3FF']},
    {'name': 'Pond Lantern', 'wall': '#081A0B', 'panel': '#0F2C12',
     'accent': '#B7F04A', 'accent2': '#FFB35C', 'text': '#F6F0DC',
     'motes': ['#B7F04A', '#FFB35C']},
    {'name': 'Bubble Bath', 'wall': '#071426', 'panel': '#0D2138',
     'accent': '#8FD0FF', 'accent2': '#FFB59E', 'text': '#EAF4FF',
     'motes': ['#8FD0FF', '#FFB59E']},
]

COUNTRIES = [
    'United States', 'Canada', 'Mexico', 'United Kingdom', 'Ireland',
    'France', 'Germany', 'Spain', 'Portugal', 'Italy', 'Netherlands',
    'Belgium', 'Switzerland', 'Austria', 'Poland', 'Czechia',
    'Slovakia', 'Hungary', 'Romania', 'Bulgaria', 'Greece', 'Turkey',
    'Sweden', 'Norway', 'Denmark', 'Finland', 'Iceland', 'Estonia',
    'Latvia', 'Lithuania', 'Ukraine', 'Russia', 'Israel', 'Egypt',
    'Morocco', 'Algeria', 'Tunisia', 'Nigeria', 'Kenya', 'Ethiopia',
    'Ghana', 'South Africa', 'Saudi Arabia', 'United Arab Emirates',
    'Iraq', 'Iran', 'Pakistan', 'India', 'Bangladesh', 'Sri Lanka',
    'Nepal', 'Thailand', 'Vietnam', 'Cambodia', 'Laos', 'Myanmar',
    'Malaysia', 'Singapore', 'Indonesia', 'Philippines', 'China',
    'Taiwan', 'Japan', 'South Korea', 'Mongolia', 'Australia',
    'New Zealand', 'Brazil', 'Argentina', 'Chile', 'Peru', 'Colombia',
    'Venezuela', 'Ecuador', 'Bolivia', 'Paraguay', 'Uruguay', 'Cuba',
    'Jamaica', 'Haiti', 'Dominican Republic', 'Guatemala', 'Honduras',
    'El Salvador', 'Nicaragua', 'Costa Rica', 'Panama', 'Norway',
    'Croatia', 'Serbia', 'Slovenia', 'Bosnia and Herzegovina',
    'Montenegro', 'North Macedonia', 'Albania', 'Malta', 'Cyprus',
    'Luxembourg', 'Liechtenstein', 'Andorra', 'Monaco',
    'Another country (my chart still works - the fleets are listed '
    'in HARBOURS.md)',
]

# ------------------------------------------------ the Muse Line door
def _lum(hexcolor):
    h = hexcolor.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    def f(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


HEX = re.compile(r'^#[0-9A-Fa-f]{6}$')


def parse_muse_line(line):
    """Check a MUSE1 colour line at the door. Returns (scheme, None)
    or (None, plain-words refusal). Colours are read as DATA only."""
    line = (line or '').strip()
    if not line.startswith('MUSE1|'):
        return None, 'That line does not start with MUSE1| - it is ' \
                     'not a Muse colour line. Nothing was changed.'
    parts = line.split('|')
    if len(parts) != 8:
        return None, 'That line has the wrong number of pieces - ' \
                     'a Muse line has 8. Nothing was changed.'
    name = parts[1].strip()
    if not name or len(name) > 28 or not re.match(
            r"^[A-Za-z0-9 '\-]+$", name):
        return None, 'The scheme name must be plain letters, numbers ' \
                     'and spaces, up to 28 characters. Nothing changed.'
    keys = ['wall', 'panel', 'accent', 'accent2', 'text']
    scheme = {'name': name}
    for part, key in zip(parts[2:7], keys):
        m = re.match(r'^' + key + r'\s+(#[0-9A-Fa-f]{6})$', part.strip())
        if not m:
            return None, f'The {key} piece is not shaped like ' \
                         f'"{key} #RRGGBB". Nothing was changed.'
        scheme[key] = m.group(1).upper()
    m = re.match(r'^motes\s+(#[0-9A-Fa-f]{6}),(#[0-9A-Fa-f]{6})$',
                 parts[7].strip())
    if not m:
        return None, 'The motes piece must be two colours like ' \
                     '"motes #RRGGBB,#RRGGBB". Nothing was changed.'
    scheme['motes'] = [m.group(1).upper(), m.group(2).upper()]
    if _lum(scheme['wall']) > 0.05:
        return None, 'The wall colour is not dark enough - this ' \
                     'house wears dark walls only. Nothing changed.'
    if _contrast(scheme['text'], scheme['wall']) < 4.5:
        return None, 'The text colour would be hard to read on that ' \
                     'wall. Nothing was changed.'
    return scheme, None


SAMPLE_BLOCK = (
    'Make me a colour scheme for my app. Give me back ONE line only, '
    'in exactly this shape:\n\n'
    'MUSE1|<a name>|wall #000000|panel #000000|accent #000000|'
    'accent2 #000000|text #000000|motes #000000,#000000\n\n'
    'Use real hex colours instead of the zeros. The wall must be '
    'very dark, the text must be light and easy to read on the wall, '
    'and the two motes colours should match the accents.\n\n'
    'Here is a real line that works, so you can see the shape:\n\n'
    'MUSE1|Plankton|wall #041E26|panel #07303C|accent #57E6B8|'
    'accent2 #FF9E7A|text #EAFBF3|motes #57E6B8,#FF9E7A')

HOWTO_TEXT = """Add a colour scheme from Muse

Want a new look? Ask Muse for a colour scheme - you'll get back
one line that starts with MUSE1|.

Copy the whole line. Come back here, paste the line in, and tap
Check it.

The app reads the colours, checks they're dark and easy to read,
and adds the scheme to your list. A scheme line is only colours -
it can't change anything else in the app.

Tap the scheme's name any time to wear it.

Don't have a line yet? Copy the sample block below and give it to
your Muse. It shows the shape, so the line your Muse makes will
fit first try.


Why you carry it yourself

This app doesn't fetch schemes on its own - it has no account for
that, and it wouldn't do it unseen if it could.

You carry the line both ways, so you see exactly what goes out and
exactly what comes back - and nothing changes here until you tap
Check it.

Your hand is the bridge. That's on purpose."""


# ------------------------------------------------ headless core
# These functions never touch tkinter, so the desk can test them
# without a window. sink is any object with .say(str).

def search_catalogue(words, scope, sink, rows=50):
    """Knock on the catalogue. Returns a list of candidate dicts."""
    words = ' '.join((words or '').split())
    if not words:
        sink.say('Type what you are hunting for first.')
        return []
    q = (f'(title:({words}) OR creator:({words}) '
         f'OR description:({words})) AND mediatype:texts')
    if scope == 'reading-room':
        q += ' AND collection:ciareadingroom'
    params = [('q', q), ('fl[]', 'identifier'), ('fl[]', 'title'),
              ('fl[]', 'date'), ('fl[]', 'creator'),
              ('rows', rows), ('output', 'json')]
    url = 'https://archive.org/advancedsearch.php?' + \
        urllib.parse.urlencode(params)
    try:
        docs = dive.get_json(url)['response']['docs']
    except Exception as e:
        sink.say(f'The catalogue did not answer: {e}')
        return []
    out = []
    for d in docs:
        title = str(d.get('title') or d['identifier']).strip()
        date = str(d.get('date') or '')[:10]
        out.append({'identifier': d['identifier'], 'title': title,
                    'date': date})
    return out


class FaceReceipt:
    """The engine's Receipt shape, speaking into the window instead
    of the black console. Gaps still land in gaps.log."""

    def __init__(self, sink):
        self.sink = sink
        self.lines = []
        self.kept = 0
        self.dupes = 0
        self.gaps = 0

    def say(self, s=''):
        self.lines.append(s)
        self.sink.say(s)

    def gap(self, s):
        self.gaps += 1
        self.say('  GAP: ' + s)
        with open(dive.GAPS, 'a', encoding='utf-8') as f:
            f.write(f'{dive.stamp()}  {s}\n')

    def save(self):
        os.makedirs(dive.RECEIPTS, exist_ok=True)
        name = time.strftime('receipt-%Y%m%d-%H%M%S.txt')
        path = os.path.join(dive.RECEIPTS, 'face-' + name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.lines) + '\n')
        return path


def dive_candidate(ident, title, date, shelf, receipt):
    """Fetch one chosen candidate through the engine's own rules:
    metadata, biggest honest PDF, verify by reading, fingerprint,
    file. Mirrors dive.job_search's per-item path exactly."""
    try:
        meta = dive.get_json(f'https://archive.org/metadata/{ident}')
    except Exception as e:
        receipt.gap(f'METADATA FAILED: {ident} - {e}')
        return
    pdfs = [f for f in meta.get('files', [])
            if f.get('name', '').lower().endswith('.pdf')]
    text_pdfs = [f for f in pdfs
                 if f.get('name', '').lower().endswith('_text.pdf')]
    plain_pdfs = [f for f in pdfs if f not in text_pdfs]
    pool = text_pdfs or plain_pdfs
    if not pool:
        receipt.gap(f'NO PDF ON THE ITEM: {ident} - {title}')
        return
    pool.sort(key=lambda f: int(f.get('size', 0) or 0), reverse=True)
    fname = pool[0]['name']
    dl = f'https://archive.org/download/{ident}/' + \
        urllib.parse.quote(fname)
    data = dive.fetch_bytes(dl, receipt)
    if data is None:
        return
    dive.file_document(data, title, dl, shelf, date, receipt)


def pond_summary():
    """Count the pond from index.csv - the pond holds what the
    index says it holds, no more, no less."""
    import csv
    if not os.path.exists(dive.INDEX):
        return 'The pond is empty. Nothing has been caught yet.'
    shelves = {}
    total = 0
    with open(dive.INDEX, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            shelves[row.get('shelf', '?')] = \
                shelves.get(row.get('shelf', '?'), 0) + 1
            total += 1
    parts = ', '.join(f'{k}: {v}' for k, v in sorted(shelves.items()))
    return f'The pond holds {total} document(s) - {parts}.'


# ------------------------------------------------ preferences
def load_prefs():
    prefs = {'home': None, 'scheme': 'Plankton', 'motes': True,
             'customs': []}
    if os.path.exists(PREFS):
        try:
            with open(PREFS, encoding='utf-8') as f:
                prefs.update(json.load(f))
        except Exception:
            pass
    return prefs


def save_prefs(prefs):
    with open(PREFS, 'w', encoding='utf-8') as f:
        json.dump(prefs, f, indent=1)


def all_schemes(prefs):
    return BUILTIN_SCHEMES + prefs.get('customs', [])


def get_scheme(prefs):
    for s in all_schemes(prefs):
        if s['name'] == prefs.get('scheme'):
            return s
    return BUILTIN_SCHEMES[0]


# ------------------------------------------------ the window
class Face:
    def __init__(self, root):
        self.root = root
        self.prefs = load_prefs()
        self.scheme = get_scheme(self.prefs)
        self.q = queue.Queue()
        self.candidates = []
        self.busy = False
        self.tip_btns = []
        self.mote_dots = []
        root.title('The Deep Diver')
        try:
            self.icon_img = tk.PhotoImage(
                file=os.path.join(HERE, 'deep-diver-icon-512.png'))
            root.iconphoto(True, self.icon_img)
        except Exception:
            self.icon_img = None
        self.build()
        self.apply_scheme()
        self.refresh_pond()
        self.say('The eternal window is open. Type what you are '
                 'hunting for, and he will knock on the catalogues.')
        if not self.prefs.get('home'):
            self.root.after(400, self.ask_home)
        self.root.after(120, self.drain)
        self.root.after(200, self.mote_tick)

    # ---------- layout
    def build(self):
        s = self.scheme
        top = tk.Frame(self.root)
        top.pack(fill='x')
        self.top = top
        if self.icon_img is not None:
            small = self.icon_img.subsample(8, 8)
            self.icon_lbl = tk.Label(top, image=small)
            self.icon_lbl.image = small
            self.icon_lbl.pack(side='left', padx=(12, 4), pady=8)
        self.title_lbl = tk.Label(
            top, text='THE DEEP DIVER', font=('Segoe UI', 20, 'bold'))
        self.title_lbl.pack(side='left', padx=6, pady=8)
        self.colours_btn = tk.Button(
            top, text='Colours', font=('Segoe UI', 11),
            command=self.open_colours)
        self.colours_btn.pack(side='right', padx=12, pady=8)
        self.motes_canvas = tk.Canvas(self.root, height=40,
                                      highlightthickness=0)
        self.motes_canvas.pack(fill='x')

        mid = tk.Frame(self.root)
        mid.pack(fill='x', padx=14, pady=(8, 2))
        self.mid = mid
        self.ask_lbl = tk.Label(mid, text='What should he dive for?',
                                font=('Segoe UI', 14, 'bold'))
        self.ask_lbl.pack(anchor='w')
        row = tk.Frame(mid)
        row.pack(fill='x', pady=6)
        self.row = row
        self.query = tk.Entry(row, font=('Segoe UI', 14))
        self.query.pack(side='left', fill='x', expand=True)
        self.query.bind('<Return>', lambda e: self.on_search())
        self.search_btn = tk.Button(
            row, text='SEARCH', font=('Segoe UI', 13, 'bold'),
            command=self.on_search)
        self.search_btn.pack(side='left', padx=(8, 0))
        row2 = tk.Frame(mid)
        row2.pack(fill='x')
        self.row2 = row2
        self.scope_var = tk.StringVar(value='Everywhere he can knock')
        if self.prefs.get('home') == 'United States':
            self.scope_var.set('The Reading Room shelf')
        self.scope_menu = tk.OptionMenu(
            row2, self.scope_var, 'Everywhere he can knock',
            'The Reading Room shelf')
        self.scope_menu.config(font=('Segoe UI', 11))
        self.scope_menu.pack(side='left')
        self.shelf_lbl = tk.Label(row2, text='  Shelf name:',
                                  font=('Segoe UI', 11))
        self.shelf_lbl.pack(side='left')
        self.shelf = tk.Entry(row2, font=('Segoe UI', 11), width=18)
        self.shelf.insert(0, 'window')
        self.shelf.pack(side='left', padx=(4, 8))
        self.dive_btn = tk.Button(
            row2, text='DIVE - fetch the picked ones',
            font=('Segoe UI', 12, 'bold'), command=self.on_dive)
        self.dive_btn.pack(side='left')
        self.home_lbl = tk.Label(mid, font=('Segoe UI', 10))
        self.home_lbl.pack(anchor='w', pady=(4, 0))
        self.update_home_lbl()

        self.results = tk.Listbox(
            self.root, font=('Segoe UI', 11), selectmode='extended',
            activestyle='none', height=13)
        self.results.pack(fill='both', expand=True, padx=14, pady=8)

        low = tk.Frame(self.root)
        low.pack(fill='both', padx=14, pady=(0, 6))
        self.low = low
        self.jobs_btn = tk.Button(
            low, text='Run the job list (jobs.txt)',
            font=('Segoe UI', 11), command=self.on_jobs)
        self.jobs_btn.pack(anchor='w')
        self.pond_lbl = tk.Label(low, font=('Segoe UI', 11),
                                 justify='left', wraplength=900)
        self.pond_lbl.pack(anchor='w', pady=(4, 2))
        self.log = tk.Text(self.root, height=9, font=('Consolas', 10),
                           wrap='word', state='disabled')
        self.log.pack(fill='both', padx=14, pady=(0, 2))
        tiprow = tk.Frame(self.root)
        tiprow.pack(fill='x', padx=14, pady=(0, 10))
        self.tiprow = tiprow
        self.tip_lbl = tk.Label(
            tiprow, text="He's free, and he stays free.",
            font=('Segoe UI', 10))
        self.tip_lbl.pack(side='left')
        btn = tk.Button(
            tiprow, text='💸 Tip the Diver',
            font=('Segoe UI', 10, 'bold'), command=self.open_tip)
        btn.pack(side='left', padx=(8, 0))
        self.tip_btns.append(btn)

    def update_home_lbl(self):
        home = self.prefs.get('home')
        if home:
            self.home_lbl.config(
                text=f'Home waters: {home} - your chart leads with '
                     f'your home fleet (HARBOURS.md).')
        else:
            self.home_lbl.config(text='')

    def open_tip(self):
        import webbrowser
        webbrowser.open('https://cash.app/$streamplay')

    # ---------- colours
    def apply_scheme(self):
        s = self.scheme
        self.root.config(bg=s['wall'])
        for w in (self.top, self.mid, self.row, self.row2, self.low,
                  self.tiprow):
            w.config(bg=s['wall'])
        self.tip_lbl.config(bg=s['wall'], fg=s['text'])
        for b in self.tip_btns:
            b.config(bg=s['panel'], fg=s['text'],
                     activebackground=s['accent'])
        for w in (self.title_lbl, self.ask_lbl, self.shelf_lbl,
                  self.home_lbl, self.pond_lbl):
            w.config(bg=s['wall'], fg=s['text'])
        if self.icon_img is not None:
            self.icon_lbl.config(bg=s['wall'])
        self.motes_canvas.config(bg=s['wall'])
        for b in (self.search_btn, self.dive_btn):
            b.config(bg=s['accent2'], fg='#101418',
                     activebackground=s['accent'],
                     font=('Segoe UI', 12, 'bold'))
        for b in (self.colours_btn, self.jobs_btn):
            b.config(bg=s['panel'], fg=s['text'],
                     activebackground=s['accent'])
        for e in (self.query, self.shelf):
            e.config(bg=s['panel'], fg=s['text'],
                     insertbackground=s['text'])
        self.scope_menu.config(bg=s['panel'], fg=s['text'],
                               activebackground=s['accent'])
        self.scope_menu['menu'].config(bg=s['panel'], fg=s['text'])
        self.results.config(bg=s['panel'], fg=s['text'],
                            selectbackground=s['accent'],
                            selectforeground='#101418')
        self.log.config(bg=s['panel'], fg=s['text'],
                        insertbackground=s['text'])
        self.mote_dots = []

    def open_colours(self):
        s = self.scheme
        win = tk.Toplevel(self.root)
        win.title('Colours')
        win.config(bg=s['wall'])
        tk.Label(win, text='Wear a scheme:', bg=s['wall'],
                 fg=s['text'], font=('Segoe UI', 12, 'bold')).pack(
                     anchor='w', padx=14, pady=(12, 4))
        for sch in all_schemes(self.prefs):
            tk.Button(
                win, text=sch['name'], font=('Segoe UI', 11),
                bg=sch['panel'], fg=sch['text'],
                activebackground=sch['accent'],
                command=lambda n=sch['name']: self.wear(n, win)).pack(
                    fill='x', padx=14, pady=2)
        self.motes_var = tk.BooleanVar(value=self.prefs.get('motes',
                                                             True))
        tk.Checkbutton(
            win, text='Sparkle motes (gentle drift, never flashing)',
            variable=self.motes_var, bg=s['wall'], fg=s['text'],
            selectcolor=s['panel'], activebackground=s['wall'],
            activeforeground=s['text'], font=('Segoe UI', 11),
            command=self.toggle_motes).pack(anchor='w', padx=14,
                                            pady=(10, 2))
        tk.Label(win, text='Add a scheme from Muse - paste the '
                           'MUSE1 line:', bg=s['wall'], fg=s['text'],
                 font=('Segoe UI', 12, 'bold')).pack(
                     anchor='w', padx=14, pady=(12, 4))
        entry = tk.Entry(win, font=('Consolas', 10), width=86,
                         bg=s['panel'], fg=s['text'],
                         insertbackground=s['text'])
        entry.pack(padx=14, fill='x')
        verdict = tk.Label(win, bg=s['wall'], fg=s['accent'],
                           font=('Segoe UI', 11), wraplength=760,
                           justify='left')
        verdict.pack(anchor='w', padx=14, pady=4)

        def check_it():
            scheme, err = parse_muse_line(entry.get())
            if err:
                verdict.config(text=err, fg=s['accent2'])
                return
            self.prefs['customs'] = [
                c for c in self.prefs.get('customs', [])
                if c['name'] != scheme['name']] + [scheme]
            save_prefs(self.prefs)
            verdict.config(
                text=f'"{scheme["name"]}" passed the door and joined '
                     f'your wardrobe. Tap its name above to wear it.',
                fg=s['accent'])
            win.after(900, lambda: (win.destroy(),
                                    self.open_colours()))
        tk.Button(win, text='Check it', font=('Segoe UI', 11, 'bold'),
                  bg=s['accent2'], fg='#101418',
                  command=check_it).pack(padx=14, pady=2, anchor='w')
        how = tk.Text(win, height=16, width=86, font=('Segoe UI', 10),
                      wrap='word', bg=s['panel'], fg=s['text'])
        how.insert('1.0', HOWTO_TEXT + '\n\n----\nGive this to your '
                          'Muse (copy the block):\n\n' + SAMPLE_BLOCK)
        how.config(state='disabled')
        how.pack(padx=14, pady=(8, 4))

        def copy_sample():
            self.root.clipboard_clear()
            self.root.clipboard_append(SAMPLE_BLOCK)
            verdict.config(text='Sample block copied - paste it to '
                                'your Muse.', fg=s['accent'])
        tk.Button(win, text='Copy the sample block',
                  font=('Segoe UI', 11), bg=s['panel'], fg=s['text'],
                  command=copy_sample).pack(padx=14, pady=(0, 12),
                                            anchor='w')

    def wear(self, name, win=None):
        self.prefs['scheme'] = name
        save_prefs(self.prefs)
        self.scheme = get_scheme(self.prefs)
        self.apply_scheme()
        if win is not None:
            win.destroy()

    def toggle_motes(self):
        self.prefs['motes'] = bool(self.motes_var.get())
        save_prefs(self.prefs)
        if not self.prefs['motes']:
            self.motes_canvas.delete('all')
            self.mote_dots = []

    # ---------- motes (Glitter Rule: gentle, scheme-tinted)
    def mote_tick(self):
        try:
            if self.prefs.get('motes', True):
                c = self.motes_canvas
                w = max(c.winfo_width(), 200)
                if len(self.mote_dots) < 26:
                    import random
                    x = random.uniform(6, w - 6)
                    col = self.scheme['motes'][
                        len(self.mote_dots) % len(self.scheme['motes'])]
                    oid = c.create_oval(x - 2, 44, x + 2, 48,
                                        fill=col, outline='')
                    self.mote_dots.append([oid, x, 46.0, 0.0])
                import random
                for d in self.mote_dots:
                    d[2] -= 0.35
                    d[3] += random.uniform(-0.15, 0.15)
                    d[1] += d[3] * 0.2
                    c.coords(d[0], d[1] - 2, d[2] - 2, d[1] + 2,
                             d[2] + 2)
                    if d[2] < -4:
                        d[2] = 48.0
        except tk.TclError:
            return
        self.root.after(90, self.mote_tick)

    # ---------- home waters (asked once)
    def ask_home(self):
        s = self.scheme
        win = tk.Toplevel(self.root)
        win.title('Home waters')
        win.config(bg=s['wall'])
        tk.Label(win, text='One question, asked once: where is home?\n'
                           'Your harbour chart will lead with your '
                           'home fleet.\nThis is a preference saved on '
                           'this machine only -\nno GPS, no tracking, '
                           'nothing leaves the house.',
                 bg=s['wall'], fg=s['text'], font=('Segoe UI', 12),
                 justify='left').pack(padx=16, pady=12)
        lb = tk.Listbox(win, height=12, width=44,
                        font=('Segoe UI', 11), bg=s['panel'],
                        fg=s['text'], selectbackground=s['accent'],
                        selectforeground='#101418')
        for cname in COUNTRIES:
            lb.insert('end', cname)
        lb.pack(padx=16)

        def pick():
            sel = lb.curselection()
            if sel:
                self.prefs['home'] = lb.get(sel[0])
                save_prefs(self.prefs)
                self.update_home_lbl()
                if self.prefs['home'] == 'United States':
                    self.scope_var.set('The Reading Room shelf')
            win.destroy()
        tk.Button(win, text='That is home', font=('Segoe UI', 12,
                  'bold'), bg=s['accent2'], fg='#101418',
                  command=pick).pack(pady=12)

    # ---------- work
    def say(self, s=''):
        self.log.config(state='normal')
        self.log.insert('end', s + '\n')
        self.log.see('end')
        self.log.config(state='disabled')

    def drain(self):
        try:
            while True:
                kind, payload = self.q.get_nowait()
                if kind == 'say':
                    self.say(payload)
                elif kind == 'results':
                    self.show_results(payload)
                elif kind == 'done':
                    self.busy = False
                    self.refresh_pond()
                elif kind == 'pond':
                    self.pond_lbl.config(text=payload)
        except queue.Empty:
            pass
        self.root.after(120, self.drain)

    class QSink:
        def __init__(self, q):
            self.q = q

        def say(self, s=''):
            self.q.put(('say', s))

    def on_search(self):
        if self.busy:
            return
        words = self.query.get().strip()
        if not words:
            self.say('Type what you are hunting for first.')
            return
        scope = 'reading-room' if self.scope_var.get().startswith(
            'The Reading Room') else 'all'
        self.busy = True
        self.say(f'Knocking on the catalogues for: {words} ...')

        def work():
            sink = Face.QSink(self.q)
            cands = search_catalogue(words, scope, sink)
            self.q.put(('results', cands))
            self.q.put(('done', None))
        threading.Thread(target=work, daemon=True).start()

    def show_results(self, cands):
        self.candidates = cands
        self.results.delete(0, 'end')
        for c in cands:
            d = f'  ({c["date"]})' if c['date'] else ''
            self.results.insert('end', f'{c["title"]}{d}')
        if cands:
            self.say(f'{len(cands)} candidate(s) on the list. Click '
                     f'the ones you want - Ctrl and Shift pick '
                     f'several - then press DIVE.')
        else:
            self.say('No candidates came back. Try plainer or fewer '
                     'words.')

    def on_dive(self):
        if self.busy:
            return
        sel = self.results.curselection()
        if not sel:
            self.say('Pick at least one candidate from the list '
                     'first - the dive is your press.')
            return
        shelf = self.shelf.get().strip() or 'window'
        picked = [self.candidates[i] for i in sel]
        self.busy = True

        def work():
            sink = Face.QSink(self.q)
            receipt = FaceReceipt(sink)
            receipt.say('')
            receipt.say('=' * 56)
            receipt.say(f'THE DEEP DIVER - window dive, '
                        f'{dive.stamp()}')
            for c in picked:
                receipt.say(f'DIVING for: {c["title"]}')
                dive_candidate(c['identifier'], c['title'],
                               c['date'], shelf, receipt)
            receipt.say('-' * 56)
            receipt.say(f'DONE. Kept {receipt.kept} new, '
                        f'{receipt.dupes} duplicate(s), '
                        f'{receipt.gaps} gap(s) in gaps.log.')
            path = receipt.save()
            sink.say(f'Receipt saved: {path}')
            self.q.put(('done', None))
        threading.Thread(target=work, daemon=True).start()

    def on_jobs(self):
        if self.busy:
            return
        self.busy = True
        self.say('Running the job list - the engine, in its own '
                 'voice:')

        def work():
            sink = Face.QSink(self.q)
            try:
                proc = subprocess.Popen(
                    [sys.executable,
                     os.path.join(HERE, 'dive.py')],
                    cwd=HERE, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True,
                    encoding='utf-8', errors='replace')
                for line in proc.stdout:
                    sink.say(line.rstrip())
                proc.wait()
            except Exception as e:
                sink.say(f'The job list would not run: {e}')
            self.q.put(('done', None))
        threading.Thread(target=work, daemon=True).start()

    def refresh_pond(self):
        try:
            self.pond_lbl.config(text=pond_summary())
        except Exception:
            pass


def main():
    if not dive.need_pypdf():
        root = tk.Tk()
        root.title('The Deep Diver')
        tk.Label(root, text='The text-reading part (pypdf) is not '
                            'installed.\nRun INSTALL.bat once - the '
                            'doorman lays it in - then open him again.',
                 font=('Segoe UI', 12), padx=20, pady=20).pack()
        root.mainloop()
        return 2
    root = tk.Tk()
    root.geometry('960x760')
    Face(root)
    root.mainloop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
