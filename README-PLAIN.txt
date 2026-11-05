THE DEEP DIVER v1.2 — plain-words readme
=========================================

WHAT IT IS
Your PC doing the desk's archival legwork, to the desk's standards
(STANDARDS.md is the whole bar, in writing). It fetches documents,
opens and READS each one before counting it, fingerprints it, files
it in the pond, keeps an honest index and an honest gaps list, and
prints a receipt with timings. It judges nothing — story-versus-paper
stays the desk's job. Downloads are data: read, never run.

SETUP (once) - the doorman starts the install
1. Unzip deep-diver-1.2.zip anywhere (your Downloads folder is fine).
2. Double-click INSTALL.bat - the doorman. He SCREAMS it, on
   purpose: first file in the pack, banner in the window. One
   press starts the install: he finds Python, installs the
   text-reading part (pypdf), lays the Diver in D:\deep-diver\,
   makes a desktop shortcut wearing the Diver's face, checks
   every piece, and writes install-receipt.txt saying exactly
   what he did.
   First press only: Windows may show "Windows protected your
   PC" - that is SmartScreen meeting a new unsigned file.
   "More info" -> "Run anyway" is the owner's press, and it is
   the only extra one.
   If Python is not on the machine he stops clean, installs
   nothing, and the receipt says so (get Python free from
   python.org, tick "Add python.exe to PATH", then press
   INSTALL again - safe to re-run; your pond, index and
   receipts are never touched).
3. Run him from the "Deep Diver" desktop shortcut - his window
   opens. Deleting the folder is the uninstall.

RUN IT - THE WINDOW
Double-click the "Deep Diver" shortcut on the desktop. His window
opens under the line: Let's find all the hidden digital knowledge.
Type what you hunt in plain words, press SEARCH, and he knocks on
the catalogues and brings back candidates with titles and dates.
Click the ones you want (Ctrl and Shift pick several), name a
shelf if you like, and press DIVE - that press is yours. He
fetches, reads, fingerprints and files into the pond, and the
receipt shows in the window and saves in the receipts\ folder.
First open only, he asks your home country once, so your chart
can lead with your home fleet - a preference on this machine,
never a location.
Colours: press Colours in the window. Four schemes are built in,
motes can be switched, and a new scheme can arrive as one line
from any Muse (the Colours room explains it, with a sample to
copy).

RUN IT - THE JOB LIST
For set work, double-click DIVE.bat inside D:\deep-diver (or the
"Run the job list" button in the window), or in CMD:
   cd /d D:\deep-diver
   python dive.py
It works through jobs.txt top to bottom and prints the receipt on
screen; the same receipt is saved in the receipts\ folder.

THE FIRST RUN — WHAT RIGHT LOOKS LIKE
Job 1 is the slice: one document, the President's Intelligence
Checklist of 13 October 1962, 7 pages. A passing run says KEPT with
7 pages and roughly 800 words, and finishes in well under a minute.
If it stops or gaps instead, the receipt and gaps.log say exactly
why, in plain words — send the desk the receipt text and it gets
named and fixed from there. Three fix rounds is the budget, same as
the spec you approved.

AFTER THE SLICE PASSES
Job 2 is already written in jobs.txt, switched off with a # —
Die-Cast Dive 2's downloadable scatter (everything the archive
dates 1970-1999). Take the # off the front of its line and run
again. Note the honest wrinkle in jobs.txt: on a fresh pond, items
Dive 1 already grabbed will be kept once here (fingerprints only
dedupe within this pond).

JOBS OF YOUR OWN
Add lines to jobs.txt in Notepad:
   fetch  <a document PDF url on archive.org or cia.gov>  <shelf>
   search <archive.org search words>  <shelf>
Shelves are just folder names in the pond. Any other host is
refused, and the refusal is written to gaps.log.

HONEST LIMITS OF v1
- Text layer only. A scanned document with no readable text is
  logged as a gap (OCR is a later slice, if called).
- The Reading Room shelf is archive.org's mirror of the CIA
  Reading Room collection — cia.gov's own document route hands a
  plain program a web page instead of the file. Same documents,
  fetchable shelf. The allowed hosts are listed in dive.py and in
  STANDARDS.md, in the open.
- No speed promises, by your ruling: the bar is standards.
