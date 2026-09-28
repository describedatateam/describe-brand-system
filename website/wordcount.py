"""wordcount.py — visible words per section of site.html (charts, tables, form fields, scripts excluded)."""
import re
import sys

p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/website/site.html'
t = open(p, encoding='utf-8').read()
STRIP = r'<style>.*?</style>|<script.*?</script>|<svg.*?</svg>|<table.*?</table>|<caption.*?</caption>|<select.*?</select>'


def words(s):
    s = re.sub(STRIP, ' ', s, flags=re.S)
    s = re.sub(r'<[^>]*class="[^"]*\bvh\b[^"]*"[^>]*>.*?</[a-z]+>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return len(s.split())


body = re.sub(r'^.*?</style>', '', t, count=1, flags=re.S)
print(f'TOTAL visible words: {words(body)}')
for sid, inner in re.findall(r'<section[^>]*\bid="([^"]+)"[^>]*>(.*?)</section>', t, flags=re.S):
    print(f'  {sid:<12}{words(inner)}')
foot = re.search(r'<footer.*?</footer>', t, flags=re.S)
if foot:
    print(f'  {"footer":<12}{words(foot.group(0))}')
