<p align="center">
  <img src="deep-diver-icon-512.png" width="220" alt="The Deep Diver — a smiling diver in a mint-teal helmet">
</p>

# The Deep Diver

> *Let's find all the hidden digital knowledge.*

## Tip jar

Free forever — and a tip is never asked for before the work can be
inspected. Run him first. Dive with him. Check the pond yourself.
If he earned it, the jar is here — tip once, tip again next month,
or never; he works exactly the same either way:

<p align="center">
  <a href="https://cash.app/$streamplay"><strong>💸 Tip the Diver</strong></a>
</p>

One button. It opens Cash App — you pick the amount there and
confirm.

**A small, honest archive diver for Windows.**

The Deep Diver fetches documents from the world's public archives —
declassified government paper, technical reports, trade journals,
books — and files them on *your* machine, in a pond you own. He reads
every document before he keeps it, fingerprints everything so nothing
is ever filed twice, and writes down everything he *couldn't* reach
in a gaps ledger. A dive that hides its gaps is lying about its
coverage; this one doesn't.

He was built to a bar: *an equal in standards and quality of search —
not in speed.* Speed is not on the standards page. Honesty is.

## What he does

- **Dives by catalogue, not by crawl.** Archives are harbours with
  indexes. He queries the catalogue (or fetches a document by its
  exact address), then opens and reads it before keeping it.
- **Verify by reading.** A file that won't open, or carries no
  readable text, is not in the pond — it's in `gaps.log`, with its
  reason.
- **Fingerprint everything.** Every kept document is SHA-256 hashed.
  The same fingerprint twice is a duplicate, said out loud.
- **Provenance on every line.** Title, source, shelf, date, pages,
  words, fingerprint — every index line traces back to its shelf.
- **Receipts a tired human can read at 2 a.m.** What was kept, what
  was already there, what's missing, and how long it took.

## His waters

v1 dives **archive.org** (including the CIA Reading Room mirror
collection) and **cia.gov**. The full chart — nine fleets of the
world's archives, each marked Open, Mixed, Index-only, or Locked —
is in [HARBOURS.md](HARBOURS.md), including the **Home Waters** rule:
tell him your home country once and the chart leads with *your*
closer archives. Home first, never home only.

Some waters are **forbidden, permanently**, and they're listed in
writing in [STANDARDS.md](STANDARDS.md): the dark web, executable
content, and people-collections (leaked personal data and breach
dumps). Locked means locked everywhere else, too — no logins, no
paywall or lending-lock bypass, no credentials, ever.

## His standards

The seven laws he runs under — primary paper first, verify by
reading, fingerprint everything, gaps written down never silent,
provenance on every line, downloads are data never programs, and
*the Diver files evidence; the human judges* — are in
[STANDARDS.md](STANDARDS.md).

## Running him (v1)

You need Windows and Python 3.

1. Download the release zip and unzip it anywhere.
2. Double-click **INSTALL.bat** — the doorman. One press starts the
   install: he finds Python, installs the text-reading part (pypdf),
   lays the Diver in `D:\deep-diver`, makes a desktop shortcut
   wearing his face, verifies every piece, and writes
   `install-receipt.txt`. (First press only, SmartScreen may ask
   "Run anyway" — an unsigned file meeting its owner for the first
   time. No Python? He stops clean and says so in the receipt.)
3. Double-click the **Deep Diver** desktop shortcut — his window
   opens. Type what you are hunting for, press **SEARCH**, pick
   from the candidates he brings back, press **DIVE**. He leaves
   his catch in `pond\`, his index in `index.csv`, and a receipt
   in `receipts\`.
4. For set work, edit `jobs.txt` (plain words inside; one job per
   line, `#` turns a line off) and double-click **DIVE.bat** — or
   press "Run the job list" inside the window.

## Honest status

- The engine is proven end-to-end on real hardware (first dive: a
  declassified 1962 intelligence checklist, kept, fingerprinted,
  receipted). As of 1.2 he wears his window — the eternal window:
  type the hunt, get candidates, pick, dive — with switchable
  colour schemes and Muse Line schemes checked at the door. The
  window calls the same engine; nothing underneath changed.
- He reads documents that already have a **text layer**. Scanned
  image-only paper is logged as a gap, not silently skipped; OCR is
  future work.
- cia.gov's own document route answers a plain program with a web
  page instead of the file, so Reading Room documents are fetched
  from archive.org's mirror of the same collection — disclosed in
  STANDARDS.md, not hidden.

## A note on colours

His face speaks **Muse Line**: any Muse can
design a colour scheme for him and hand it over as one rigid,
colours-only line of text — carried by the human, checked at the door
against the dark-and-readable rules, never executed as code. Nothing
about him phones home to anyone's AI. The human is the bridge, on
purpose.

## License

MIT. Built by **Songwright**.
