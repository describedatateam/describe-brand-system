# Make a source photo on Replicate for the atmosphere treatments.
# The proxy injects the Replicate token, so any placeholder bearer works here.
# usage: python3 source.py out.png "subject description"
import json, sys, urllib.request

STYLE = ("High-detail documentary photograph. One clear subject, {subject}. Soft directional light "
         "from the upper left, plain dark background, clear tonal contrast, no faces in shadow, "
         "sharp edges, no text, no logos, no watermark.")

def make(out, subject, model='black-forest-labs/flux-1.1-pro', aspect='1:1'):
    body = json.dumps({'input': {'prompt': STYLE.format(subject=subject), 'aspect_ratio': aspect,
                                 'output_format': 'png', 'safety_tolerance': 2}}).encode()
    req = urllib.request.Request(f'https://api.replicate.com/v1/models/{model}/predictions', body,
                                 {'Authorization': 'Bearer placeholder', 'Content-Type': 'application/json',
                                  'Prefer': 'wait=60'})
    pred = json.load(urllib.request.urlopen(req, timeout=90))
    if pred.get('status') != 'succeeded': raise SystemExit(f"{pred.get('status')}: {pred.get('error')}")
    url = pred['output'] if isinstance(pred['output'], str) else pred['output'][0]
    urllib.request.urlretrieve(url, out)
    return out

if __name__ == '__main__':
    make(sys.argv[1], sys.argv[2], aspect=sys.argv[3] if len(sys.argv) > 3 else '1:1')
