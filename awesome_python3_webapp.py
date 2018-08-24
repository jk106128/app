#!/usr/bin/env python
# Copyright (c) 2012 Trent Mick.
# Copyright (c) 2007-2008 ActiveState Corp.
# License: MIT (http://www.opensource.org/licenses/mit-license.php)

from __future__ import generators

r"""A fast and complete Python implementation of Markdown.

[from http://daringfireball.net/projects/markdown/]
> Markdown is text-to-HTML filter; it translates an easy-to-read/
> easy-to-write structured text format into HTML. Markdown's text
> format is most similar to that of plain text email, and supports
> features such as headers, *emphasis*, code blocks, blockquotes, and
> links.
>
> Markdown's syntax is designed not as a generic markup language, but
> specifically to serve as a front-end to (x)HTML. You can us span-level 
> HTML tags anywhere in a Markdown document, and you can use block level
> HTML tags (like <div> and <table> as well).

Module usage:

