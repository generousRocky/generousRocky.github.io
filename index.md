---
layout: home
permalink: /
title: "Latest posts in all categories"
excerpt:
image:
  feature: library.jpg
ads: false
---

<div style="text-align:left">
  <span style = " font-size:2em;  color: gray;">
  </span>
</div>
<div class="tiles">
    {% for post in site.posts limit: 8 %}
        {% include post-grid.html %}
    {% endfor %}
</div>
