---
layout: home
permalink: /
title: "Rocky's Dev and Research blog"
excerpt:
image:
  feature: wood-texture-1600x800.jpg
---



<div style="text-align:left">
  <span style = " font-size:2em;  color: gray;">
    &nbsp;<br />
    &nbsp;<br />
    &nbsp;<br />
    Development
  </span>
</div>
<div class="tiles">
    {% for post in site.categories.book limit: 8 %}
        {% include post-grid.html %}
    {% endfor %}
</div>

<div style="text-align:left">
  <span style = " font-size:2em;  color: gray;">
    Research
  </span>
</div>
<div class="tiles">
    {% for post in site.categories.research limit: 8 %}
        {% include post-grid.html %}
    {% endfor %}
</div>
