---
layout: home
permalink: /
title: "Latest Posts ( Latest 4 posts per each section )"
excerpt:
image:
  feature: wood-texture-1600x800.jpg
---


<div style="text-align:left">
  <span style = " font-size:2em;  color: gray;">
    Research
  </span>
</div>
<div class="tiles">
    {% for post in site.categories.research limit: 4 %}
        {% include post-grid.html %}
    {% endfor %}
</div>


<div style="text-align:left">
  <span style = " font-size:2em;  color: gray;">
    &nbsp;<br />
    &nbsp;<br />
    &nbsp;<br />
    Books & Studies
  </span>
</div>
<div class="tiles">
    {% for post in site.categories.book limit: 4 %}
        {% include post-grid.html %}
    {% endfor %}
</div>



<div style="text-align:left">
  <span style = " font-size:2em;  color: gray;">
    &nbsp;<br />
    &nbsp;<br />
    &nbsp;<br />
    Whatever
  </span>
</div>
<div class="tiles">
    {% for post in site.categories.whatever limit: 4 %}
        {% include post-grid.html %}
    {% endfor %}
</div>
