#import "@preview/merman:0.3.0": show-mermaid-blocks
#import "@preview/cheq:0.4.0": checklist

#show raw.where(lang: "mermaid"): show-mermaid-blocks(width: 100%)
#show: checklist

#set page(margin: 22mm, numbering: "1")
#set text(size: 10.5pt)
#set par(justify: true)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  it
}

#let book-title = {{title}}
#set document(title: book-title)

#align(center)[
  #v(35%)
  #text(size: 25pt, weight: "bold")[#book-title]
]

#pagebreak()
#outline(title: [Contents], depth: 3)
#pagebreak()

{{content}}
