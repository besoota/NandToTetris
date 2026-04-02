import sys
import os
from hack_parser import Parser
from hack_code import Code
from hack_symboltable import SymbolTable
def main():
    if len(sys.argv)!=2:
        print("使い方: python assembler.py <file.asm>")
        sys.exit(1)
    
    input_file = sys.argv[1]

    output_file = os.path.splitext(input_file)[0]+".hack"
    #インスタンス作成
    symboltable=SymbolTable()

    ####1回目の読み込み
    pre_parser=Parser(input_file)
    rom=0

    while pre_parser.has_more_commands():
        pre_parser.advance()
        #A,C命令のときは行を進める
        if pre_parser.command_type()=='A' or pre_parser.command_type()=='C':
            rom+=1
        #L命令のときそのときのアドレスを登録
        elif pre_parser.command_type()=='L':
            symbol=pre_parser.symbol()
            if not symboltable.contains(symbol):
                symboltable.add_entry(symbol,rom)

    ####2回目読み込み
    #インスタンス作成
    parser=Parser(input_file)
    code=Code()
    ram=16

    #出力ファイルに書き込んでいく
    #フィールドを1つずつ見ていく
    with open(output_file, 'w') as out_f:

        while parser.has_more_commands():
            parser.advance()

            #A命令
            if parser.command_type()=='A':
                symbol=parser.symbol()
                #@の後が数字
                if symbol.isdigit():
                    address=int(symbol)
                #シンボル
                else:
                    #新しい変数
                    if not symboltable.contains(symbol):
                        symboltable.add_entry(symbol,ram)
                        ram+=1
                    address=symboltable.get_address(symbol)

                #2進数に直す
                #先頭2文字は使わない, 0埋め
                binary_val= bin(int(address))[2:].zfill(15)
                machine_code="0"+binary_val
                out_f.write(machine_code + '\n')

            
            
            #C命令->ニーモニックに分解し変換 
            elif parser.command_type()=='C':
                d_nemonic = parser.dest()
                c_nemonic = parser.comp()
                j_nemonic = parser.jump()
                d_code = code.dest(d_nemonic)
                c_code = code.comp(c_nemonic)
                j_code = code.jump(j_nemonic)

                machine_code="111"+c_code+d_code+j_code
                out_f.write(machine_code + '\n')
            else:
                continue
    print(f"Complete!{output_file}!!")

if __name__ == "__main__":
    main()
        
