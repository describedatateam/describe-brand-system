import json, re, os
H=os.path.dirname(os.path.abspath(__file__))
A=json.load(open(os.path.join(H,'..','web_assets.json')))
R='/home/claude/'
css=open(R+'type/typography.css').read()+'\n'+re.sub(r"@import url\('\.\./type/typography\.css'\);\s*","",open(R+'ui/ui.css').read())
SPEC={'cygnus':[('dotted','dot','var(--body)'),('lines','full','var(--ink)'),('outside','','var(--ink)'),('stars','','var(--active)')],
      'cyg_outside':[('lines','','var(--ink)'),('stars','','var(--active)'),('outside','','var(--mark)')],
      'astrolabe':[('lines','','var(--body)')],
      'libra':[('lines','','var(--ink)'),('outside','','var(--ink)'),('stars','','var(--active)')],
      'cancer_globe':[('lines','','var(--ink)'),('outside','','var(--ink)'),('stars','','var(--active)')],
      'cancer_sky':[('lines','','var(--ink)'),('outside','','var(--ink)'),('stars','','var(--active)')]}
LABEL={'cygnus':'Cygnus drawn as a swan, its stars marked','cyg_outside':'Detail of Cygnus with two stars outside the figure','astrolabe':'Astrolabe plate diagram','libra':'Libra drawn as a pair of scales, its stars marked','cancer_globe':'Cancer as seen on the globe','cancer_sky':'Cancer as seen in the sky'}
def ill(name):
    a=A[name]; spans=''.join(f'<span class="{cls}" style="--c:{c};--m:url({a["layers"][k]})"></span>'
                             for k,cls,c in SPEC[name] if k in a['layers'])
    return f'<div class="art" style="--ar:{a["w"]}/{a["h"]}" role="img" aria-label="{LABEL[name]}">{spans}</div>'
t=open(os.path.join(H,'template.html')).read().replace('/*CSS*/',css)
t=re.sub(r'<!--ILL:(\w+)-->',lambda m:ill(m.group(1)),t)
t=re.sub(r'<!--BG:(\w+)-->',lambda m:'',t)
t=t.replace('<div class="herosky" aria-hidden="true">','<div class="herosky" aria-hidden="true" style="--m:url('+A['herosky']['layers']['field']+')">')
open(os.path.join(H,'fixed-stars.html'),'w').write(t); print(len(t)//1024,'KB')
