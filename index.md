---
layout: home
permalink: /
title: "Latest posts"
excerpt:
image:
  feature: wallpaper.jpg
ads: false
---

<div style="text-align:left">
  <span style = " font-size:2em;  color: black;">
    &nbsp;<br />
    Development<br />
  </span>
    &nbsp;<br />
</div>
<div class="tiles">
    {% for post in site.categories.development limit: 4 %}
        {% include post-grid.html %}
    {% endfor %}
</div>

<div style="text-align:left">
  <span style = " font-size:2em;  color: black;">
    Research<br />
  </span>
    &nbsp;<br />
</div>
<div class="tiles">
    {% for post in site.categories.research limit: 4 %}
        {% include post-grid.html %}
    {% endfor %}
</div>

<div style="text-align:left">
  <span style = " font-size:2em;  color: black;">
    &nbsp;<br />
    &nbsp;<br />
    &nbsp;<br />
    etc.<br />
  </span>
    &nbsp;<br />
</div>
<div class="tiles">
    {% for post in site.categories.writing limit: 4 %}
        {% include post-grid.html %}
    {% endfor %}
</div>
