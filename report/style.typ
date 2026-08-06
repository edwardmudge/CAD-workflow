#let report-style(title: "", author: "", date: none, body) = {
  set page(margin: 2.5cm, numbering: "1")
  set text(size: 11pt, lang: "en", region: "gb")
  set heading(numbering: "1.1")
  set par(justify: true)
  align(center)[
    #text(size: 20pt, weight: "bold")[#title] \
    #v(0.3cm)
    #author \ #date.display("[day] [month repr:long] [year]")
  ]
  v(1cm)
  body
}
