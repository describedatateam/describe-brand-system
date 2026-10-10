const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
for(const n of ['post1','post2','post3','post4','post5']){await p.goto('file://'+process.cwd()+'/'+n+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 const fams=await p.evaluate(()=>[...document.fonts].map(f=>f.family+':'+f.status).join(' '));console.log(n,fams);
 await p.screenshot({path:n+'.png',clip:{x:0,y:0,width:1080,height:1350}});
 if(n==='post5'){await p.pdf({path:'post5-carousel.pdf',width:'1080px',height:'1350px',printBackground:true});
  const c=await p.locator('.page').count();for(let i=0;i<c;i++)await p.locator('.page').nth(i).screenshot({path:`slide${i+1}.png`});}}
await b.close();})();
