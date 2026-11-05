import asyncio, json, random, secrets, time, os
from pathlib import Path
from aiohttp import web, WSMsgType

NAMES=['배시언','홍은우','홍연우','백다솜','강태겸']
STATS=[[1,2,3,5,4],[5,5,3,4,2],[2,1,5,5,3],[3,3,4,5,2],[5,4,3,2,5]]
ROOMS={'music':('밴드부실','방음재가 붙은 벽과 먼지 쌓인 악기들. 익숙한 공간이지만 오늘은 누구도 연주하지 않는다.',.008),'hall':('3층 복도','유리창으로 흐린 빛이 들어온다. 교실 문 너머로 희미한 긁는 소리가 들린다.',.04),'nurse':('보건실','흰 커튼과 소독약 냄새. 약품함 한쪽이 열려 있다.',.025),'roof':('옥상','차가운 바람이 철제 난간을 울린다. 아래 운동장은 기이할 만큼 조용하다.',.018),'gate':('정문','철문 너머로 감염자들이 서성인다. 발을 잘못 디디면 단번에 시선이 쏠릴 것이다.',.22),'library':('도서관','책장 사이로 종이 넘기는 소리가 들린다.',.045),'cafeteria':('급식실','식판과 의자가 뒤엉켜 있다.',.09),'gym':('체육관','텅 빈 관중석 너머로 둔탁한 울림이 퍼진다.',.13),'lab':('과학실','깨진 비커와 약품 냄새가 남아 있다.',.11),'office':('교무실','책상마다 서류가 흩어져 있다.',.055),'storage':('창고','먼지 쌓인 선반에 물건들이 남아 있다.',.12),'yard':('운동장','넓은 공간에 몸을 숨길 곳이 적다.',.19),'broadcast':('방송실','꺼진 마이크와 송출 장비가 놓여 있다.',.19),'basement':('지하 기계실','배관에서 뜨거운 증기가 샌다.',.24),'class1':('1학년 교실','책상 사이에 가방들이 널려 있다.',.05),'class3':('3학년 교실','급히 떠난 학생들의 흔적.',.08),'stairs':('비상계단','철제 계단에 핏자국이 이어진다.',.16),'parking':('지하 주차장','어둠 속에서 경보음이 희미하게 울린다.',.27),'auditorium':('강당','커튼 뒤에 누군가 숨은 듯하다.',.17),'security':('경비실','무전기와 감시 모니터가 남아 있다.',.12)}
LOOT={'music':['기타 피크','드럼 스틱','낡은 악보','곰인형','생수'],'hall':['손전등','송충이','커피 캔','건전지'],'nurse':['붕대','응급약','딸기 사탕','리본 머리핀'],'roof':['작은 손거울','에너지바','생수'],'gate':['에너지바','손전등','붕대','방검 조끼'],'library':['정신 안정제','커피 캔','야구 방망이'],'cafeteria':['생수','에너지바','통조림','철제 파이프'],'gym':['야구 방망이','운동 보호대','붕대'],'lab':['정신 안정제','소독약','응급약'],'office':['방검 조끼','응급약','손전등'],'storage':['철제 파이프','소방 도끼','방검 조끼','에너지바'],'yard':['운동 보호대','에너지바','생수'],'broadcast':['정신 안정제','손전등','낡은 악보','홍연우의 머리끈'],'basement':['철제 파이프','소독약','통조림'],'class1':['배시언의 기타 피크','생수','딸기 사탕'],'class3':['홍은우의 수첩','커피 캔','붕대'],'stairs':['붕대','송충이','손전등'],'parking':['방검 조끼','에너지바','철제 파이프'],'auditorium':['백다솜의 키링','드럼 스틱','통조림'],'security':['강태겸의 손목밴드','손전등','응급약']}
GIFTS={'곰인형':[0,0,3,1,1],'송충이':[-2,-1,-3,-2,-1],'기타 피크':[3,1,0,2,2],'드럼 스틱':[0,1,0,1,3],'낡은 악보':[1,1,1,3,1],'딸기 사탕':[0,1,3,2,1],'리본 머리핀':[-1,0,3,2,0],'작은 손거울':[0,0,2,3,0],'커피 캔':[0,3,-1,2,2],'에너지바':[1,2,1,1,3],'생수':[1,1,1,1,1],'붕대':[1,1,1,1,2],'응급약':[2,2,2,2,2],'손전등':[1,2,1,1,1],'배시언의 기타 피크':[3,0,0,1,1],'홍은우의 수첩':[0,3,1,1,1],'홍연우의 머리끈':[0,1,3,2,0],'백다솜의 키링':[0,0,1,3,1],'강태겸의 손목밴드':[1,1,0,1,3]}
LINES={'music':['앰프는 건드리지 마. 소리 나면 끝이야.','여긴 잠깐 쉬기 좋겠어. 문부터 잠그자.','저기, 우리가 연습하던 자리잖아…','누나가 악보라도 챙겨 둘까?','다들 괜찮지? 하하, 여기서 드럼 치진 않을게!'],'hall':['위험해 보이는데. 문 열기 전에 소리부터 들어.','발자국이 이어져 있어. 조심해서 가자.','잠깐, 저쪽에 뭐 움직였어.','쉿. 누나 귀에 뭔가 들리거든?','좋아, 내가 앞에서 확인할게!'],'nurse':['약부터 챙겨. 쓸데없는 건 만지지 말고.','붕대가 필요할 수도 있어.','커튼 뒤에 누가 있는 것 같아.','누나가 약 좀 찾아볼게~','다친 사람 있으면 바로 말해!'],'roof':['문 닫을 때 소리 조심해.','아래쪽 길부터 확인하자.','바람 때문에 발소리가 안 들려.','와, 바람 장난 아니네~','내가 문 잡고 있을게!'],'gate':['저기 봐. 꽤 많이 모여 있는데.','정면 돌파는 위험해.','저쪽 그림자… 하나 더 있어.','누나도 여기선 장난 못 치겠네.','다들 뒤로 붙어! 내가 앞을 볼게!']}
ITEMS={'생수':('consume','정신력 +8 / 피로 -10'),'응급약':('consume','생명력 +40'),'붕대':('consume','생명력 +20'),'에너지바':('consume','피로 -20'),'커피 캔':('consume','피로 -25 / 정신력 +5'),'딸기 사탕':('consume','정신력 +15'),'정신 안정제':('consume','정신력 +35'),'통조림':('consume','생명력 +12 / 피로 -12 / 허기 -30'),'소독약':('consume','감염도 -15'),'배시언의 기타 피크':('keepsake','배시언의 소지품'),'홍은우의 수첩':('keepsake','홍은우의 소지품'),'홍연우의 머리끈':('keepsake','홍연우의 소지품'),'백다솜의 키링':('keepsake','백다솜의 소지품'),'강태겸의 손목밴드':('keepsake','강태겸의 소지품'),'야구 방망이':('weapon','공격력 +8'),'철제 파이프':('weapon','공격력 +11'),'소방 도끼':('weapon','공격력 +17'),'운동 보호대':('armor','방어력 +5'),'방검 조끼':('armor','방어력 +11')}
RECOVER={'생수':(0,8,-10,0),'응급약':(40,0,0,0),'붕대':(20,0,0,0),'에너지바':(0,0,-20,0),'커피 캔':(0,5,-25,0),'딸기 사탕':(0,15,0,0),'정신 안정제':(0,35,0,0),'통조림':(12,0,-12,0),'소독약':(0,0,0,-15)}
NPCS={
 'library':{'name':'도서관의 학생','need':'생수','reward':'정신 안정제','dialogue':'목이 너무 말라요… 물 한 병만 구해 주실래요?'},
 'nurse':{'name':'부상당한 교사','need':'붕대','reward':'응급약','dialogue':'다리에 피가 멈추지 않아요. 붕대를 부탁해요.'},
 'cafeteria':{'name':'굶주린 생존자','need':'통조림','reward':'운동 보호대','dialogue':'이틀째 굶었어요. 먹을 것을 주면 보호대를 드릴게요.'},
 'basement':{'name':'감염이 진행 중인 경비원','need':'소독약','reward':'방검 조끼','dialogue':'상처가 이상해요… 소독약이라도 있으면…'},
 'auditorium':{'name':'숨어 있는 후배','need':'에너지바','reward':'드럼 스틱','dialogue':'너무 무서워서 못 나가겠어요. 먹을 것 좀 주세요.'}
}
# 전투 전리품은 구역의 조사 물자(최대 4개)와 별도로 지급됩니다.
ZOMBIE_DROPS=[('붕대',25),('생수',20),('에너지바',18),('철제 파이프',10),('운동 보호대',8),('정신 안정제',7),('응급약',7),('방검 조끼',5)]
RAID_DROPS=[('소방 도끼',25),('방검 조끼',25),('응급약',20),('정신 안정제',15),('운동 보호대',15)]
def weighted_drop(table):
 return random.choices([name for name,_ in table],weights=[weight for _,weight in table],k=1)[0]
def award_drop(g,p,item,source):
 if len(p['inventory'])>=20:
  g.emit(f'🎒 {p["name"]}의 가방이 가득 차 [{item}] 전리품을 획득하지 못했다. ({source})')
  return False
 p['inventory'].append(item)
 g.emit(f'🎁 {p["name"]}이(가) {source} 보상으로 [{item}] 획득! ({len(p["inventory"])}/20칸)')
 return True
FOOD={'생수':(0,10),'에너지바':(32,0),'통조림':(45,0),'딸기 사탕':(12,0),'커피 캔':(0,5)}
rooms={}
class Game:
 def __init__(self,code):
  self.code=code;self.players={};self.sockets={};self.events=[];self.enemy=None;self.seq=0;self.supplies={r:4 for r in ROOMS};self.notices=[];self.private={};self.last_event=time.time();self.raid=None;self.follow={};self.npc_done=set();self.last_hunger=time.time();self.npc_encounters={};self.last_npc=time.time();self.last_supply=time.time();self.carry={};self.traps=set();self.pending_requests={};self.combat_joined={}
 def emit(self,msg):
  self.seq+=1;self.events.append({'id':self.seq,'time':time.strftime('%H:%M:%S'),'text':msg});self.events=self.events[-60:]
 async def notify(self,player,kind,message,source=None,**extra):
  sock=next((self.sockets.get(t) for t,q in self.players.items() if q is player),None)
  if sock and not sock.closed:
   await sock.send_json({'type':'notification','kind':kind,'text':message,'from':source,'time':time.strftime('%H:%M:%S'),**extra})
 def state(self):
  return {'type':'state','code':self.code,'players':[{k:v for k,v in p.items() if k!='token'} for p in self.players.values()],'events':self.events,'enemy':self.enemy,'rooms':ROOMS,'seq':self.seq,'supplies':self.supplies,'server_time':time.time(),'notices':self.notices[-20:],'raid':self.raid,'item_info':ITEMS,'npcs':self.npc_encounters,'npc_done':[r for r,_ in self.npc_done],'follow':self.follow,'npc_encounters':self.npc_encounters,'carry':self.carry,'combat_joined':{k:list(v) for k,v in self.combat_joined.items()}}
 async def broadcast(self):
  data=json.dumps(self.state(),ensure_ascii=False)
  for ws in list(self.sockets.values()):
   if not ws.closed:
    try:await ws.send_str(data)
    except Exception:pass

def clamp(v):return max(0,min(100,v))
def get_player(g,token):return g.players.get(token)
async def portrait(req):
 i=req.match_info['id']
 if i not in ('0','1','2','3','4'):raise web.HTTPNotFound()
 return web.FileResponse(Path(__file__).with_name('assets')/f'portrait_{i}.png')
async def index(req):return web.FileResponse(Path(__file__).with_name('index.html'))
async def socket(req):
 ws=web.WebSocketResponse(heartbeat=25,max_msg_size=8192);await ws.prepare(req);g=None;token=None
 try:
  async for msg in ws:
   if msg.type!=WSMsgType.TEXT:continue
   try:m=json.loads(msg.data)
   except Exception:continue
   cmd=m.get('cmd');
   if cmd in ('create','join') and not token:
    code=''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789',k=5)) if cmd=='create' else str(m.get('code','')).strip().upper()
    if cmd=='create':
     while code in rooms:code=''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789',k=5))
     rooms[code]=Game(code)
    g=rooms.get(code)
    if not g:await ws.send_json({'type':'error','message':'방을 찾을 수 없습니다.'});continue
    char=m.get('char')
    if not isinstance(char,int) or char not in range(5) or any(p['char']==char for p in g.players.values()):await ws.send_json({'type':'error','message':'이미 선택된 캐릭터이거나 잘못된 선택입니다.'});continue
    if len(g.players)>=5:await ws.send_json({'type':'error','message':'방이 가득 찼습니다.'});continue
    token=secrets.token_hex(12);g.players[token]={'id':token[:8],'char':char,'name':NAMES[char],'room':'music','hp':100,'mental':100,'fatigue':0,'infection':0,'inventory':['생수'],'equipment':{'weapon':None,'armor':None},'bonds':{str(i): (95 if {char,i}=={1,2} else 75 if i!=char else 100) for i in range(5)},'ready':False,'unconscious_until':0,'deaths':0,'hunger':0,'heal_cooldown':0,'injuries':[],'infected_parts':[],'romance':{},'limb_removed':False}
    g.sockets[token]=ws;g.emit(f'{NAMES[char]}이(가) 합류했다.');await ws.send_json({'type':'welcome','code':code,'token':token,'char':char});await g.broadcast();continue
   if not g or not token:continue
   p=get_player(g,token)
   if not p:continue
   now=time.time()
   if p.get('unconscious_until',0) and now>=p['unconscious_until']:
    p['unconscious_until']=0;p['fatigue']=60;g.emit(f'{p["name"]}이(가) 의식을 되찾았다. 피로 60%.')
   if cmd not in ('chat','private_chat','respawn') and p.get('unconscious_until',0)>now:
    await ws.send_json({'type':'error','message':f'기절 상태입니다. {int(p["unconscious_until"]-now+59)//60}분 후 행동할 수 있습니다.'})
    await g.broadcast();continue
   # 위치별 감염자와 레이드 보스가 살아 있으면 탐색과 휴식은 봉쇄.
   battle=(g.enemy and g.enemy['room']==p['room']) or (g.raid and g.raid['room']==p['room'])
   if battle and cmd in ('search','rest','move','trap'):
    await ws.send_json({'type':'error','message':'전투 중에는 조사·휴식·이동할 수 없습니다. 공격하거나 도주하세요.'});continue
   if cmd in ('dm_request','follow_request'):
    other=next((q for q in g.players.values() if q['char']==m.get('target') and q is not p and q['room']==p['room']),None)
    if other:
     typ='dm_request' if cmd=='dm_request' else 'follow_request'
     g.pending_requests[(typ,p['char'],other['char'])]=now
     await g.notify(other,typ,f'{p["name"]}이(가) '+('1:1 대화를 신청했습니다.' if typ=='dm_request' else '동행을 요청했습니다.'),p['char'])
     await ws.send_json({'type':'notification','kind':'info','text':f'{other["name"]}에게 요청을 보냈습니다.','from':other['char']})
    continue
   if cmd=='request_reply':
    kind=m.get('kind');source=m.get('target');accepted=m.get('accept') is True
    key=(kind,source,p['char'])
    if kind not in ('dm_request','follow_request') or key not in g.pending_requests:continue
    del g.pending_requests[key]
    other=next((q for q in g.players.values() if q['char']==source),None)
    if other and other['room']==p['room']:
     if accepted and kind=='follow_request':g.follow[str(other['char'])]=p['char']
     await g.notify(other,'request_result',f'{p["name"]}이(가) '+('1:1 대화' if kind=='dm_request' else '동행')+' 요청을 '+('수락했습니다.' if accepted else '거절했습니다.'),p['char'],accepted=accepted,request_kind=kind)
     await ws.send_json({'type':'request_result','kind':kind,'target':source,'accepted':accepted})
     if accepted and kind=='follow_request':g.emit(f'{other["name"]}이(가) {p["name"]}과 동행을 시작했다.')
    await g.broadcast();continue
   if cmd=='combat_join':
    enemy=g.enemy if g.enemy and g.enemy['room']==p['room'] else g.raid if g.raid and g.raid['room']==p['room'] else None
    if enemy:
     g.combat_joined.setdefault(p['room'],set()).add(p['char'])
     g.emit(f'⚔ {p["name"]}이(가) 전투에 합류했다!')
     await g.broadcast()
    continue
   if cmd=='private_chat':
    other=next((q for q in g.players.values() if q['char']==m.get('target') and q is not p),None)
    t=str(m.get('text','')).strip()[:180]
    if other and t and other['room']==p['room']:
     payload={'type':'private','from':p['char'],'to':other['char'],'text':t,'time':time.strftime('%H:%M:%S')}
     for key in (token,next(k for k,v in g.players.items() if v is other)):
      w=g.sockets.get(key)
      if w and not w.closed:await w.send_json(payload)
    continue
   if cmd=='respawn':
    if p['hp']>0:continue
    p.update(room='music',hp=100,mental=100,fatigue=0,infection=0,inventory=['생수'],equipment={'weapon':None,'armor':None},unconscious_until=0,hunger=0,heal_cooldown=0,injuries=[],infected_parts=[],limb_removed=False)
    g.emit(f'{p["name"]}이(가) 처음부터 다시 생존을 시작했다.');await g.broadcast();continue
   if p['hp']<=0:
    await ws.send_json({'type':'error','message':'사망했습니다. 다시 시작을 선택하세요.'});continue
   if cmd=='chat':
    t=str(m.get('text','')).strip()[:180]
    if t:
     payload={'type':'public_chat','room':p['room'],'from':p['char'],'text':t,'time':time.strftime('%H:%M:%S')}
     for key,q in g.players.items():
      if q['room']==p['room']:
       w=g.sockets.get(key)
       if w and not w.closed:await w.send_json(payload)
   elif cmd=='follow':
    other=next((q for q in g.players.values() if q['char']==m.get('target') and q is not p and q['room']==p['room']),None)
    if other:g.follow[str(p['char'])]=other['char'];g.emit(f'{p["name"]}이(가) {other["name"]}을(를) 따라가기 시작했다.')
   elif cmd=='unfollow':
    g.follow.pop(str(p['char']),None);g.emit(f'{p["name"]}이(가) 동행을 해제했다.')
   elif cmd=='discard':
    item=m.get('item')
    if item in p['inventory']:p['inventory'].remove(item);g.emit(f'{p["name"]}이(가) [{item}]을(를) 버렸다.')
   elif cmd=='npc_talk':
    npc=g.npc_encounters.get(p['room'])
    if npc:await ws.send_json({'type':'npc_dialogue','npc':npc,'done':p['room'] in g.npc_done})
   elif cmd=='npc_quest':
    r=p['room'];npc=g.npc_encounters.get(r)
    if npc and (r,npc['name']) not in g.npc_done and npc['need'] in p['inventory'] and len(p['inventory'])<=20:
     p['inventory'].remove(npc['need']);p['inventory'].append(npc['reward']);g.npc_done.add((r,npc['name']));g.emit(f'✓ {p["name"]}이(가) {npc["name"]}의 부탁을 들어주고 [{npc["reward"]}]을(를) 받았다.')
   
   elif cmd=='trap':
    if p['room']=='broadcast':
     g.emit(f'📻 {p["name"]}이(가) 방송 기계를 고쳤다. 갑자기 교내 스피커에서 비명이 울려 퍼진다!')
     spawn(g,p['room'],p,force=True)
    elif p['room']=='lab':
     if random.random()<.65:p['infection']=clamp(p['infection']+12);g.emit(f'⚠ {p["name"]}이(가) 실험 약품을 건드려 감염 위험이 커졌다!')
     else:award_drop(g,p,'소독약','과학실 약품 실험')
    else:g.emit('수상한 장치를 발견하지 못했다.')
   elif cmd=='carry':
    other=next((q for q in g.players.values() if q['char']==m.get('target') and q is not p and q['room']==p['room'] and q['hp']>0 and q.get('unconscious_until',0)>now),None)
    if other:g.carry[str(other['char'])]=p['char'];g.emit(f'🤝 {p["name"]}이(가) 기절한 {other["name"]}을(를) 업었다.')
   elif cmd=='release':
    for k,v in list(g.carry.items()):
     if v==p['char']:g.carry.pop(k,None)
    g.emit(f'{p["name"]}이(가) 동료를 내려놓았다.')
   elif cmd=='treat':
    other=next((q for q in g.players.values() if q['char']==m.get('target') and q is not p and q['room']==p['room'] and q['hp']>0),None)
    if other and '붕대' in p['inventory'] and now>=p.get('heal_cooldown',0):
     p['inventory'].remove('붕대');p['heal_cooldown']=now+300;other['hp']=clamp(other['hp']+25);g.emit(f'✚ {p["name"]}이(가) {other["name"]}의 상처를 치료했다. 생명력 +25')
   elif cmd=='confess':
    other=next((q for q in g.players.values() if q['char']==m.get('target') and q is not p and q['room']==p['room']),None)
    if other and p['bonds'].get(str(other['char']),0)>=85:
     other.setdefault('romance',{})[str(p['char'])]='pending'
     await g.notify(other,'confession',f'{p["name"]}이(가) 당신에게 고백했습니다. 수락하거나 거절해 주세요.',p['char'])
     await ws.send_json({'type':'notification','kind':'info','text':f'{other["name"]}에게 고백을 전했습니다. 답변을 기다려 주세요.','from':other['char']})
   elif cmd=='confess_reply':
    other=next((q for q in g.players.values() if q['char']==m.get('target') and q is not p),None)
    if other and p.setdefault('romance',{}).get(str(other['char']))=='pending':
     yes=m.get('accept') is True
     p['romance'][str(other['char'])]='accepted' if yes else 'rejected'
     other.setdefault('romance',{})[str(p['char'])]='accepted' if yes else 'rejected'
     await g.notify(other,'confession_result',f'{p["name"]}이(가) 고백을 '+('수락했습니다. 이제 연인입니다!' if yes else '거절했습니다.'),p['char'])
     await ws.send_json({'type':'notification','kind':'confession_result','text':f'{other["name"]}의 고백을 '+('수락했습니다.' if yes else '거절했습니다.'),'from':other['char']})
     g.emit(f'💌 {p["name"]}이(가) {other["name"]}의 고백을 '+('받아들였다.' if yes else '거절했다.'))
   elif cmd=='amputate':
    required=['소방 도끼','붕대','소독약']
    if p['infection']>=35 and all(x in p['inventory'] for x in required) and not p.get('limb_removed'):
     for x in required:p['inventory'].remove(x)
     p['infection']=0;p['hp']=max(1,p['hp']-30);p['limb_removed']=True;p['injuries']=['절단 후유증'];p['infected_parts']=[]
     g.emit(f'⚠ {p["name"]}의 감염 부위를 절단했다. 감염도 0, 생명력 -30. 영구 후유증이 남았다.')
   elif cmd=='move':
    dest=m.get('room')
    if dest not in ROOMS:continue
    if p['mental']<=0:g.emit(f'{p["name"]}은(는) 정신이 혼란스러워 이동하지 못했다.');continue
    p['room']=dest;
    for q in g.players.values():
     if q is not p and g.carry.get(str(q['char']))==p['char'] and q['hp']>0:
      q['room']=dest;g.emit(f'🤝 {p["name"]}이(가) {q["name"]}을(를) 업고 이동했다.')
    for q in g.players.values():
     if q is not p and g.follow.get(str(q['char']))==p['char'] and q['room']!=dest and q['hp']>0 and q['mental']>0 and q['unconscious_until']<=now:
      q['room']=dest;q['fatigue']=clamp(q['fatigue']+4);g.emit(f'{q["name"]}이(가) {p["name"]}을(를) 따라 {ROOMS[dest][0]}로 이동했다.')
    p['mental']=clamp(p['mental']-2);p['fatigue']=clamp(p['fatigue']+max(2,8-STATS[p['char']][0]));g.emit(f'{p["name"]} → {ROOMS[dest][0]}. {ROOMS[dest][1]}')
    if random.random()<ROOMS[dest][2]:spawn(g,dest,p)
    elif random.random()<.48:ambient(g,p)
   elif cmd=='search':
    if p['mental']<=0:g.emit(f'{p["name"]}은(는) 정신력이 부족해 조사에 집중하지 못한다.');continue
    r=p['room'];p['mental']=clamp(p['mental']-4);p['fatigue']=clamp(p['fatigue']+max(2,11-STATS[p['char']][0]));chance=min(.9,.36+STATS[p['char']][3]*.1)
    if g.supplies[r]>0 and len(p['inventory'])<20 and random.random()<chance:
     item=random.choice(LOOT[r]);g.supplies[r]-=1;p['inventory'].append(item);g.emit(f'{p["name"]}이(가) {ROOMS[r][0]}에서 [{item}] 발견! (남은 물자 {g.supplies[r]}/4)')
    else:g.emit(f'{p["name"]}이(가) 주변을 조사했지만 '+('가방이 가득 차 물건을 챙길 수 없었다.' if len(p['inventory'])>=20 else '더 이상 찾을 물자가 없었다.' if g.supplies[r]<=0 else '아무것도 찾지 못했다.'))
    if random.random()<.12:
     g.emit(f'💥 {p["name"]}이(가) 물품을 무너뜨렸다! 큰 소음이 울려 퍼진다.')
     spawn(g,r,p,force=True)
    elif random.random()<ROOMS[r][2]*1.4:spawn(g,r,p)
    elif random.random()<.48:ambient(g,p)
   elif cmd=='talk':
    other=next((q for q in g.players.values() if q['char']==m.get('target') and q is not p and q['room']==p['room']),None)
    if other:
     p['mental']=clamp(p['mental']+12+STATS[p['char']][4]*2);other['mental']=clamp(other['mental']+5);p['bonds'][str(other['char'])]=min(100,p['bonds'][str(other['char'])]+2)
     g.emit(f'{p["name"]}이(가) {other["name"]}에게 말을 걸었다. 두 사람은 잠시 이야기를 나누며 마음을 추슬렀다.')
   elif cmd=='gift':
    other=next((q for q in g.players.values() if q['char']==m.get('target') and q is not p and q['room']==p['room']),None)
    item=m.get('item')
    if other and item in p['inventory'] and len(other['inventory'])<20:
     p['inventory'].remove(item);other['inventory'].append(item);delta=GIFTS.get(item,[0]*5)[other['char']];other['bonds'][str(p['char'])]=clamp(other['bonds'][str(p['char'])]+delta*8);p['bonds'][str(other['char'])]=clamp(p['bonds'][str(other['char'])]+delta*8)
     g.emit(f'{p["name"]} → {other["name"]}: [{item}] 선물. 유대도 {delta:+d}단계.');await g.notify(other,'gift',f'{p["name"]}에게 [{item}] 선물을 받았습니다. 유대도 {delta:+d}단계.',p['char'])
   elif cmd=='use':
    item=m.get('item')
    if item in p['inventory'] and item in RECOVER:
     if now<p.get('heal_cooldown',0):
      await ws.send_json({'type':'error','message':f'회복 아이템 쿨타임: {int(p["heal_cooldown"]-now+59)//60}분 남음'});continue
     hp,mental,fatigue,inf=RECOVER[item];p['inventory'].remove(item);p['heal_cooldown']=now+300
     p['hunger']=clamp(p.get('hunger',0)-FOOD.get(item,(0,0))[0])
     p['hp']=clamp(p['hp']+hp);p['mental']=clamp(p['mental']+mental);p['fatigue']=clamp(p['fatigue']+fatigue);p['infection']=clamp(p['infection']+inf)
     g.emit(f'{p["name"]}이(가) [{item}] 사용. {ITEMS[item][1]}')
   elif cmd=='equip':
    item=m.get('item');kind=ITEMS.get(item,('',''))[0]
    if item in p['inventory'] and kind in ('weapon','armor'):
     old=p['equipment'].get(kind);p['inventory'].remove(item)
     if old:p['inventory'].append(old)
     p['equipment'][kind]=item;g.emit(f'{p["name"]}이(가) [{item}] 장착.')
   elif cmd=='unequip':
    kind=m.get('slot')
    if kind in ('weapon','armor') and p['equipment'].get(kind) and len(p['inventory'])<20:
     item=p['equipment'][kind];p['inventory'].append(item);p['equipment'][kind]=None;g.emit(f'{p["name"]}이(가) [{item}] 장착 해제.')
   elif cmd=='raid_start':
    if not g.raid and p['room']=='gym':
     g.raid={'room':'gym','name':'돌연변이 감염자 · 체육관의 포식자','hp':420,'max_hp':420,'participants':[]};g.emit('⚠ RAID 발생! 체육관에서 거대한 돌연변이 감염자가 깨어났다. 여러 생존자가 협력해야 한다.')
   elif cmd=='raid_attack':
    if g.raid and p['room']==g.raid['room'] and (p['char'] in g.combat_joined.get(p['room'],set()) or not any(q['room']==p['room'] and q is not p for q in g.players.values())):
     dmg=random.randint(5,12)+STATS[p['char']][1]*4+(8 if p['equipment']['weapon']=='야구 방망이' else 11 if p['equipment']['weapon']=='철제 파이프' else 17 if p['equipment']['weapon']=='소방 도끼' else 0)
     g.raid['hp']-=dmg;g.raid['participants']=list(set(g.raid['participants']+[p['char']]))
     g.emit(f'⚔ {p["name"]}의 레이드 공격! 돌연변이에게 {dmg} 피해. HP {max(0,g.raid["hp"])}/{g.raid["max_hp"]}')
     if g.raid['hp']<=0:
      g.emit('★ RAID CLEAR! 돌연변이가 쓰러졌다! 생존자들이 힘을 합쳐 승리했다.')
      # 실제 전투에 참가한 생존자에게 각각 1개씩, 마지막 공격자에게 추가 보상 1개.
      for fighter in list(g.players.values()):
       if fighter['char'] in g.raid['participants'] and fighter['hp']>0:
        award_drop(g,fighter,weighted_drop(RAID_DROPS),'돌연변이 레이드 참가')
      award_drop(g,p,weighted_drop(RAID_DROPS),'레이드 마무리 일격')
      g.combat_joined.pop(p['room'],None);g.raid=None
     else:
      armor=5 if p['equipment']['armor']=='운동 보호대' else 11 if p['equipment']['armor']=='방검 조끼' else 0
      loss=max(1,random.randint(9,22)-armor);p['hp']=clamp(p['hp']-loss);g.emit(f'{p["name"]}이(가) 돌연변이의 반격으로 {loss} 피해.')
   elif cmd=='attack':
    if g.enemy and g.enemy['room']==p['room'] and (p['char'] in g.combat_joined.get(p['room'],set()) or not any(q['room']==p['room'] and q is not p for q in g.players.values())):
     dmg=random.randint(3,6)+STATS[p['char']][1]*4+(8 if p['equipment']['weapon']=='야구 방망이' else 11 if p['equipment']['weapon']=='철제 파이프' else 17 if p['equipment']['weapon']=='소방 도끼' else 0);g.enemy['hp']-=dmg;g.emit(f'{p["name"]}의 공격! 감염자에게 {dmg} 피해.')
     if g.enemy['hp']<=0:
      g.emit('감염자가 쓰러졌다. 전리품을 확인한다.')
      # 일반 좀비는 처치자에게 65% 확률로 1개 드롭. 조사 물자와 별개.
      if random.random()<.65:award_drop(g,p,weighted_drop(ZOMBIE_DROPS),'일반 감염자 처치')
      else:g.emit('감염자가 가진 물건은 쓸 수 없는 상태였다. (전리품 없음)')
      g.combat_joined.pop(p['room'],None);g.enemy=None
     elif random.random()>.15+STATS[p['char']][2]*.1:
      loss=max(1,random.randint(5,15)-(5 if p['equipment']['armor']=='운동 보호대' else 11 if p['equipment']['armor']=='방검 조끼' else 0));p['hp']=clamp(p['hp']-loss);g.emit(f'{p["name"]}이(가) 반격으로 {loss} 피해를 입었다.')
      if random.random()<.17:
       p['infection']=clamp(p['infection']+random.randint(7,22));part=random.choice(['왼팔','오른팔','왼다리','오른다리']);p['infected_parts']=list(set(p.get('infected_parts',[])+[part]));g.emit(f'{p["name"]}의 {part}에 감염 징후가 나타났다!')
   elif cmd=='flee':
    if (g.enemy and g.enemy['room']==p['room']) or (g.raid and g.raid['room']==p['room']):
     if random.random()<min(.9,.22+STATS[p['char']][2]*.12):p['room']='music';g.emit(f'{p["name"]}이(가) 밴드부실로 도주했다!')
     else:p['hp']=clamp(p['hp']-8);g.emit(f'{p["name"]}의 도주 실패. 체력 -8.')
   elif cmd=='rest':p['fatigue']=clamp(p['fatigue']-15);p['hp']=clamp(p['hp']+5);g.emit(f'{p["name"]}이(가) 잠시 휴식했다.')
   if p['hp']<=0:
    p['hp']=0;p['inventory']=[];p['equipment']={'weapon':None,'armor':None};p['deaths']+=1
    g.emit(f'☠ {p["name"]} 사망. 소지품과 장비가 모두 소멸했다. [다시 시작]으로 부활할 수 있다.')
   if p['fatigue']>=100 and not p.get('unconscious_until',0):
    p['unconscious_until']=time.time()+600
    g.emit(f'⚠ {p["name"]}이(가) 피로 누적으로 기절했다! 10분 동안 행동 불능.')
   elif 90<=p['fatigue']<100:
    await ws.send_json({'type':'warning','message':f'⚠ 기절 위험! 피로 {p["fatigue"]}%. 100%가 되면 10분간 행동할 수 없습니다.'})
   await g.broadcast()
 finally:
  if g and token in g.players:
   p=g.players.pop(token);g.sockets.pop(token,None);g.emit(f'{p["name"]} 연결 종료.');await g.broadcast()
   if not g.players:rooms.pop(g.code,None)
 return ws

def spawn(g,r,p,force=False):
 if g.enemy:return
 g.enemy={'room':r,'hp':random.randint(30,55),'max_hp':55};g.emit(f'⚠ {ROOMS[r][0]}에서 감염자가 나타났다! 함께 싸우거나 도망쳐라.')
def ambient(g,p):
 pool=[q for q in g.players.values() if q is not p and q['room']==p['room']]
 if pool:
  q=random.choice(pool);g.emit(q["name"]+": “"+LINES.get(p["room"],LINES["hall"])[q["char"]]+"”")

async def recovery_loop(app):
 while True:
  await asyncio.sleep(2)
  now=time.time()
  for g in list(rooms.values()):
   changed=False
   if now-g.last_hunger>=180:
    g.last_hunger=now
    for q in g.players.values():
     if q['hp']>0:
      q['hunger']=clamp(q.get('hunger',0)+4)
      if q['hunger']>=90:q['mental']=clamp(q['mental']-4)
    changed=True
   if now-g.last_supply>=60:
    g.last_supply=now
    total=sum(g.supplies.values());capacity=len(g.supplies)*4
    if total/capacity<.30:
     for r in g.supplies:g.supplies[r]=4
     g.emit('📦 [교내 비상 물자 안내] 일부 구역에서 보급 물자가 다시 발견되었습니다.');changed=True
   if now-g.last_npc>=600 or not g.npc_encounters:
    g.last_npc=now;g.npc_encounters={}
    for r in random.sample(list(ROOMS),k=4):g.npc_encounters[r]=dict(random.choice(list(NPCS.values())))
    g.emit('📢 [교내 안내] 교내 곳곳에서 생존자의 구조 요청이 접수되었습니다.');changed=True
   if now-g.last_event>=600:
    g.last_event=now
    choices=['📢 [학생안전부] 3층 복도 출입을 자제해 주십시오. 유리 파편이 확인되었습니다.','📢 [방송부] 마이크 점검 중입니다. 원인을 알 수 없는 소음에 주의해 주십시오.','📢 [긴급 안내] 정문에 다수의 감염자가 집결했습니다. 이동을 삼가 주십시오.','📢 [시설관리실] 창고 방화문이 자동 폐쇄되었습니다.','📢 [보건실] 응급 처치가 필요한 학생은 가까운 생존자에게 도움을 요청하십시오.','📢 [외부 구조 방송] 군 구조대가 운동장 인근에 진입했습니다. 안전을 확인하고 접근하십시오.','📢 [긴급 대피 방송] 교내 일부 구역에서 감염자 집단이 확인되었습니다.']
    if random.random()<.4 and g.players:
     target=random.choice(list(g.players.values()))
     g.emit(f'🚨 [긴급 교내 방송] {ROOMS[target["room"]][0]}에 감염자 떼가 접근 중입니다!')
     spawn(g,target['room'],target,force=True)
    elif random.random()<.35:g.emit('🪖 [외부 무전] 구조대원이 교내에 진입했습니다. 학생들은 위치를 알리고 대기하십시오.')
    notice={'time':time.strftime('%H:%M:%S'),'text':random.choice(choices)};g.notices.append(notice);g.notices=g.notices[-20:];g.emit(notice['text']);changed=True

   for p in g.players.values():
    if p.get('unconscious_until',0) and now>=p['unconscious_until']:
     p['unconscious_until']=0;p['fatigue']=60;g.emit(f'{p["name"]}이(가) 의식을 되찾았다.');changed=True
   if changed:await g.broadcast()
async def recovery_context(app):
 task=asyncio.create_task(recovery_loop(app))
 yield
 task.cancel()
 try:await task
 except asyncio.CancelledError:pass
async def health(req):return web.json_response({'status':'ok','active_rooms':len(rooms)})
app=web.Application();app.cleanup_ctx.append(recovery_context);app.router.add_get('/',index);app.router.add_get('/assets/portrait_{id}.png',portrait);app.router.add_get('/ws',socket);app.router.add_get('/health',health)
if __name__=='__main__':web.run_app(app,host='0.0.0.0',port=int(os.environ.get('PORT','8765')))
