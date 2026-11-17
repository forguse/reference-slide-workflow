// Behavioral fault injection; uses a retained browser profile, never removes trees.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const audit=require('./layout_audit.cjs');
const arg=n=>process.argv[process.argv.indexOf(n)+1];
(async()=>{
 const {chromium}=require(arg('--playwright-module'));
 const root=path.resolve(arg('--out'));fs.mkdirSync(root,{recursive:true});
 const browser=await chromium.launchPersistentContext(path.join(root,'test-browser-profile'),{channel:'msedge',headless:true,timeout:30000});
 const cases=[];
 try{
  const page=await browser.newPage();
  const base='<rect width="400" height="300" fill="white"/><text id="a" x="20" y="50" font-size="20">标题甲</text><g id="group"><text id="b" x="220" y="50" font-size="20">标题乙</text></g>';
  const contract={rules:[{kind:'align',items:['a','b'],edge:'baseline',tolerance:1},{kind:'inside',items:['a'],box:[10,10,180,80]}],allow_overlap:[]};
  async function run(name,svg,rule,expected){
   await page.setContent('<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" font-family="Microsoft YaHei">'+svg+'</svg>');await page.evaluate(()=>document.fonts.ready);
   const result=await page.locator('svg').evaluate((svg,{source,rule})=>(0,eval)('('+source+')')(svg,rule),{source:audit.toString(),rule});
   if(expected)assert(result.errors.some(e=>e.code===expected),name+': '+JSON.stringify(result.errors));else assert.equal(result.errors.length,0,name+': '+JSON.stringify(result.errors));
   cases.push({name,status:'passed',expected:expected||'no errors'});
  }
  await run('aligned controls',base,contract);
  await run('nested transform misalignment',base.replace('id="group"','id="group" transform="translate(0,12)"'),contract,'alignment');
  await run('inside canvas but outside container',base.replace('标题甲','这是一段在整页内但挤出小栏宽度的很长说明文字'),contract,'container_overflow');
  await run('text collision',base.replace('x="220"','x="25"'),contract,'text_overlap');
  await run('line crossing text',base.replace('<text id="a"','<line id="line" x1="10" y1="43" x2="190" y2="43" stroke="blue"/><text id="a"'),contract,'line_crosses_text');
  await run('intentional masked feedback line','<line id="line" x1="10" y1="43" x2="190" y2="43" stroke="blue"/><rect x="18" y="20" width="70" height="50" fill="white"/>'+base.replace('<rect width="400" height="300" fill="white"/>',''),contract);
  await run('picture colliding with text',base+'<image id="pic" x="20" y="30" width="180" height="70"/>',contract,'image_text_overlap');
  await run('caption gap too small',base+'<rect id="fig" x="20" y="100" width="160" height="100"/><text id="cap" x="20" y="215" font-size="16">图注</text>',{rules:[...contract.rules,{kind:'gap',items:['fig','cap'],min:12,axis:'y'}]},'gap');
  await run('unequal module spacing','<rect id="r1" x="10" y="20" width="10" height="30"/><rect id="r2" x="40" y="20" width="10" height="30"/><rect id="r3" x="80" y="20" width="10" height="30"/>',{rules:[{kind:'equal-gap',items:['r1','r2','r3'],axis:'x',tolerance:2}]},'unequal_gaps');
  await run('missing declared element',base,{rules:[{kind:'align',items:['a','missing'],edge:'top'}]},'invalid_contract');
 }finally{await browser.close()}
 fs.writeFileSync(path.join(root,'layout-fault-tests.json'),JSON.stringify({status:'passed',cases},null,2));console.log(JSON.stringify({status:'passed',cases:cases.length}));
})().catch(e=>{console.error(e);process.exitCode=1});
