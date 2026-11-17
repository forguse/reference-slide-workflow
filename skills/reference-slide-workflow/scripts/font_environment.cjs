// Font installation changes invalidate screenshots in both renderers.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto');
module.exports=function fontEnvironment(){
 // Desktop shells can redirect LOCALAPPDATA to a different ephemeral directory each run.
 // Fingerprint the real user's font directory; extra/custom locations can be explicit.
 const dirs=process.platform==='win32'?[path.join(process.env.WINDIR||'C:\\Windows','Fonts'),path.join(os.homedir(),'AppData','Local','Microsoft','Windows','Fonts')]:
  process.platform==='darwin'?['/System/Library/Fonts','/Library/Fonts',path.join(os.homedir(),'Library/Fonts')]:['/usr/share/fonts','/usr/local/share/fonts',path.join(os.homedir(),'.fonts'),path.join(os.homedir(),'.local/share/fonts')];
 if(process.env.PPT_FONT_DIRS)dirs.push(...process.env.PPT_FONT_DIRS.split(path.delimiter).filter(Boolean));
 const records=[];
 function visit(dir){
  let entries;try{entries=fs.readdirSync(dir,{withFileTypes:true})}catch(e){records.push([dir,e.code]);return}
  for(const e of entries.sort((a,b)=>a.name.localeCompare(b.name))){
   const p=path.join(dir,e.name);
   if(e.isDirectory())visit(p);
   else if(e.isFile()&&/\.(ttf|otf|ttc|woff2?|fon)$/i.test(e.name)){const st=fs.statSync(p);records.push([p,st.size,st.mtimeMs]);}
  }
 }
 for(const d of [...new Set(dirs)].sort())visit(d);
 return crypto.createHash('sha256').update(JSON.stringify({version:1,records})).digest('hex');
};
