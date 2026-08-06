#import "style.typ": report-style
#show: report-style.with(
  title: "PROJECT TITLE",
  author: "YOUR NAME",
  date: datetime.today(),
)

// All prose in this file is yours. Rename, delete, or reorder headings
// freely. Harvest content from report_nodes.md; write every sentence
// yourself. Escape hatch: past roughly 1500 lines, split each top-level
// heading into report/sections/<name>.typ and #include them here.

= Introduction
// TODO: problem, motivation, objectives

= Background
// TODO: prior work, theory needed to follow the rest

= Method
// TODO: design decisions live here; see report_nodes.md section tags

= Results
// TODO: figures from figures/, measurements, tests

= Discussion
// TODO: what worked, what did not, refer to postmortems by P number

= Conclusions
// TODO: objectives met or not, and what you would do differently

// #bibliography("refs.bib")  // uncomment and create refs.bib when citing
