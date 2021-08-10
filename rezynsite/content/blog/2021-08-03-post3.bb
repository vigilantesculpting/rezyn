---
author: g0rb
date: '2021-08-03T14:47:42 -0700'
tags:
- hello
- world
title: '-=[rezyn]=-'
---
Rezyn is a static website generator in Python

It uses a database of plain text files to store content, and renders the content
to HTML using solon (a structured templating language) and pretzyl (a functional expression
evaluation language).

Rezyn provides the tools to build an Environment structure from the source files, 
and solon + pretzyl gets their data from the Environment to populate template files
with rendered text, which can be written out to file.
