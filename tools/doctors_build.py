"""Builds the readable MERA ENT Pathways page (one file, scripts inlined) for the doctors' login.
Usage: python3 tools/doctors_build.py <folder with index.html, nt.js, who.js, growth.js> <out.html>
The output is readable: keep it OUTSIDE the repo; doctors_publish.sh encrypts it."""
import re, sys, pathlib
src = pathlib.Path(sys.argv[1]); html = (src / "index.html").read_text()
def inline(m):
    js = (src / m.group(1)).read_text().replace("</script", "<\\/script")
    return "<script>\n" + js + "\n</script>"
html = re.sub(r'<script src="([a-z]+\.js)"></script>', inline, html)
assert 'src="' not in html.split("<body")[1], "unexpected external script"
html = html.replace('<meta name="viewport"', '<meta name="robots" content="noindex, nofollow">\n<meta name="viewport"', 1)
html = html.replace("<p>MERA © Dr Rejith R S</p>",
  '<p>MERA © Dr Rejith R S · <a href="https://www.entmidas.com/" style="color:inherit">MIDAS ENT, Thrissur</a></p>', 1)
pathlib.Path(sys.argv[2]).write_text(html)
print("built", sys.argv[2], len(html), "bytes")
