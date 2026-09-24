#import "@preview/merman:0.3.0": show-mermaid-blocks
#import "@preview/cheq:0.4.0": checklist

#show raw.where(lang: "mermaid"): show-mermaid-blocks(width: 100%)
#show: checklist

#let ink = rgb("#17243A")
#let accent = rgb("#247A83")
#let muted = rgb("#697586")
#let rule = rgb("#D6DEE5")
#let cover-paper = rgb("#F3F6F7")
#let book-title = {{title}}

#set document(title: book-title)
#set text(font: "Libertinus Serif", size: 10.5pt, fill: ink)
#set par(justify: true, leading: 0.72em, spacing: 0.8em)
#set heading(numbering: "1.1")

// A quiet, spacious cover that works for books with short or long titles.
#page(
  paper: "a4",
  margin: (left: 28mm, right: 28mm, top: 25mm, bottom: 24mm),
  fill: cover-paper,
  numbering: none,
)[
  #set text(font: "Libertinus Sans", fill: ink)
  #text(size: 8pt, weight: "bold", tracking: 1.5pt, fill: accent)[PRACTICAL GUIDE]
  #v(38mm)
  #text(size: 35pt, weight: "bold")[#book-title]
  #v(9mm)
  #line(length: 24mm, stroke: 2.5pt + accent)
  #v(7mm)
  #text(font: "Libertinus Serif", size: 13pt, fill: muted)[A reference for thoughtful practice]
  #v(1fr)
  #line(length: 100%, stroke: 0.6pt + rule)
  #v(4mm)
  #text(size: 8.5pt, fill: muted)[Compiled from the book source]
]

#pagebreak()

#set page(
  paper: "a4",
  margin: (left: 25mm, right: 25mm, top: 25mm, bottom: 23mm),
  numbering: "1",
  header: context {
    grid(
      columns: (1fr, auto),
      align: (left, right),
      text(size: 8pt, fill: muted)[#book-title],
      text(size: 8pt, weight: "bold", fill: accent)[FIELD GUIDE],
    )
    v(4pt)
    line(length: 100%, stroke: 0.5pt + rule)
  },
  footer: context {
    line(length: 100%, stroke: 0.5pt + rule)
    v(4pt)
    grid(
      columns: (1fr, auto),
      align: (left, right),
      text(size: 8pt, fill: muted)[#book-title],
      text(size: 8pt, fill: muted)[#counter(page).display("1")],
    )
  },
)

#set par(first-line-indent: 0pt)
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  block(above: 0pt, below: 1.2em)[
    #set text(font: "Libertinus Sans", size: 23pt, weight: "bold", fill: ink)
    #it
    #v(0.45em)
    #line(length: 100%, stroke: 1.4pt + accent)
  ]
}
#show heading.where(level: 2): it => {
  set text(font: "Libertinus Sans", size: 15pt, weight: "bold", fill: accent)
  it
}
#show heading.where(level: 3): it => {
  set text(font: "Libertinus Sans", size: 11.5pt, weight: "bold", fill: ink)
  it
}

#align(center)[
  #text(font: "Libertinus Sans", size: 23pt, weight: "bold", fill: ink)[Contents]
  #v(2mm)
  #line(length: 20mm, stroke: 1.5pt + accent)
]
#v(7mm)
#outline(title: none, depth: 3)
#pagebreak()

{{content}}
