import sys
import os
from vm_parser import Parser
from vm_code import CodeWriter

def main():
    if len(sys.argv) != 2:
        print("使い方: python vm_translator.py <file.vm>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = os.path.splitext(input_file)[0] + ".asm"

    # ファイル名取得
    # : "C:/.../Class1.vm" -> "Class1.vm"
    base_name = os.path.basename(input_file)
    # "Class1.vm" -> "Class1"
    file_name = os.path.splitext(base_name)[0]

    # インスタンスの作成
    code_writer = CodeWriter(output_file)
    code_writer.setFileName(file_name) 

    parser = Parser(input_file)

    while parser.has_more_lines():
        parser.advance()
        cmd_type = parser.command_type()

        if cmd_type == 'C_ARITHMETIC':
            command= parser.arg1()
            code_writer.writeArithmetic(command)
            
        elif cmd_type in ['C_PUSH', 'C_POP']:
            segment= parser.arg1()
            index= parser.arg2()
            code_writer.writePushPop(cmd_type, segment, index)

    code_writer.close()
    print(f"Complete!: {output_file}")
    
if __name__ == "__main__":
    main()

            


