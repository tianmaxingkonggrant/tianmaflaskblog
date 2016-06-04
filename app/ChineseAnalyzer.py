# coding=utf-8
from whoosh.analysis import Tokenizer, Token
from whoosh.fields import *
import pynlpir
from pynlpir import nlpir
class ChineseTokenizer(Tokenizer):
    def __call__(self, value, positions=False, chars=False,
                 keeporiginal=False, removestops=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        assert isinstance(value, text_type), "%r is not unicode" % value
        t = Token(positions, chars, removestops=removestops, mode=mode,
            **kwargs)
        nlpir.Init(nlpir.PACKAGE_DIR, nlpir.UTF8_CODE)
        pynlpir.open()
        pynlpir.open(encoding='utf-8')
        seglist = pynlpir.segment(value,)
        for w in seglist:
            t.original = t.text = w
            t.boost = 1.0
            if positions:
                t.pos=start_pos+value.find(w)
            if chars:
                t.startchar=start_char+value.find(w)
                t.endchar=start_char+value.find(w)+len(w)
            yield t      #通过生成器返回每个分词的结果token

def ChineseAnalyzer():
    return ChineseTokenizer()