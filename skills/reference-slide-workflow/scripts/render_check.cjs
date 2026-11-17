#!/usr/bin/env node
// The browser profile is retained. No recursive cleanup is performed.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {pathToFileURL}=require('node:url');
const audit=require('./layout_audit.cjs');
const fontEnvironment=require('./font_environment.cjs');
const hash=value=>crypto.createHash('sha256').update(value).digest('hex');
function arg(name,def){const i=process.argv.indexOf(name);return i<0?def:process.argv[i+1];}
(async()=>{
 const folder=arg('--out');if(!folder)throw new Error('Required: --out OUTPUT_DIRECTORY');
 const root=path.resolve(folder),manifest=JSON.parse(fs.readFileSync(path.join(root,'build.json'),'utf8'));
 if(manifest.schema!==3)throw new Error('Use a v3 project with canonical source and layout contracts.');
 const contracts=JSON.parse(fs.readFileSync(path.join(root,'project','layout-contracts.json'),'utf8'));
 const profile=JSON.parse(fs.readFileSync(path.join(root,'project','style-profile.json'),'utf8'));
 const expectedCanvas=[0,0,...profile.canvas].join(' ');
 const previous=fs.existsSync(path.join(root,'preview-report.json'))?JSON.parse(fs.readFileSync(path.join(root,'preview-report.json'),'utf8')):{};
 for(const item of manifest.files){const h=crypto.createHash('sha256').update(fs.readFileSync(path.join(root,item.path))).digest('hex');if(h!==item.sha256)throw new Error('Rebuild HTML after changing '+item.path);}
 const modulePath=arg('--playwright-module',process.env.PLAYWRIGHT_MODULE||'playwright');
 const {chromium}=require(modulePath);
 const channel=arg('--channel',process.platform==='win32'?'msedge':undefined);
 const options={headless:true,viewport:{width:Math.ceil(profile.canvas[0]+110),height:Math.ceil(profile.canvas[1]+230)},deviceScaleFactor:1,timeout:30000};
 if(channel&&channel!=='chromium')options.channel=channel;
 fs.mkdirSync(path.join(root,'screenshots'),{recursive:true});
 console.log('Opening local HTML in '+(channel||'Chromium')+' (30 second launch timeout)...');
 const browser=await chromium.launchPersistentContext(path.join(root,'browser-profile'),options);
 const report={build_digest:manifest.build_digest,pages:[],javascript_errors:[],fonts:[],status:'failed'};
 report.environment=hash(JSON.stringify({browser:browser.browser()?.version(),node:process.version,platform:process.platform,fonts:fontEnvironment(),checker:hash(fs.readFileSync(__filename)),audit:hash(fs.readFileSync(require.resolve('./layout_audit.cjs'))),fontChecker:hash(fs.readFileSync(require.resolve('./font_environment.cjs')))}));
 try{
  const page=await browser.newPage();page.on('pageerror',e=>report.javascript_errors.push(String(e)));
  await page.goto(pathToFileURL(path.join(root,'preview.html')).href,{waitUntil:'load'});
  await page.evaluate(()=>document.fonts.ready);
  await page.evaluate(()=>show(1));
  if(manifest.pages.length>1){
   await page.locator('[data-action=next]').click();
   if(await page.locator('#pageSelect').inputValue()!=='2')throw new Error('Next-page control failed');
   await page.locator('[data-action=previous]').click();
   if(await page.locator('#pageSelect').inputValue()!=='1')throw new Error('Previous-page control failed');
  }
  await page.locator('#pageSelect').selectOption(String(manifest.pages.length));
  if(!await page.locator('#page-'+manifest.pages.length).isVisible())throw new Error('Page selector failed');
  await page.locator('[data-action=all]').click();
  if(await page.locator('.page:visible').count()!==manifest.pages.length)throw new Error('All-pages control failed');
  report.navigation='passed';
  const cdp=await page.context().newCDPSession(page);await cdp.send('DOM.enable');await cdp.send('CSS.enable');
  for(let i=1;i<=manifest.pages.length;i++){
   await page.evaluate(n=>show(n),i);
   await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   const locator=page.locator('#page-'+i);
   const result=await locator.locator('svg').evaluate(svg=>{
    return {canvas:svg.getAttribute('viewBox'),overflow:[]};
   });
   const geometry=await locator.locator('svg').evaluate((svg,{source,contract})=>{const fn=(0,eval)('('+source+')');return fn(svg,contract)},{source:audit.toString(),contract:contracts.pages[String(i)]});
   const entry={page:i,...result,layout:geometry,visual_digest:manifest.pages[i-1].visual_digest};
   report.pages.push(entry);
   const doc=await cdp.send('DOM.getDocument',{depth:1});
   const {nodeIds}=await cdp.send('DOM.querySelectorAll',{nodeId:doc.root.nodeId,selector:'#page-'+i+' text'});
   const sampled=new Set();
   for(const n of nodeIds){
    const outer=(await cdp.send('DOM.getOuterHTML',{nodeId:n})).outerHTML;
    const family=(outer.match(/font-family="([^"]+)"/)||[])[1]||profile.typography.body.family;
    const weight=(outer.match(/font-weight="([^"]+)"/)||[])[1]||'400';
    const expected=family.split(',')[0].replace(/["']/g,'').trim();
    const key=expected+'|'+weight;
    if(expected&&!sampled.has(key)){const fonts=(await cdp.send('CSS.getPlatformFontsForNode',{nodeId:n})).fonts;report.fonts.push({page:i,expected,weight,fonts});sampled.add(key);}
   }
   const png=path.join(root,'screenshots',String(i).padStart(2,'0')+'.png');
   entry.measurement_digest=hash(JSON.stringify({bounds:geometry.bounds,fonts:report.fonts.filter(f=>f.page===i)}));
   const prior=previous.pages?.find(p=>p.page===i);
   entry.screenshot_reused=previous.environment===report.environment&&prior?.visual_digest===entry.visual_digest&&prior?.measurement_digest===entry.measurement_digest&&fs.existsSync(png)&&prior?.screenshot_sha256===hash(fs.readFileSync(png));
   if(!entry.screenshot_reused)await locator.screenshot({path:png});
   entry.screenshot_sha256=hash(fs.readFileSync(png));
  }
  const ids=await page.locator('svg [id]').evaluateAll(els=>els.map(e=>e.id));report.duplicate_ids=ids.filter((v,i)=>ids.indexOf(v)!==i);
  const normal=s=>s.toLowerCase().replace(/[^a-z0-9]/g,'');
  report.font_substitution=report.fonts.some(r=>!r.fonts.some(f=>normal(f.familyName+' '+f.postScriptName).includes(normal(r.expected))));
  const allow=process.argv.includes('--allow-font-substitution');
  report.status=report.javascript_errors.length===0&&report.duplicate_ids.length===0&&report.pages.every(p=>p.canvas===expectedCanvas&&p.overflow.length===0&&p.layout.errors.length===0)&&(!report.font_substitution||allow)?'passed':'failed';
  report.exact_font_environment=!report.font_substitution;
 }finally{await browser.close();fs.writeFileSync(path.join(root,'preview-report.json'),JSON.stringify(report,null,2));}
 console.log(JSON.stringify({status:report.status,pages:report.pages.length,reused_screenshots:report.pages.filter(p=>p.screenshot_reused).length,font_substitution:report.font_substitution,layout_errors:report.pages.filter(p=>p.layout.errors.length).map(p=>({page:p.page,errors:p.layout.errors})),javascript_errors:report.javascript_errors}));
 if(report.status!=='passed')process.exitCode=1;
})().catch(e=>{console.error(String(e));process.exitCode=1;});
