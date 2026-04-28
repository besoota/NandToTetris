import re
class JackTokenizer:
    def __init__(self, input_file):
        with open(input_file, 'r', encoding='utf-8')as f:
            code=f.read()
        
        #re.sub(パターン, 置き換える文字列, 元の文字列)
        #1行コメントを削除
        code= re.sub(r'//.*', '', code)
        #コメント削除
        code= re.sub(r'(?s)/\*.*?\*/', '', code)

        #(?P<タグ> パターン)
        pattern = re.compile(
            r'(?P<KEYWORD>\b(?:class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\b)|'
            r'(?P<SYMBOL>[{}()\[\].,;+\-*/&|<>=~])|'
            r'(?P<INT_CONST>\d+)|'
            r'(?P<STRING_CONST>"[^"\n]*")|'
            r'(?P<IDENTIFIER>[A-Za-z_][A-Za-z0-9]*)'
        )

        #リストに保存
        self.tokens=[]
        for match in pattern.finditer(code):
            #match...マッチしたものの各グループ
            #グループのタグ
            token_type = match.lastgroup
            #グループの要素
            token_value= match.group()
            self.tokens.append((token_type, token_value))
        self.index=0
        self.current_token=None

    #(タグ, 値)の形でリストにpushした
    def hasMoreTokens(self):
        return self.index < len(self.tokens)

    def advance(self):
        if self.hasMoreTokens():
            self.current_token= self.tokens[self.index]
            self.index+=1

    def tokenType(self):
        return self.current_token[0]

    def keyWord(self):
        #キーワードをそのまま返す
        return self.current_token[1]
    
    def symbol(self):
        #シンボルを返す
        return self.current_token[1]
    
    def identifier(self):
        #識別子
        return self.current_token[1]
    
    def intVal(self):
        #整数
        return int(self.current_token[1])
    
    def stringVal(self):
        #文字列定数(""は飛ばす)
        return self.current_token[1][1:-1]