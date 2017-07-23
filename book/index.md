---
title: Book
date: 2014-06-02 13:44:20 Z
layout: archive
modified: 2017-07-24 18:56:44 Z
excerpt: Things I've read, studied
image:
  feature:
  teaser:
  thumb:
share: false
ads: false
---

<div class="tiles">
{% for post in site.categories.book %}
  {% include post-grid.html %}
{% endfor %}
</div><!-- /.tiles -->
