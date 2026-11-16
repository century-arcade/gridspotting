# #Gridspotting

Crosswords spotted on screen, traced back to the puzzles they came from. The spottings are
Ben Zimmer's, from his talk ["Adventures in Gridspotting"](https://www.youtube.com/watch?v=KkjbiKiHQyE) (Crossword Con, New York,
Apr. 10, 2026). This site is a placeholder built from the talk slides until Ben's own blog
exists.

Published at https://centuryarcade.org/gridspotting/

- `data/sightings.tsv`: one row per sighting (what was on screen, and the puzzle it matches,
  with its id at The Cross(word) Reference, `crossref`, when it has one there,
  if any). `post` groups rows into pages.
- `sightings.json`: the same data with a stable URL for each sighting, for indexers such as
  The Cross Reference.
- `tools/import_pptx.py <slides.pptx>`: copies the images the TSV names out of the slides.
- `tools/build.py`: regenerates `index.html`, `posts/` and `sightings.json` from the TSV.
