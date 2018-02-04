# encoding=utf-8

from pathlib import Path
import re

pat = r"image:\s*\n(\s+)teaser:\s*(.*)"
sub = r"\g<0>\n\1path: /images/\2"

p = Path("_posts/book/how_computers_work")
for file in p.iterdir():
    with file.open() as f:
        txt = f.read()

    print(re.search(pat, txt).group(1))
    newtxt = re.sub(pat, sub, txt)
    
    with file.open('w') as f:
        f.write(newtxt)

_posts/book/how_computers_work