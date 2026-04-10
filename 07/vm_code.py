class CodeWriter:
    def __init__(self, output_file):
        self.file=open(output_file, 'w')
        self.label_count=0
    
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
                    "A=M+D\n"
                    "D=M\n"
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
                    f"D=M+D\n"
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
    
    def close(self):
        self.file.close()



    
    
            

    
