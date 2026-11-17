// Render the exact exported PPTX. Unchanged native pages can reuse verified PNGs.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL,fileURLToPath} from 'node:url';
import fontEnvironment from './font_environment.cjs';
const arg=n=>process.argv[process.argv.indexOf(n)+1];
for(const n of ['--out','--artifact-module'])if(!process.argv.includes(n))throw new Error('Missing '+n);
const root=path.resolve(arg('--out')),modulePath=path.resolve(arg('--artifact-module'));
const hash=v=>crypto.createHash('sha256').update(v).digest('hex');
const read=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const ex=await read(path.join(root,'export-manifest.json'));
if(hash(await fs.readFile(ex.pptx))!==ex.pptx_sha256)throw new Error('PPTX changed after export checks');
const rendererInputs={module:hash(await fs.readFile(modulePath)),node:process.version,platform:process.platform,fonts:fontEnvironment(),fontChecker:hash(await fs.readFile(new URL('./font_environment.cjs',import.meta.url))),script:hash(await fs.readFile(fileURLToPath(import.meta.url)))};
const renderer=hash(JSON.stringify(rendererInputs));
let previous={};try{previous=await read(path.join(root,'ppt-render-report.json'))}catch{}
const {FileBlob,PresentationFile}=await import(pathToFileURL(modulePath).href);
const deck=await PresentationFile.importPptx(await FileBlob.load(ex.pptx));
await fs.mkdir(path.join(root,'ppt-render'),{recursive:true});
const report={pptx_sha256:ex.pptx_sha256,renderer,renderer_inputs:rendererInputs,pages:[],status:'failed'};
for(let i=0;i<ex.pages.length;i++){
 const row=ex.pages[i],file=path.join(root,'ppt-render',String(i+1).padStart(2,'0')+'.png'),old=previous.pages?.[i];
 let reuse=false;try{reuse=previous.renderer===renderer&&old?.visual_fingerprint===row.visual_fingerprint&&hash(await fs.readFile(file))===old.screenshot_sha256}catch{}
 if(!reuse){const png=await deck.export({slide:deck.slides.getItem(i),format:'png',scale:1});await fs.writeFile(file,new Uint8Array(await png.arrayBuffer()))}
 report.pages.push({page:i+1,visual_fingerprint:row.visual_fingerprint,screenshot_sha256:hash(await fs.readFile(file)),reused:reuse});
 console.log((reuse?'Reused ':'Rendered ')+(i+1)+'/'+ex.pages.length);
}
report.status='passed';await fs.writeFile(path.join(root,'ppt-render-report.json'),JSON.stringify(report,null,2));
