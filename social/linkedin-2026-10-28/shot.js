const {chromium}=require('/opt/node-tools/node_modules/playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
for(const n of ['c3','p3','c4']){await p.goto('file://'+process.cwd()+'/'+n+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:n+'.png',clip:{x:0,y:0,width:1080,height:1350}});}
await b.close();})();
