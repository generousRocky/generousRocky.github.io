---
layout: home
permalink: /
title: "Latest Posts"
excerpt: 
image:
  feature: wood-texture-1600x800.jpg
---

<div class="tiles">
{% for post in site.posts limit: 4 %}
	{% include post-grid.html %}
{% endfor %}
</div><!-- /.tiles -->

