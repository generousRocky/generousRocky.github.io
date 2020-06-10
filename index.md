---
layout: home
permalink: /
title: "Rocky's Dev and Research blog"
excerpt:
image:
  feature: wood-texture-1600x800.jpg
ads: true
---

<div style="text-align:left">
  <span style = " font-size:2em;  color: gray;">
    Research
  </span>
</div>
<div class="tiles">
    {% for post in site.posts limit: 12 %}
        {% include post-grid.html %}
    {% endfor %}
</div>
