# THE DEEP DIVER — STANDARDS

*The bar, in the author's words (2026-11-05): "your equal as best it can —
not in speed, but in standards and quality of search." Speed is not on
this page. These are the rules the desk's own dives run under, written
down so the Diver runs under the same ones.*

## The seven laws

1. **Primary paper first.** Original documents outrank retellings,
   summaries, and other people's conclusions. When the paper and the
   story disagree, the paper is the evidence and the story is the claim.

2. **Verify by reading.** A document counts only after the Diver has
   opened it and pulled real text from it. A file that will not open,
   or that carries no readable text layer, is not in the pond — it is
   in the gaps ledger, with its reason. Names and listings are never
   taken as proof of contents.

3. **Fingerprint everything.** Every kept document is hashed
   (SHA-256). The same fingerprint arriving twice is a duplicate, said
   out loud, never silently filed twice.

4. **Gaps are written down, never silent.** Locked, missing, scan-only,
   too big, not a PDF, shelf unreachable — every failure lands in
   `gaps.log` with a date and a plain reason. A dive that hides its
   gaps is lying about its coverage.

5. **Provenance on every line.** Each index line carries title,
   source URL, shelf, the document's own date, page count, word count,
   fingerprint, and when it was fetched. Any line can be traced back
   to the shelf it came from.

6. **Downloads are data, never programs.** The Diver fetches documents
   (PDFs) from the allowed shelves only, writes only inside its own
   folder, and never executes anything it fetched — or anything else.

7. **The Diver files evidence; the desk judges.** Told-story versus
   paper is a judgment, and judgment is not delegated to the legwork.
   The Diver's receipt reports what exists, what was kept, and what is
   missing. It never summarises a document's meaning and never
   concludes anything about one.

## The shelves (v1)

- **archive.org** — including the CIA Reading Room mirror collection
  (`ciareadingroom`): the Reading Room's own documents. cia.gov's own
  document route answers a plain program with a web page instead of
  the file, so the mirror is where a program can honestly fetch them;
  the documents are the same collection.
- **cia.gov** — allowed, for any route that does serve a file.

Any other host is refused and the refusal is logged as a gap.

## The waters — charted, addable, and forbidden

*Added 2026-11-05 by design decision, written for the technical reader —
the ones who would know how to try the dangerous things, told plainly
why the chart says no.*

**The method, so the chart makes sense.** The Diver does not crawl
the open web and does not scrape search engines. Archives are
harbours, each with a catalogue; the Diver queries a harbour's
catalogue (or fetches a document by its exact address/identifier),
then verifies by reading (Law 2). "Everything" is not a place; a
specific file is found through the catalogue of the harbour that
holds it.

**Charted and dived (v1):** archive.org (including the CIA Reading
Room mirror) and cia.gov, per the shelves above.

**Addable harbours** — real water, each needing its own door module
plus a standards check before it joins the allowlist: the National
Archives (NARA) catalogue, DTIC (defence technical reports), the FBI
Vault and other agency FOIA reading rooms (NSA, State, DIA), 
HathiTrust and Google Books (largely index-only — a listing there
produces a lead or a gap, never a grab past a lending lock),
university, museum and company archives, and foreign national
archives. The full chart of harbours, fleet by fleet with access
classes, lives in HARBOURS.md. Locked is locked: an access control
is a wall, not a puzzle, and the Diver does not climb walls (no
logins, no paywall or lending-lock bypass, no credential use of
any kind).

**Forbidden waters — permanently off the chart:**

- **The dark web (Tor hidden services, .onion, and their kin).**
  Excluded in construction, not just in policy: the engine carries
  no Tor client and no proxy support, the jobs parser accepts only
  http(s) addresses on allowlisted hosts, and an .onion or any
  non-allowlisted address is refused and logged as a gap like any
  other. The reasons, for the record: (1) the Diver's quarry is
  published paper — declassified means released, and released paper
  lives in harbours with a chain of custody; (2) story-versus-paper
  (Law 1, Law 7) needs provenance, and an anonymous file has none —
  it would fail the audit on arrival; (3) those waters carry the
  highest density of poisoned downloads anywhere, against Law 6's
  whole intent; (4) an indiscriminate crawl there trawls criminal
  material onto the host machine. Technical ability to try is not a
  gap in this list. It is the reason the list exists.
- **Executable or active content of any kind** — the Diver reads
  PDFs as data (Law 6). Nothing fetched is run, opened in a helper
  app, or trusted with a macro, a script, or a link inside it.
- **People-collections** — leaked personal data, dox and breach
  dumps, wherever hosted. Not paper about events; not the quarry;
  refused even if a harbour-shaped site offers them.

## What a finished dive looks like

A pond folder per shelf; one text file per kept document; an
`index.csv` whose lines all trace; a `gaps.log` that tells the truth
about what is not there; and a receipt a tired human can read at
2 a.m. that says what was kept, what was already there, what is
missing, and how long it took.
