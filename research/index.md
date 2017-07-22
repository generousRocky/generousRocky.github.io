---
title: Reserch Blog
date: 2014-05-30 15:39:03
layout: archive
modified: 2016-05-30 15:39:03
excerpt: "It's a bit embarrassing, but literally research"
tags: []
image:
  feature:
  teaser: 
---

<div class="tiles">
{% for post in site.categories.research %}
  {% include post-grid.html %}
{% endfor %}
</div><!-- /.tiles -->