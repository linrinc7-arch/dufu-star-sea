# -*- coding: utf-8 -*-
"""03_export_web.py — 导出前端数据"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(BASE, 'data', 'build')
W = os.path.join(BASE, 'web')

sf = json.load(open(os.path.join(B, 'starfield.json'), encoding='utf-8'))
per = json.load(open(os.path.join(B, 'periods.json'), encoding='utf-8')) if os.path.exists(os.path.join(B,'periods.json')) else {'periods': [-1]*len(sf['poems'])}
PDP = per['periods']
poems = json.load(open(os.path.join(B, 'dufu_poems.json'), encoding='utf-8'))
feat = json.load(open(os.path.join(B, 'features.json'), encoding='utf-8'))

CAT_ORDER = ['天象时序','地理空间','植物','动物','器物','身体生命','情感心理','社会战争','人伦交往','宗教哲理']
CAT_LABEL = {
 '天象时序':'日月','地理空间':'江山','植物':'草木','动物':'鸟兽','器物':'器物',
 '身体生命':'病老','情感心理':'愁思','社会战争':'兵戈','人伦交往':'亲友','宗教哲理':'释道'}
CAT_COLOR = {
 '天象时序':'#8fb8de','地理空间':'#6fa8a0','植物':'#8fbf7f','动物':'#d4a373','器物':'#c9b458',
 '身体生命':'#d98a8a','情感心理':'#b08fc7','社会战争':'#d1603d','人伦交往':'#e0c9d8','宗教哲理':'#7f8fa6'}

HOT = {'登高','春望','北征','秋兴八首 一','茅屋为秋风所破歌','石壕吏','新安吏','潼关吏',
       '新婚别','垂老别','无家别','望岳','月夜','春夜喜雨','旅夜书怀','阁夜','咏怀古迹五首 三',
       '兵车行','丽人行','自京赴奉先县咏怀五百字','闻官军收河南河北','登岳阳楼','蜀相','客至',
       '江南逢李龟年','绝句','江畔独步寻花七绝句 六','赠李白','梦李白二首 一','天末忆李白','春日忆李白',
       '哀江头','悲陈陶','同诸公登慈恩寺塔','房兵曹胡马诗','前出塞九首 六'}
found = {p['title'] for p in poems}
missing = [h for h in HOT if h not in found]


# 名篇的一句话注（"为什么被记住"）
NOTE = {
 '登高':'明人胡应麟推为“古今七律第一”。八句皆对，却无板滞之气。',
 '春望':'五律写国破，四十字里没有一个废字。“烽火连三月，家书抵万金”后来成了战乱家书的代称。',
 '北征':'七百字的长篇纪行，把家国之痛写成了路上的具体见闻。',
 '石壕吏':'“三吏三别”之首。全篇不着一句议论，只让老妇自己说。',
 '新安吏':'“三吏”之一。写征兵，写母子，写到后来连安慰都显得无力。',
 '潼关吏':'“三吏”之一。借守关士卒之口说筑城，实则是杜甫对防务的忧虑。',
 '新婚别':'“三别”之一。新婚次日即别，全篇是新妇自述。',
 '垂老别':'“三别”之一。老者被征，老妻相送，“孰知是死别”。',
 '无家别':'“三别”之一。战败归乡，家已无人，最后连“家”也无得可别。',
 '茅屋为秋风所破歌':'由一己之屋推及“天下寒士”，是杜甫式推己及人的典型。',
 '望岳':'二十四岁所作。“会当凌绝顶，一览众山小”——他一生的志气都在这十字里。',
 '月夜':'不写自己在长安望月，而写妻子在鄜州望月，从对面写来。',
 '春夜喜雨':'“随风潜入夜，润物细无声”，写雨，也写一种不声张的德性。',
 '旅夜书怀':'“星垂平野阔，月涌大江流”，以壮阔之景衬孤舟之身。',
 '阁夜':'“五更鼓角声悲壮，三峡星河影动摇”，声与影同时入诗。',
 '咏怀古迹五首 三':'咏昭君。“千载琵琶作胡语，分明怨恨曲中论”，借古人说自己。',
 '兵车行':'以问答体写征兵。“信知生男恶，反是生女好”是极沉痛的反语。',
 '丽人行':'写曲江春游的杨氏姐妹。末句“炙手可热势绝伦”，讽刺不着一字。',
 '自京赴奉先县咏怀五百字':'“朱门酒肉臭，路有冻死骨”出于此篇，写于安史之乱爆发前夕。',
 '闻官军收河南河北':'被称为杜甫“生平第一快诗”，八句一气奔注。',
 '登岳阳楼':'“吴楚东南坼，乾坤日夜浮”，晚年登楼，气象仍阔大。',
 '蜀相':'“出师未捷身先死，长使英雄泪满襟”，为诸葛亮，也为自己。',
 '客至':'“花径不曾缘客扫，蓬门今始为君开”，难得的家常暖意。',
 '江南逢李龟年':'二十八字写尽四十年盛衰，“落花时节又逢君”。',
 '绝句四首 三':'“窗含西岭千秋雪，门泊东吴万里船”，小小一窗含着万里。',
 '江畔独步寻花七绝句 六':'“黄四娘家花满蹊”，杜甫少见的明丽。',
 '赠李白':'现存杜甫赠李白诗十余首，此为最早的一批。',
 '梦李白二首 一':'“死别已吞声，生别常恻恻”，写梦，写疑，写不敢信。',
 '天末忆李白':'“文章憎命达，魑魅喜人过”，为李白鸣不平。',
 '春日忆李白':'“白也诗无敌，飘然思不群”，是杜甫对李白最直白的推崇。',
 '哀江头':'写曲江在被陷长安时的荒凉，“人生有情泪沾臆”。',
 '悲陈陶':'写陈陶斜之败。“孟冬十郡良家子，血作陈陶泽中水”。',
 '同诸公登慈恩寺塔':'与高适、岑参、薛据同登大雁塔，各赋一首，历来推杜作最高。',
 '房兵曹胡马诗':'写马“所向无空阔，真堪托死生”，是早年豪气。',
 '前出塞九首 六':'“射人先射马，擒贼先擒王”，被后世反复引用。',
 '饮中八仙歌':'八人各一段，李白“天子呼来不上船”最著名。',
 '秋兴八首 一':'“丛菊两开他日泪，孤舟一系故园心”，夔州秋日，八年漂泊收于一句。',
}

NOTE_SEEN = {}
NOTE_COUNT = {}
for _p in sf['poems']:
    NOTE_COUNT[_p['title']] = NOTE_COUNT.get(_p['title'], 0) + 1

out = {'poems': [], 'cats': [], 'clusters': []}
for p in sf['poems']:
    i = p['id']
    src = poems[i]
    words = list(feat['counts'][i].keys())
    out['poems'].append({
        'i': i, 't': p['title'], 'f': p['form'], 'n': p['n'],
        'x': p['x'], 'y': p['y'], 'z': p['z'], 'c': p['c'],
        'd': p['dom'], 'l': p['dom_lift'], 'k': p['top'][:4],
        'w': words,
        'wc': {k: v for k, v in list(feat['counts'][i].items())[:24]},
        'L': src['lines'],
        'hot': 1 if p['title'] in HOT else 0,
        'note': (NOTE.get(p['title'], '')
                 if (NOTE_COUNT.get(p['title'], 0) == 1
                     or (p['title'] in HOT and not NOTE_SEEN.setdefault(p['title'], p['id']) != p['id']))
                 else ''),
        'pd': (src.get('pd') if src.get('pd') is not None else PDP[i]),
    })
for c in CAT_ORDER:
    out['cats'].append({'id': c, 'label': CAT_LABEL[c], 'color': CAT_COLOR[c],
                        'n': sum(1 for p in out['poems'] if p['d'] == c)})
for c in sf['clusters']:
    out['clusters'].append({'id': c['id'], 'label': c['label'], 'size': c['size']})

def _load(name):
    p = os.path.join(B, name)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None

out['meta'] = {'life': _load('shengping.json'), 'friends': _load('jiaoyou.json'), 'critics': _load('pingjia.json')}

# 诗题 → 配图 slug（有图的才给）
ART = {
 '登高':'denggao','春望':'chunwang','北征':'beizheng','石壕吏':'shihaoli',
 '茅屋为秋风所破歌':'maowu','望岳':'wangyue','月夜':'yueye','春夜喜雨':'chunyexiyu',
 '旅夜书怀':'lvyeshuhuai','阁夜':'geye','兵车行':'bingchexing',
 '咏怀古迹五首 三':'yonghuaiguji','丽人行':'lirenxing','闻官军收河南河北':'wenguanjun',
 '登岳阳楼':'dengyueyanglou','蜀相':'shuxiang','客至':'kezhi','江南逢李龟年':'jiangnan',
 '绝句四首 三':'jueju','赠李白':'zenglibai','房兵曹胡马诗':'huma','梦李白二首 一':'menglibai',
 '哀江头':'aijiangtou','悲陈陶':'beichentao','同诸公登慈恩寺塔':'ciensi',
 '新婚别':'xinhunbie','垂老别':'chuilaobie','无家别':'wujiabie',
 '新安吏':'xinanli','潼关吏':'tongguanli',
}
out['art'] = ART

os.makedirs(W, exist_ok=True)
js = 'window.DUFU=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';'
open(os.path.join(W, 'data.js'), 'w', encoding='utf-8').write(js)
print('poems', len(out['poems']), 'size', len(js.encode('utf-8')), 'hot', sum(p['hot'] for p in out['poems']), 'missing', missing)
