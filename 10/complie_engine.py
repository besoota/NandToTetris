from jack_tokenizer import JackTokenizer

class CompilationEngine:
    def __init__(self, tokenizer, output_file):
        self.tokenizer=tokenizer
        self.file=open(output_file, 'w', encoding='utf-8')
        self.indent_level=0
        #起動時, 1単語目を読み込んでおく
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
    
    def close(self):
        self.file.close()

    #indentは空白文字
    def write_xml(self, tag, value):
        indent=" "*self.indent_level
        #特殊文字に置き換え
        if value=='<': value='&lt;'
        elif value=='>': value='&gt;'
        elif value=='&': value='&amp;'

        self.file.write(f"{indent}<{tag}> {value} </{tag}>\n")

    #今のトークンが正しいか確認し, <タイプ>~<タイプ>を書き込む
    def process(self, expected_value=None, expected_type=None):
        #今のトークンを処理して, xmlに出力し, tokenizerを次へ進める
        current_type = self.tokenizer.tokenType()
        current_value=""

        if current_type=='KEYWORD': current_value=self.tokenizer.keyWord()
        elif current_type == 'SYMBOL': current_value = self.tokenizer.symbol()
        elif current_type == 'IDENTIFIER': current_value = self.tokenizer.identifier()
        elif current_type == 'INT_CONST': current_value = str(self.tokenizer.intVal())
        elif current_type == 'STRING_CONST': current_value = self.tokenizer.stringVal()

        #文法エラー
        if expected_value and current_value!=expected_value:
            raise SyntaxError(f"文法エラー{current_value}->{expected_value}")
        
        #タグ名に変換
        tag_name=self._get_tag_name(current_type)
        
        #書き込み
        self.write_xml(tag_name, current_value)

        #次のトークンへ進む
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()

    def _get_tag_name(self, token_type):
        #タイプ名をタグ名に変換
        if token_type == 'KEYWORD': return 'keyword'
        elif token_type == 'SYMBOL': return 'symbol'
        elif token_type == 'IDENTIFIER': return 'identifier'
        elif token_type == 'INT_CONST': return 'integerConstant'
        elif token_type == 'STRING_CONST': return 'stringConstant'

    def compileClass(self):
        """
        class:
        'class' className '{' classVarDec* subroutineDec* '}'
        """
        #<class>を最初に書く
        self.file.write("<class>\n")
        self.indent_level+=1

        #はじめはclassがくる
        self.process("class")

        #次はクラス名（INDETIFIER）がくる
        self.process(expected_type="IDENTIFIER")
        #<identifier> 名前 </identifier>
        
        #次に{に進む
        self.process("{")
        
        #次に0回以上のclassVarDecがくる
        #次のトークンは"int ~~"の形
        #条件が合えばループしていく
        while self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyWord() in ['static', 'field']:
            self.compileClassVarDec()
        #0回以上のサブルーチン
        while self.tokenizer.tokenType()=='KEYWORD' and self.tokenizer.keyWord() in ['constructor', 'function', 'method']:
            self.compileSubroutine()
        
        self.process("}")

        #"classは終わり"
        #スペース文字カウントを元に戻す
        self.indent_level-=1
        self.file.write("</class>\n")


    def compileClassVarDec(self):
        """
        classVarDec:
        ('static' | 'field') type varName (',' varName)* ';'
        """
        #インデントは継続して空ける
        indent = " " * self.indent_level
        #<classVarDec>
        self.file.write(f"{indent}<classVarDec>\n")
        self.indent_level +=1

        #('static' | 'field')の処理
        self.process()

        #typeの処理
        #型名は構造体もあるため, expectedは指定しない
        self.process()
        
        #varName
        self.process(expected_type="IDENTIFIER")

        #(',' varName)*
        while self.tokenizer.tokenType()=='SYMBOL' and self.tokenizer.symbol()==',':
            self.process(",")
            self.process(expected_type="IDENTIFIER")
        
        # ;
        self.process(";")

        #</classVarDec>を閉じる
        self.indent_level -= 1
        self.file.write(f"{indent}</classVarDec>\n")


    def compileSubroutine(self):
        """
        subroutine:
        ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        """
        #インデントは継続して空ける
        indent = " " * self.indent_level
        #<subroutineDec>
        self.file.write(f"{indent}<subroutineDec>\n")
        self.indent_level +=1

        #('constructor' | 'function' | 'method')
        self.process()

        #('void' | type)
        self.process()

        #subroutineName
        self.process(expected_type="IDENTIFIER")

        # '('
        self.process("(")
        
        # parameterList
        self.compileParameterList()

        #')'
        self.process(")")

        #subroutineBody
        self.compileSubroutineBody()

        #</subroutineDec>閉じる
        self.indent_level -= 1
        self.file.write(f"{indent}</subroutineDec>\n")


    def compileParameterList(self):
        """
        parameterlist:
        ( ( type varName ) ( ',' type varName )* )?
        """
        #インデントは継続して空ける
        indent = " " * self.indent_level
        #<parameterList>
        self.file.write(f"{indent}<parameterList>\n")
        self.indent_level +=1

        #  ')' でなければ処理を始める
        if not (self.tokenizer.tokenType()=='SYMBOL' and self.tokenizer.symbol()==')'):
            # type
            self.process()
            #varName
            self.process(expected_type="IDENTIFIER")

            #( ',' type varName )*
            while self.tokenizer.tokenType()=='SYMBOL' and self.tokenizer.symbol()==',':
                self.process(",")
                self.process()
                self.process(expected_type="IDENTIFIER")

        #</parameterList>閉じる
        self.indent_level -= 1
        self.file.write(f"{indent}</parameterList>\n")

    def compileSubroutineBody(self):
        """
        subroutineBody:
        '{' varDec* statements '}'
        """
        # <subroutineBody>
        indent = "  " * self.indent_level
        self.file.write(f"{indent}<subroutineBody>\n")
        self.indent_level += 1

        # '{'
        self.process("{")

        # varDec*
        while self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyWord()=='var':
            self.compileVarDec()
        
        #statements
        self.compileStatements()

        #'}'
        self.process("}")

        #</subroutineBody> 閉じる
        self.indent_level -= 1
        self.file.write(f"{indent}</subroutineBody>\n")

    def compileVarDec(self):
        """
        varDec:
        'var' type varName (',' varName)* ';'
        """
        #<varDec>
        indent = "  " * self.indent_level
        self.file.write(f"{indent}<varDec>\n")
        self.indent_level += 1

        #'var'
        self.process("var")

        #type varName
        self.process()
        self.process(expected_type="IDENTIFIER")

        #(',' varName)*
        while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ',':
            self.process(",")
            self.process(expected_type="IDENTIFIER")
        
        #';'
        self.process(";")

        #</varDec>
        self.indent_level -= 1
        self.file.write(f"{indent}</varDec>\n")

    def compileStatements(self):
        '''
        statements:
        statement*
        '''

        indent = "  " * self.indent_level
        self.file.write(f"{indent}<statements>\n")
        self.indent_level += 1
        '''
        statement:
        letStatement | ifStatement | whileStatement | doStatement | returnStatement
        '''
        while self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyWord() in ['let', 'if', 'while', 'do', 'return']:
            kw=self.tokenizer.keyWord()

            if kw == 'let':
                self.compileLet()
            elif kw == 'if':
                self.compileIf()
            elif kw == 'while':
                self.compileWhile()
            elif kw == 'do':
                self.compileDo()
            elif kw == 'return':
                self.compileReturn()
        
        self.indent_level -= 1
        self.file.write(f"{indent}</statements>\n")


    def compileLet(self):
        '''
        LetStatement:
        'let' varName ( '[' expression ']' )? '=' expression ';'
        '''
        indent = "  " * self.indent_level
        self.file.write(f"{indent}<letStatement>\n")
        self.indent_level += 1
        #'let'
        self.process("let")
        #varName
        self.process(expected_type="IDENTIFIER")
        #( '[' expression ']' )?
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == '[':
            self.process("[")
            self.compileExpression()
            self.process("]")
        
        #'='
        self.process("=")
        #expression
        self.compileExpression()
        #';'
        self.process(";")
        #</letStatement>
        self.indent_level -= 1
        self.file.write(f"{indent}</letStatement>\n")


    def compileIf(self):
        '''
        ifStatement:
        'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )?
        '''
        indent = "  " * self.indent_level
        self.file.write(f"{indent}<ifStatement>\n")
        self.indent_level += 1
        #'if'
        self.process("if")
        #'('
        self.process("(")
        #expression
        self.compileExpression()
        #')'
        self.process(")")
        #'{'
        self.process("{")
        #statements
        self.compileStatements()
        #'}'
        self.process("}")
        #( 'else' '{' statements '}' )?
        if self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyWord() == 'else':
            self.process("else")
            self.process("{")
            self.compileStatements()
            self.process("}")
        #</ifStatement>
        self.indent_level -= 1
        self.file.write(f"{indent}</ifStatement>\n")
    
    def compileWhile(self):
        '''
        whileStatement:
        'while' '(' expression ')' '{' statements '}'
        '''
        indent = "  " * self.indent_level
        self.file.write(f"{indent}<whileStatement>\n")
        self.indent_level += 1
        #'while'
        self.process("while")
        #'('
        self.process("(")
        #expression
        self.compileExpression()
        #')'
        self.process(")")
        #'{'
        self.process("{")
        #statements
        self.compileStatements()
        #'}'
        self.process("}")
        #</whileStatement>
        self.indent_level -= 1
        self.file.write(f"{indent}</whileStatement>\n")
    
    def compileDo(self):
        '''
        doStatement:
        'do' subroutineCall ';'
        '''
        '''
        subroutineCall:
        subroutineName '(' expressionList ')' | 
        (className | varName) '.' subroutineName '(' expressionList ')'
        '''
        indent = "  " * self.indent_level
        self.file.write(f"{indent}<doStatement>\n")
        self.indent_level += 1
        #'do'
        self.process("do")
        #subroutineCall
        self.process(expected_type="IDENTIFIER")
        current_symbol = self.tokenizer.symbol()

        if current_symbol == '.':
            #(className | varName) '.' subroutineName '(' expressionList ')'
            self.process(".")
            self.process(expected_type="IDENTIFIER") # subroutineName
            self.process("(")
            self.compileExpressionList()
            self.process(")")
        elif current_symbol == '(':
            #subroutineName '(' expressionList ')'
            self.process("(")
            self.compileExpressionList()
            self.process(")")
        else:
            raise SyntaxError(f"文法エラー: do文の関数呼び出しが不正です (現在のトークン: {self.tokenizer.current_token})")
        #';'
        self.process(";")
        #</doStatement>
        self.indent_level -= 1
        self.file.write(f"{indent}</doStatement>\n")
    
    def compileReturn(self):
        '''
        returnStatement:
        'return' expression? ';'
        '''
        indent = "  " * self.indent_level
        self.file.write(f"{indent}<returnStatement>\n")
        self.indent_level += 1
        #'return'
        self.process("return")
        #expression?
        if not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ';'):
            self.compileExpression()
        
        #';'
        self.process(";")
        #</returnStatement>
        self.indent_level -= 1
        self.file.write(f"{indent}</returnStatement>\n")
    
    def compileExpression(self):
        '''
        expression:
        term (op term)*
        '''
        indent = "  " * self.indent_level
        self.file.write(f"{indent}<expression>\n")
        self.indent_level += 1

        #term
        self.compileTerm()

        #(op term)*
        while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            op=self.tokenizer.symbol()
            self.process(op)
            self.compileTerm()
        
        #</expression>
        self.indent_level -= 1
        self.file.write(f"{indent}</expression>\n")
    
    def compileTerm(self):
        '''
        term:
        integerConstant | stringConstant | keywordConstant | 
        varName | varName '[' expression ']' | subroutineCall | 
        '(' expression ')' | unaryOp term
        '''
        '''
        subroutineCall:
        subroutineName '(' expressionList ')' | 
        (className | varName) '.' subroutineName '(' expressionList ')'
        '''
        indent = "  " * self.indent_level
        self.file.write(f"{indent}<term>\n")
        self.indent_level += 1

        token_type = self.tokenizer.tokenType()

        # integerConstant | stringConstant | keywordConstant
        if token_type in ['INT_CONST', 'STRING_CONST'] or \
           (token_type == 'KEYWORD' and self.tokenizer.keyWord() in ['true', 'false', 'null', 'this']):
            self.process()
        

        elif token_type == 'IDENTIFIER':
            # varName | varName '[' expression ']' | subroutineCall | 
            #'(' expression ')' | unaryOp term
            self.process(expected_type="IDENTIFIER")

            #次のトークンで分岐
            current_type = self.tokenizer.tokenType()
            current_symbol = self.tokenizer.symbol() if current_type == 'SYMBOL' else None

            if current_symbol == '[':
                # varName '[' expression ']' の処理
                self.process("[")
                self.compileExpression()
                self.process("]")

            elif current_symbol == '(':
                # サブルーチン呼び出しの1つ目
                # subroutineName '(' expressionList ')'
                self.process("(")
                self.compileExpressionList() 
                self.process(")")
            elif current_symbol == '.':
                #サブルーチン呼び出しの2つ目
                #className '.' subroutineName '(' expressionList ')'
                self.process(".")
                self.process(expected_type="IDENTIFIER") # subroutineName
                self.process("(")
                self.compileExpressionList()
                self.process(")")
            else:
                # varName
                # のこりで最初がIDENTIFIERなのはvarNameだけ
                pass
        elif token_type == 'SYMBOL' and self.tokenizer.symbol() == '(':
            # '(' expression ')'の処理
            self.process("(")
            self.compileExpression()
            self.process(")")
        elif token_type == 'SYMBOL' and self.tokenizer.symbol() in ['-', '~']:
            # unaryOp term
            self.process()
            self.compileTerm()
        else:
            raise SyntaxError(f"文法エラー: termが見つかりませんでした (現在のトークン: {self.tokenizer.current_token})")

        # </term>\n
        self.indent_level -= 1
        self.file.write(f"{indent}</term>\n")
    
    def compileExpressionList(self):
        '''
        expressionList:
        (expression (',' expression)* )?
        '''
        indent = "  " * self.indent_level
        self.file.write(f"{indent}<expressionList>\n")
        self.indent_level += 1

        # ')'でなければ処理を始める
        if not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ')'):
            # expression
            self.compileExpression()

            # (',' expression)*
            while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ',':
                self.process(",")
                self.compileExpression()
        
        # </expressionList>
        self.indent_level -= 1
        self.file.write(f"{indent}</expressionList>\n")


            
            

