import json,re,sys
# Markdown を Google ドキュメントの1つのタブに流し込む batchUpdate の要求を作る。送るのは Claude（Google ドキュメントのコネクタの update_doc）。
# 文書の現在の位置を読まずに済むよう、ブロックを後ろから順にタブの先頭（index 1）へ挿入する。
def u16(s): return len(s.encode('utf-16-le'))//2
INL=re.compile(r'\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)\s]+)\)|`([^`]+)`')
def inline(s):
  """return plain text and list of (start,end,style)"""
  out='';sty=[];pos=0
  for m in INL.finditer(s):
    out+=s[pos:m.start()]
    if m.group(1) is not None:
      inner,isty=inline(m.group(1)); st=u16(out); out+=inner
      sty.append((st,u16(out),{'bold':True},'bold'))
      sty+=[(st+a,st+b,c,f) for a,b,c,f in isty]
    elif m.group(2) is not None:
      st=u16(out); out+=m.group(2); sty.append((st,u16(out),{'link':{'url':m.group(3)}},'link'))
    else:
      st=u16(out); out+=m.group(4); sty.append((st,u16(out),{'weightedFontFamily':{'fontFamily':'Roboto Mono'}},'weightedFontFamily'))
    pos=m.end()
  out+=s[pos:]; return out,sty
def blocks(md):
  lines=md.split('\n'); i=0; B=[]
  while i<len(lines):
    l=lines[i]
    if l.startswith('```'):
      j=i+1; buf=[]
      while j<len(lines) and not lines[j].startswith('```'): buf.append(lines[j]); j+=1
      B.append(('code',buf)); i=j+1; continue
    if l.strip().startswith('|') and i+1<len(lines) and re.match(r'^\s*\|[\s\-:|]+\|\s*$',lines[i+1]):
      rows=[]; j=i
      while j<len(lines) and lines[j].strip().startswith('|'):
        if j!=i+1: rows.append([c.strip().replace('\\|','|') for c in re.split(r'(?<!\\)\|',lines[j].strip())[1:-1]])
        j+=1
      B.append(('table',rows)); i=j; continue
    m=re.match(r'^(#{1,6})\s+(.*)',l)
    if m: B.append(('h',len(m.group(1)),m.group(2))); i+=1; continue
    m=re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)',l)
    if m:
      lvl=len(m.group(1).replace('\t','  '))//2; B.append(('li',lvl,'num' if m.group(2)[0].isdigit() else 'bul',m.group(3))); i+=1; continue
    if l.strip()=='---': B.append(('hr',)); i+=1; continue
    if l.strip()=='': B.append(('blank',)); i+=1; continue
    B.append(('p',l)); i+=1
  return B
def text_reqs(tab,paras):
  """paras: list of (kind,text,styles,extra)。タブの先頭に挿入する要求"""
  idx=1; text=''; reqs=[]; prs=[]
  for kind,t,sty,extra in paras:
    s=idx+u16(text); body=('\t'*extra.get('lvl',0) if kind=='li' else '')+t
    text+=body+'\n'; e=s+u16(body)
    off=s+(extra.get('lvl',0) if kind=='li' else 0)
    prs.append((kind,s,e+1,extra,[(off+a,off+b,c,f) for a,b,c,f in sty]))
  end=idx+u16(text)
  reqs.append({'insertText':{'location':{'index':idx,'tabId':tab},'text':text}})
  # 挿入した段落は挿入先の段落の書式（見出し・箇条書き）を引き継ぐので、先に戻す
  reqs.append({'deleteParagraphBullets':{'range':{'startIndex':idx,'endIndex':end,'tabId':tab}}})
  reqs.append({'updateParagraphStyle':{'range':{'startIndex':idx,'endIndex':end,'tabId':tab},'paragraphStyle':{'namedStyleType':'NORMAL_TEXT'},'fields':'namedStyleType'}})
  reqs.append({'updateTextStyle':{'range':{'startIndex':idx,'endIndex':end,'tabId':tab},'textStyle':{},'fields':'bold,link,weightedFontFamily'}})
  # bullets: group contiguous li of same type, apply from last to first (tabs removed shift indices)
  groups=[];cur=None
  for p in prs:
    if p[0]=='li':
      if cur and cur[0]==p[3]['type'] and cur[2]==p[1]: cur[2]=p[2]; cur[3].append(p)
      else: cur=[p[3]['type'],p[1],p[2],[p]]; groups.append(cur)
    else: cur=None
  for kind,s,e,extra,sty in prs:
    if kind=='h': reqs.append({'updateParagraphStyle':{'range':{'startIndex':s,'endIndex':e,'tabId':tab},'paragraphStyle':{'namedStyleType':f"HEADING_{min(extra['n'],6)}"},'fields':'namedStyleType'}})
    for a,b,c,f in sty:
      if b>a: reqs.append({'updateTextStyle':{'range':{'startIndex':a,'endIndex':b,'tabId':tab},'textStyle':c,'fields':f}})
    if kind=='code' and e-1>s: reqs.append({'updateTextStyle':{'range':{'startIndex':s,'endIndex':e-1,'tabId':tab},'textStyle':{'weightedFontFamily':{'fontFamily':'Roboto Mono'}},'fields':'weightedFontFamily'}})
  for g in reversed(groups):
    reqs.append({'createParagraphBullets':{'range':{'startIndex':g[1],'endIndex':g[2]-1,'tabId':tab},'bulletPreset':'NUMBERED_DECIMAL_ALPHA_ROMAN' if g[0]=='num' else 'BULLET_DISC_CIRCLE_SQUARE'}})
  return reqs
def table_reqs(tab,rows):
  """タブの先頭に表を挿入する要求。表の前に空の段落が1つ入り、表は index 2 から始まる"""
  ncol=max(len(r) for r in rows); rows=[r+['']*(ncol-len(r)) for r in rows]
  reqs=[{'insertTable':{'rows':len(rows),'columns':ncol,'location':{'index':1,'tabId':tab}}}]
  t=2; cells=[]
  for ri,r in enumerate(rows):
    for ci,txt in enumerate(r): cells.append((t+3+ri*(2*ncol+1)+2*ci,txt,ri==0))
  for si,txt,hdr in sorted(cells,key=lambda x:-x[0]):
    plain,sty=inline(txt)
    if not plain: continue
    reqs.append({'insertText':{'location':{'index':si,'tabId':tab},'text':plain}})
    if hdr: reqs.append({'updateTextStyle':{'range':{'startIndex':si,'endIndex':si+u16(plain),'tabId':tab},'textStyle':{'bold':True},'fields':'bold'}})
    for a,b,c,f in sty:
      if b>a: reqs.append({'updateTextStyle':{'range':{'startIndex':si+a,'endIndex':si+b,'tabId':tab},'textStyle':c,'fields':f}})
  return reqs
def segments(md):
  """表と、表に挟まれた段落のまとまりに分ける"""
  segs=[]; paras=[]; prev=None
  for b in blocks(md):
    k=b[0]
    if k=='table':
      if paras: segs.append(('text',paras)); paras=[]
      segs.append(('table',b[1])); prev='table'; continue
    if k=='blank':
      if prev not in (None,'blank','li','h'): paras.append(('p','',[],{}))
      prev='blank'; continue
    if k=='hr': paras.append(('p','',[],{})); prev='blank'; continue
    if k=='h':
      t,s=inline(b[2]); paras.append(('h',t,s,{'n':b[1]}))
    elif k=='li':
      t,s=inline(b[3]); paras.append(('li',t,s,{'lvl':b[1],'type':b[2]}))
    elif k=='code':
      for cl in b[1]: paras.append(('code',cl,[],{}))
    else:
      t,s=inline(b[1]); paras.append(('p',t,s,{}))
    prev=k
  if paras: segs.append(('text',paras))
  return segs
def build(tab,md,clear_end=None):
  reqs=[]
  if clear_end and clear_end>2: reqs.append({'deleteContentRange':{'range':{'startIndex':1,'endIndex':clear_end-1,'tabId':tab}}})
  for kind,v in reversed(segments(md)):
    reqs+=text_reqs(tab,v) if kind=='text' else table_reqs(tab,v)
  reqs.append({'updateDocumentStyle':{'documentStyle':{'documentFormat':{'documentMode':'PAGELESS'}},'fields':'documentFormat'}})
  return reqs

if __name__=='__main__':
  # 使い方: python3 md2tab.py <tabId> <markdownファイル> [--clear-end <タブの本文の最後の endIndex>]
  # 出力（要求の JSON 配列）を update_doc の requests に渡す。タブは空か、--clear-end で中身を消す前提
  tab,path=sys.argv[1:3]
  clear_end=int(sys.argv[sys.argv.index('--clear-end')+1]) if '--clear-end' in sys.argv else None
  print(json.dumps(build(tab,open(path,encoding='utf-8').read(),clear_end),ensure_ascii=False))
