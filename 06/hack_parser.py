class Parser:
    ##初期化..改行, コメントを消す
    def __init__(self, filepath):
        self.commands=[]
        with open(filepath, 'r') as f:
            for line in f:
                #'//'以降の文字は見ない
                clean_line=line.split('//')[0]
                #空白, 改行を削除
                clean_line = "".join(clean_line.split())
                #文字が残ってたらリストに追加
                if clean_line:
                    self.commands.append(clean_line)
        self.current_index=-1
        self.current_command=""

    #コマンドがまだあるか
    def has_more_commands(self):
        return self.current_index+1 < len(self.commands)

    #次のコマンドを読み込む
    def advance(self):
        self.current_index +=1
        self.current_command = self.commands[self.current_index]

    #現在のコマンドの種類を返す
    def command_type(self):
        if self.current_command.startswith('@'):
            return 'A'
        elif self.current_command.startswith('('):
            return 'L'
        else:
            return 'C'

    #A命令のとき@以降の部分を返す
    #L命令だと, シンボルを抽出
    def symbol(self):
        if self.command_type()=='A':
            return self.current_command[1:] #@以降の文字
        elif self.command_type()=='L':
            return self.current_command[1:-1] #()の中身
    
    #C命令だと, 3個抽出
    def dest(self):
        if '=' in self.current_command:
            return self.current_command.split('=')[0]
        return "null"
    
    def comp(self):
        temp=self.current_command
        #'='の左
        if '=' in temp:
            temp=temp.split('=')[1]
        #';'の右
        if ';' in temp:
            temp=temp.split(';')[0]
        
        return temp
    
    def jump(self):
        #';'の右側
        if ';' in self.current_command:
            return self.current_command.split(';')[1]
        return "null"
