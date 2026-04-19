class Parser:
    def __init__(self, filepath):
        self.commands=[]
        with open(filepath, 'r') as f:
            for line in f:
                #コメント
                clean_line=line.split('//')[0]
                #前後の空白
                clean_line=clean_line.strip()
                
                if clean_line:
                    self.commands.append(clean_line)
        self.current_index=-1
        self.current_command=""
        self.parts=[]
    
    def has_more_lines(self):
        return self.current_index+1<len(self.commands)
    
    def advance(self):
        self.current_index+=1
        self.current_command=self.commands[self.current_index]
        #空白でワードを分割して入れる
        self.parts=self.current_command.split()
    #種類分け
    def command_type(self):
        cmd=self.parts[0]
        if cmd=='push':
            return 'C_PUSH'
        elif cmd=='pop':
            return 'C_POP'
        elif cmd in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            return 'C_ARITHMETIC'
        ##7章, 分岐命令, 関数は考えない
        elif cmd == 'label': return 'C_LABEL'
        elif cmd == 'goto': return 'C_GOTO'
        elif cmd == 'if-goto': return 'C_IF'
        elif cmd == 'function': return 'C_FUNCTION'
        elif cmd == 'call': return 'C_CALL'
        elif cmd == 'return': return 'C_RETURN'
    #1つめの引数
    def arg1(self):
        if self.command_type()=='C_ARITHMETIC':
            #add, subを返す
            return self.parts[0]
        else:
            return self.parts[1]
    #2つめの引数
    def arg2(self):
        return int(self.parts[2])
    
        

