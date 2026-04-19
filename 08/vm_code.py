class CodeWriter:
    def __init__(self, output_file):
        self.file=open(output_file, 'w')
        self.label_count=0
        self.call_count=0
    
    def setFileName(self, fileName):
        self.current_file=fileName

    #算術素子の書き込み
    def writeArithmetic(self, command):
        #デバッグ用
        self.file.write(f"//{command}\n")

        if command=='add':
            asm=(
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "M=D+M\n"
            )
            self.file.write(asm)
        
        elif command=='sub':
            asm=(
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "M=M-D\n"
            )
            self.file.write(asm)
        elif command=='neg':
            asm=(
                "@SP\n"
                "A=M-1\n"
                "M=-M\n"
            )
            self.file.write(asm)
        
        elif command in ['eq', 'gt', 'lt']:
            #D=x-y
            asm=(
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "D=D-M\n"
            )
            l_num=self.label_count
            self.label_count+=1
            #ジャンプ先ラベル
            asm+= f"@TRUE_{l_num}\n"
            if command=='eq':
                asm+="D;JEQ\n"
            elif command=='gt':
                asm+="D;JGT\n"
            elif command=='lt':
                asm+="D;JLT\n"

            #条件を満たさない
            asm+=(
                "@SP\n"
                "A=M-1\n"
                "M=0\n"
                f"@END_{l_num}\n"
                "0;JMP\n"
            )
            #条件を満たす
            asm+=(
                f"(TRUE_{l_num})\n"
                "@SP\n"
                "A=M-1\n"
                "M=-1\n"
            )
            asm+=f"(END_{l_num})\n"
            self.file.write(asm)
        
        elif command in ['and', 'or']:
            asm=(
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
            )
            if command=='and':
                asm+="M=D&M\n"
            elif command=='or':
                asm+="M=D|M\n"
            self.file.write(asm)
        
        elif command=='not':
            asm=(
                "@SP\n"
                "A=M-1\n"
                "M=!M\n"
            )
            self.file.write(asm)
        
    #push, popに対応するアセンブリ
    def writePushPop(self, command, segment, index):
        #デバッグ用
        self.file.write(f"//{command}{segment}{index}\n")
        
        if command=='C_PUSH':
            #定数
            if segment == 'constant':
                asm=(
                    f"@{index}\n"
                    "D=A\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
                self.file.write(asm)
            elif segment in ['local', 'argument', 'this', 'that']:
                asm=(
                    f"@{index}\n"
                    "D=A\n"
                )
                if segment=='local':
                    asm+=("@LCL\n")
                elif segment=='argument':
                    asm+=("@ARG\n")
                elif segment=='this':
                    asm+=("@THIS\n")
                elif segment=='that':
                    asm+=("@THAT\n")
                asm+=(
                    "A=M\n"
                    "D=D+A\n"
                    "A=D\n"
                    "D=M\n"
                    #RAM[sp]<-D
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    #SP++
                    "@SP\n"
                    "M=M+1\n"
                )
                self.file.write(asm)
            
            elif segment in ['temp', 'pointer']:
                #アドレスを計算
                address=int(index)
                if segment=='temp': address+=5
                else: address+=3
                asm=(
                    f"@{address}\n"
                    "D=M\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    #SP++
                    "@SP\n"
                    "M=M+1\n"
                )
                self.file.write(asm)
            elif segment == 'static':
                #ファイル名.{index}というシンボル
                symbol=f"{self.current_file}.{index}"
                asm=(
                    f"@{symbol}\n"
                    "D=M\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    #SP++
                    "@SP\n"
                    "M=M+1\n"
                )
                self.file.write(asm)
                    

        elif command=='C_POP':
            if segment in ['local', 'argument', 'this', 'that']:
                #保存先アドレスをRAM[13]へ
                asm=(
                    f"@{index}\n"
                    "D=A\n"
                )
                if segment=='local':
                    asm+=("@LCL\n")
                elif segment=='argument':
                    asm+=("@ARG\n")
                elif segment=='this':
                    asm+=("@THIS\n")
                elif segment=='that':
                    asm+=("@THAT\n")
                asm+=(
                    #R13に保存先アドレスが
                    f"D=D+M\n"
                    "@R13\n"
                    "M=D\n"
                    #スタックから値を取り出す
                    "@SP\n"
                    "AM=M-1\n"
                    "D=M\n"
                    #アドレスにその値を格納
                    "@R13\n"
                    "A=M\n"
                    "M=D\n"
                )
                self.file.write(asm)
            elif segment in ['temp','pointer']:
                address=int(index)
                if segment=='temp': address+=5
                else: address+=3
                asm=(
                    "@SP\n"
                    "AM=M-1\n"
                    "D=M\n"
                    f"@{address}\n"
                    "M=D\n"
                )
                self.file.write(asm)
            elif segment == 'static':
                #ファイル名.{index}というシンボル
                symbol=f"{self.current_file}.{index}"
                asm=(
                    "@SP\n"
                    "AM=M-1\n"
                    "D=M\n"
                    f"@{symbol}\n"
                    "M=D\n"
                )
                self.file.write(asm)

    #分岐コマンド(追加)
    def writeLabel(self, label):
        self.file.write(f"// {label}\n")
        asm= f"({label})\n"
        self.file.write(asm)

    def writeGoto(self, label):
        asm=(
            f"@{label}\n"
            "0;JMP\n"
        )
        self.file.write(asm)
    
    def writeIf(self,label):
        asm=(
            "@SP\n"
            "AM=M-1\n"
            "D=M\n"
            f"@{label}\n"
            "D;JNE\n"
        )
        self.file.write(asm)
    
    #関数コマンド
    def writeFunction(self, functionName, nVars):
        self.file.write(f"// {functionName}\n")
        asm=f"({functionName})\n"
        #変数分0をpush
        for _ in range(int(nVars)):
            asm+=(
                f"@0\n"
                "D=A\n"
                "@SP\n"
                "A=M\n"
                "M=D\n"
                "@SP\n"
                "M=M+1\n"
            )
        self.file.write(asm)
    
    def writeCall(self, functionName, nArgs):
        #ラベル作成
        label=f"{functionName}$ret.{self.call_count}"
        self.call_count+=1
        #returnアドレスpush
        asm=(
            f"@{label}\n"
            "D=A\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
        )
        #ベースアドレスpush
        for base in ['LCL', 'ARG', 'THIS', 'THAT']:
            asm+=(
                f"@{base}\n"
                "D=M\n"
                "@SP\n"
                "A=M\n"
                "M=D\n"
                "@SP\n"
                "M=M+1\n"
            )

        #LCL=SP
        asm+=(
            "@SP\n"
            "D=M\n"
            "@LCL\n"
            "M=D\n"
        )
        #ARG=SP-5-nArgs
        d=5+int(nArgs)
        asm+=(
            f"@{d}\n"
            "D=A\n"
            "@SP\n"
            "D=M-D\n"
            "@ARG\n"
            "M=D\n"
        )
        #jump
        asm+=(
            f"@{functionName}\n"
            "0;JMP\n"
        )
        self.file.write(asm)

    def writeReturn(self):
        #親のフレームの番地の終わり..frame<-LCL
        #戻り値...retAddr<-*(frame-5)
        asm=(
            #frame=LCL
            "@LCL\n"
            "D=M\n"
            "@frame\n"
            "M=D\n"
            #retAddr=*(frame-5)
            "@5\n"
            "A=D-A\n"
            "D=M\n"
            "@retAddr\n"
            "M=D\n"
        )
        #親領域の次の場所に計算結果をpushする
        #*ARG<-pop()
        asm+=(
            "@SP\n"
            "AM=M-1\n"
            "D=M\n"
            "@ARG\n"
            "A=M\n"
            "M=D\n"
        )
        #SPを下げて, フレームを開放
        #SP<-ARG+1
        asm+=(
            "@ARG\n"
            "D=M+1\n"
            "@SP\n"
            "M=D\n"
        )
        #ベースアドレス復元
        for base in ['THAT', 'THIS', 'ARG', 'LCL']:
            asm+=(
            "@frame\n"
            "AM=M-1\n"
            "D=M\n"
            f"@{base}\n"
            "M=D\n"
        )
        #ジャンプ
        #goto retAddr
        asm+=(
            "@retAddr\n"
            "A=M\n"
            "0;JMP\n"
        )

        self.file.write(asm)
    #ブーストラップ
    def writeInit(self):
        asm=(
            #SP=256
            "@256\n"
            "D=A\n"
            "@SP\n"
            "M=D\n"
        )
        self.file.write(asm)
        #call Sys.init 0
        self.writeCall("Sys.init",0)

    def close(self):
        self.file.close()



    
    
            

    
