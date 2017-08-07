---
layout: home
permalink: /
title: "Latest Posts"
excerpt:
image:
  feature: wood-texture-1600x800.jpg
---


<div style="text-align:left">
  <span style = " font-size:2em;  color: gray;">
    &nbsp;<br />
    Posts for Research<br />
    </span>
    &nbsp;<br />
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
    Posts for Books & Studies<br />
    </span>
    &nbsp;<br />
</div>
<div class="tiles">
    {% for post in site.categories.book limit: 4 %}
        {% include post-grid.html %}
    {% endfor %}
</div>



<div style="text-align:left">
  <span style = " font-size:2em;  color: gray;">
    &nbsp;<br />
    Posts for Whatever<br />
    </span>
    &nbsp;<br />
</div>
<div class="tiles">
    {% for post in site.categories.whatever limit: 4 %}
        {% include post-grid.html %}
    {% endfor %}
</div>
