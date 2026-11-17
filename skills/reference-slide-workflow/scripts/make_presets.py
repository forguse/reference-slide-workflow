"""Rebuild the optional neutral presets from original native shapes and synthetic example content."""
from pathlib import Path
import argparse,html,json
SKILL=Path(__file__).resolve().parents[1]

def build(name,dest):
    blue=name=='academic-blue'
    c={'bg':'#F8FAFD','ink':'#142234','accent':'#073B85','secondary':'#5985B7','soft':'#E8EFF8','highlight':'#B3131C','line':'#B5C7DF'} if blue else {'bg':'#F5F1E8','ink':'#202624','accent':'#B64A2F','secondary':'#CC7A5D','soft':'#EAE2D4','highlight':'#B64A2F','line':'#C7BCAA'}
    font='Microsoft YaHei';left=58 if blue else 72;titley=65 if blue else 91
    profile={'schema':1,'name':name,'canvas':[1280,720],'language':'zh-CN',
      'typography':{'title':{'family':font,'size':34 if blue else 40,'weight':700},'body':{'family':font,'size':24,'weight':400},'caption':{'family':font,'size':18,'weight':400},'numeral':{'family':'Arial','size':44,'weight':700}},
      'palette':c,'margins':{'left':left,'right':left,'top':40,'bottom':38},
      'fixed_anchors':['Shared left edge for heading and body','Stable type hierarchy','Consistent emphasis color'],
      'flexible_compositions':['Evidence with interpretation','Comparison table','Three-stage process','Standalone cover and ending'],
      'identity_assets':[],'origin':'Original neutral preset; all example scores are synthetic',
      'writing':{'repeated_middle_dot_labels':False}}
    dest.mkdir(parents=True,exist_ok=True);(dest/'layouts').mkdir(exist_ok=True)
    (dest/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf-8')
    slides=[]
    def page(slug,title,job):
        elements=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" lang="zh-CN" font-family="{font}" data-pptx-page-role="{'section' if job=='chapter' else (job if job in ['cover','ending'] else 'content')}"><defs><linearGradient id="grad"><stop offset="0" stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["secondary"]}"/></linearGradient></defs>',f'<rect id="background" width="1280" height="720" fill="{c["bg"]}" data-pptx-role="background"/>'];rules=[]
        def rect(ident,x,y,w,h,fill,stroke='none'):
            elements.append(f'<rect id="{ident}" x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>')
        def line(ident,x,y,x2,y2,color=None,width=1.5):elements.append(f'<line id="{ident}" x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{color or c["line"]}" stroke-width="{width}"/>')
        def text(ident,x,y,content,size=24,weight=400,color=None,anchor='start',family=None):
            elements.append(f'<text id="{ident}" x="{x}" y="{y}" font-family="{family or font}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color or c["ink"]}">{html.escape(content)}</text>')
        def align(ids,edge='anchorX'):rules.append({'kind':'align','items':ids,'edge':edge,'tolerance':1})
        def finish():
            elements.append('</svg>');(dest/'layouts'/f'{slug}.svg').write_text(''.join(elements),encoding='utf-8')
            slides.append({'id':slug,'name':title,'svg':'layouts/'+slug+'.svg','notes':'All scores and scenarios on this page are synthetic demonstration content. No real project, person or organization is represented.',
              'contract':{'rules':rules,'allow_overlap':[],'review_focus':['Visible alignment of adjacent content','Role-based type sizes and density','Captions and evidence remain legible']}})
        if job=='cover':
            if blue:
                rect('cover-band',0,525,1280,150,'url(#grad)');line('cover-rule',92,170,1188,170)
                text('kicker',92,120,'项目方案演示',22,700,c['accent'])
                text('main-title',92,292,'城市雨水利用方案',58,700,c['accent'])
                text('subtitle',92,358,'方案比较与实施计划',30)
                text('footer-note',92,615,'示例内容，可替换为自己的项目',24,400,'#FFFFFF')
            else:
                text('kicker',72,90,'PROJECT STUDY',18,700,c['accent'],family='Arial');line('cover-rule',72,125,1208,125)
                text('main-title',72,266,'城市雨水',74,700)
                text('subtitle',72,380,'利用方案',74,700)
                text('footer-note',72,568,'方案比较与实施计划',28)
                text('cover-index',1142,352,'01',102,700,c['accent'],'end','Arial')
                text('cover-label',72,640,'示例内容，可替换为自己的项目',18,400,c['accent'])
            align(['kicker','main-title','subtitle','footer-note']);rules.append({'kind':'inside','items':['main-title','subtitle'],'box':[60,180,1150,250]});finish();return
        if job=='chapter':
            if blue:
                rect('chapter-band',0,200,1280,300,'url(#grad)');text('chapter-number',86,383,'01',108,700,'#B9CDEA',family='Arial')
                text('chapter-title',350,331,'方案评估',52,700,'#FFFFFF');text('chapter-subtitle',350,402,'比较条件、证据和实施顺序',26,400,'#FFFFFF');align(['chapter-title','chapter-subtitle'])
            else:
                text('chapter-number',72,172,'01',96,700,c['accent'],family='Arial');line('chapter-rule',72,228,1208,228)
                text('chapter-title',72,359,'方案评估',64,700);text('chapter-subtitle',72,431,'比较条件、证据和实施顺序',28);align(['chapter-number','chapter-title','chapter-subtitle'])
            finish();return
        if job=='ending':
            if blue:
                rect('ending-band',0,0,1280,14,'url(#grad)');text('end-title',640,320,'讨论与建议',64,700,c['accent'],'middle')
                line('end-rule',490,365,790,365,c['accent'],3);text('end-subtitle',640,440,'选择适合场地的方案，明确下一步验证任务',27,400,c['ink'],'middle')
            else:
                text('end-title',72,316,'讨论与建议',78,700);line('end-rule',72,380,1208,380,c['accent'],3)
                text('end-subtitle',72,459,'选择适合场地的方案，明确下一步验证任务',27);text('end-label',72,640,'END OF DEMONSTRATION',16,700,c['accent'],family='Arial')
            align(['end-title','end-subtitle'],'centerX' if blue else 'anchorX');finish();return
        if blue:
            rect('title-marker',0,20,28,55,c['accent']);text('page-title',left,titley,title,34,700,c['accent']);line('header-rule',left,96,1222,96)
        else:
            text('section-label',left,37,'PROJECT STUDY',15,700,c['accent'],family='Arial');text('page-title',left,titley,title,40,700);line('header-rule',left,125,1208,125)
        text('page-num',1210,690,str(len(slides)+1),16,400,c['ink'],'end','Arial')
        text('demo-note',left,687,'演示数据与示例情境',16,400,c['secondary']);rules.append({'kind':'inside','items':['page-title'],'box':[left,20,1150,90]})
        if job=='evidence':
            if blue:
                rect('chart-heading-bg',left,145,650,44,'url(#grad)');text('chart-heading',left+20,176,'综合评分（演示数据）',27,700,'#FFFFFF')
            else:text('chart-heading',left,188,'综合评分',27,700)
            x0=left+190;scale=3.95
            for i,(label,value) in enumerate([('雨水花园',78),('透水铺装',66),('调蓄设施',54)]):
                y=260+i*108;text(f'label-{i}',left,y+29,label,25,700)
                rect(f'bar-{i}',x0,y,round(value*scale),42,c['accent'] if i==0 else c['secondary'])
                text(f'value-{i}',x0+value*scale+15,y+30,str(value),25,700,c['ink'],family='Arial')
            line('chart-axis',x0,570,x0+395,570)
            for i in [0,50,100]:text('tick-'+str(i),x0+i*scale,604,str(i),18,400,c['ink'],'middle','Arial')
            bx=790 if blue else 810
            text('body-heading',bx,176 if blue else 188,'场地条件决定方案顺序',27,700,c['accent'])
            for i,txt in enumerate(['先利用现有空地布置雨水花园。','再将透水铺装纳入道路改造。','调蓄设施需要考虑后续维护。']):text(f'body-{i}',bx,280+i*50,txt,22)
            text('body-conclusion',bx,557,'先试点，再评估运行效果',25,700,c['highlight'])
            align(['chart-heading','body-heading'],'baseline');align(['body-heading','body-0','body-1','body-2','body-conclusion']);align(['label-0','label-1','label-2']);align(['bar-0','bar-1','bar-2'],'left')
            rules.append({'kind':'inside','items':['body-heading','body-0','body-1','body-2','body-conclusion'],'box':[bx-2,140,440,470]})
        elif job=='comparison':
            x=left;cw=[250,440,444 if blue else 422];y=180;rh=91
            if blue:rect('table-header',x,y,sum(cw),65,'url(#grad)')
            else:line('table-top',x,y+62,x+sum(cw),y+62,c['ink'],2)
            headers=['比较维度','雨水花园','透水铺装']
            for j,hdr in enumerate(headers):text(f'th-{j}',x+sum(cw[:j])+22,y+43,hdr,26,700,'#FFFFFF' if blue else c['ink'])
            cells=[['建设条件','可利用绿地与低洼空间','可结合道路更新施工'],['主要用途','就地汇集和滞留雨水','减少硬质地面的径流'],['维护重点','植物养护与溢流口检查','清理表面与恢复渗透能力']]
            for i,row in enumerate(cells):
                yy=y+65+i*rh
                if blue and i%2==0:rect(f'row-bg-{i}',x,yy,sum(cw),rh,c['soft'])
                line(f'row-line-{i}',x,yy+rh,x+sum(cw),yy+rh)
                for j,cell in enumerate(row):text(f'cell-{i}-{j}',x+sum(cw[:j])+22,yy+55,cell,24,700 if j==0 else 400)
                align([f'cell-{i}-{j}' for j in range(3)],'baseline')
            text('comparison-conclusion',left,610,'方案选择应同时考虑施工条件和持续维护能力',27,700,c['accent'])
            for j in range(3):align([f'th-{j}']+[f'cell-{i}-{j}' for i in range(3)])
        elif job=='process':
            xs=[left,left+395,left+790];width=344
            for i,(heading,body,outcome) in enumerate([('场地勘测','记录汇水路径与可用空间','形成场地条件清单'),('小范围试点','验证构造与实际运行情况','获得可比较的现场记录'),('运行评估','对照目标调整后续方案','确定扩大实施的条件')]):
                x=xs[i];text(f'step-number-{i}',x+20,217,f'0{i+1}',42,700,c['secondary'],family='Arial')
                rect(f'step-box-{i}',x,246,width,66,'url(#grad)' if blue else c['soft'])
                text(f'step-title-{i}',x+20,289,heading,29,700,'#FFFFFF' if blue else c['ink'])
                text(f'step-body-{i}',x+20,381,body,23);text(f'step-output-{i}',x+20,454,outcome,23,700,c['accent'])
                if i<2:
                    line(f'arrow-{i}',x+width+8,280,x+width+42,280,c['secondary'],3)
                    elements.append(f'<path d="M {x+width+35} 273 L {x+width+42} 280 L {x+width+35} 287" fill="none" stroke="{c["secondary"]}" stroke-width="3"/>')
                align([f'step-number-{i}',f'step-title-{i}',f'step-body-{i}',f'step-output-{i}'])
            text('process-conclusion',left,597,'每一步留下可核查的记录，为下一步提供依据',28,700,c['highlight'])
            rules.append({'kind':'equal-gap','items':['step-box-0','step-box-1','step-box-2'],'axis':'x','tolerance':1})
            align(['step-title-0','step-title-1','step-title-2'],'baseline')
        finish()
    for slug,title,job in [('cover','城市雨水利用方案','cover'),('chapter','方案评估','chapter'),('evidence','三种措施的示例评估','evidence'),('comparison','两类措施的适用条件','comparison'),('process','试点实施流程','process'),('ending','讨论与建议','ending')]:page(slug,title,job)
    (dest/'deck.json').write_text(json.dumps({'title':name+' demonstration','profile':'profile.json','slides':slides},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=SKILL/'assets/presets');a=p.parse_args()
    for name in ['academic-blue','editorial-light']:build(name,a.out/name)
    print('Built two explicitly optional, identity-free presets.')
