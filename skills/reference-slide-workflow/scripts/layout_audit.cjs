// Pure browser-side audit. Every coordinate is converted to the SVG root space.
module.exports=function audit(svg,contract){
 const errors=[],bounds={},tol=2; const canvas=svg.viewBox.baseVal;
 const issue=(code,items,detail)=>errors.push({code,items,detail});
 const rootInverse=svg.getScreenCTM().inverse();
 const matrix=el=>rootInverse.multiply(el.getScreenCTM());
 const xy=(el,x,y)=>new DOMPoint(x,y).matrixTransform(matrix(el));
 function box(el){
  const b=el.getBBox(),p=[xy(el,b.x,b.y),xy(el,b.x+b.width,b.y),xy(el,b.x,b.y+b.height),xy(el,b.x+b.width,b.y+b.height)];
  const x=Math.min(...p.map(p=>p.x)),y=Math.min(...p.map(p=>p.y));
  const r={x,y,w:Math.max(...p.map(p=>p.x))-x,h:Math.max(...p.map(p=>p.y))-y};
  if(el.tagName==='text'){
   const a=xy(el,el.x.baseVal.getItem(0)?.value||0,el.y.baseVal.getItem(0)?.value||0);r.anchorX=a.x;r.baseline=a.y;
  }
  return r;
 }
 const nodes=[...svg.querySelectorAll('[id]')];
 for(const el of nodes){try{bounds[el.id]=box(el)}catch{}}
 const byid=id=>nodes.find(e=>e.id===id);
 const b=id=>{if(!bounds[id])throw new Error('Unknown element '+id);return bounds[id]};
 const edge=(id,name)=>{const r=b(id);return ({left:r.x,right:r.x+r.w,top:r.y,bottom:r.y+r.h,centerX:r.x+r.w/2,centerY:r.y+r.h/2,width:r.w,height:r.h,anchorX:r.anchorX,baseline:r.baseline})[name]};
 const allowed=(a,b)=> (contract?.allow_overlap||[]).some(r=>r.reason&&r.items.includes(a)&&r.items.includes(b));
 const intersect=(a,b)=>Math.max(0,Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x))*Math.max(0,Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y));
 if(!contract||!Array.isArray(contract.rules)||!contract.rules.length)issue('contract_missing',[],'Add relationships and review focus for this page.');
 const texts=nodes.filter(e=>e.tagName==='text'&&e.textContent.trim()&&bounds[e.id]);
 for(const t of texts){const r=b(t.id);if(r.x<-.5||r.y<-.5||r.x+r.w>canvas.width+.5||r.y+r.h>canvas.height+.5)issue('canvas_overflow',[t.id],r)}
 for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){
  const a=texts[i],c=texts[j],ra=b(a.id),rc=b(c.id),area=intersect(ra,rc);
  const depthY=Math.min(ra.y+ra.h,rc.y+rc.h)-Math.max(ra.y,rc.y),depthX=Math.min(ra.x+ra.w,rc.x+rc.w)-Math.max(ra.x,rc.x);
  if(depthX>2&&depthY>2&&area>4&&area>.03*Math.min(ra.w*ra.h,rc.w*rc.h)&&!allowed(a.id,c.id))issue('text_overlap',[a.id,c.id],{area});
 }
 for(const line of svg.querySelectorAll('line')){
  const p=xy(line,line.x1.baseVal.value,line.y1.baseVal.value),q=xy(line,line.x2.baseVal.value,line.y2.baseVal.value);
  if(Math.abs(p.y-q.y)>.1||Math.abs(p.x-q.x)<5)continue;
  for(const t of texts){const r=b(t.id);
   const covered=[...svg.querySelectorAll('rect')].some(el=>{if(!(line.compareDocumentPosition(el)&Node.DOCUMENT_POSITION_FOLLOWING)||!(el.compareDocumentPosition(t)&Node.DOCUMENT_POSITION_FOLLOWING))return false;const fill=getComputedStyle(el).fill;if(fill==='none'||Number(getComputedStyle(el).fillOpacity)<1||Number(getComputedStyle(el).opacity)<1)return false;const c=box(el);return c.x<=Math.max(r.x,Math.min(p.x,q.x))&&c.x+c.w>=Math.min(r.x+r.w,Math.max(p.x,q.x))&&c.y<=p.y&&c.y+c.h>=p.y});
   if(!covered&&p.y>r.y+2&&p.y<r.y+r.h-2&&Math.min(p.x,q.x)<r.x+r.w-2&&Math.max(p.x,q.x)>r.x+2&&!allowed(line.id,t.id))issue('line_crosses_text',[line.id||'(line without id)',t.id],{y:p.y})}
 }
 for(const im of nodes.filter(e=>e.tagName==='image')){
  const r=b(im.id);if(im.getAttribute('data-pptx-role')==='background')continue; // Explicit intentional background only.
  for(const t of texts){const tb=b(t.id),area=intersect(r,tb);if(area>4&&area>.1*tb.w*tb.h&&!allowed(im.id,t.id))issue('image_text_overlap',[im.id,t.id],{area})}
 }
 for(const rule of contract?.rules||[]){
  const ids=rule.items||[],t=rule.tolerance??tol;
  try{
   if(rule.kind==='align'){
    const values=ids.map(id=>edge(id,rule.edge)+(rule.offsets?.[id]||0));
    if(values.length<2||values.some(v=>!Number.isFinite(v)))throw new Error('Invalid align rule');
    if(Math.max(...values)-Math.min(...values)>t)issue('alignment',ids,{edge:rule.edge,values,tolerance:t});
   }else if(rule.kind==='inside'){
    const [x,y,w,h]=rule.box||[b(rule.owner).x,b(rule.owner).y,b(rule.owner).w,b(rule.owner).h],pad=rule.inset||0;
    for(const id of ids){const r=b(id);if(r.x<x+pad-t||r.y<y+pad-t||r.x+r.w>x+w-pad+t||r.y+r.h>y+h-pad+t)issue('container_overflow',[id],{container:[x,y,w,h],box:r})}
   }else if(rule.kind==='gap'){
    const [a,c]=ids,vertical=rule.axis!=='x',gap=edge(c,vertical?'top':'left')-edge(a,vertical?'bottom':'right');
    if(gap<(rule.min??0)-t||(rule.max!==undefined&&gap>rule.max+t))issue('gap',ids,{gap,min:rule.min,max:rule.max});
   }else if(rule.kind==='avoid'){
    for(let i=0;i<ids.length;i++)for(let j=i+1;j<ids.length;j++)if(intersect(b(ids[i]),b(ids[j]))>t)issue('overlap',[ids[i],ids[j]],{});
   }else if(rule.kind==='equal-gap'){
    const vertical=rule.axis!=='x',gaps=ids.slice(1).map((id,i)=>edge(id,vertical?'top':'left')-edge(ids[i],vertical?'bottom':'right'));
    if(gaps.length<2||Math.max(...gaps)-Math.min(...gaps)>t)issue('unequal_gaps',ids,{gaps});
   }else throw new Error('Unknown rule '+rule.kind);
  }catch(e){issue('invalid_contract',ids,String(e.message));}
 }
 return {errors,bounds,rule_count:contract?.rules?.length||0};
};
