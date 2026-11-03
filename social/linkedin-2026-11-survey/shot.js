const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
for(const n of ['s1','s2']){await p.goto('file://'+__dirname+'/'+n+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:__dirname+'/'+n+'.png',clip:{x:0,y:0,width:1080,height:1350}});}
await b.close();})();
