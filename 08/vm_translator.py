import sys
import os
from vm_parser import Parser
from vm_code import CodeWriter

def translate(vm_file, code_writer):
    # ファイル名取得
    file_name = os.path.basename(vm_file).replace(".vm","")

    
    code_writer.setFileName(file_name) 

    parser = Parser(vm_file)

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
        
        elif cmd_type == 'C_LABEL':
            code_writer.writeLabel(parser.arg1())
            
        elif cmd_type == 'C_GOTO':
            code_writer.writeGoto(parser.arg1())
            
        elif cmd_type == 'C_IF':
            code_writer.writeIf(parser.arg1())
        
        elif cmd_type == 'C_FUNCTION':
            code_writer.writeFunction(parser.arg1(), parser.arg2())
            
        elif cmd_type == 'C_CALL':
            code_writer.writeCall(parser.arg1(), parser.arg2())
            
        elif cmd_type == 'C_RETURN':
            code_writer.writeReturn()

    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python vm_translator.py <file.vm>")
        sys.exit(1)
    input_path = sys.argv[1]
    vm_files=[]
    #出力ファイル名, 入力vmファイルのリストを決定
    if os.path.isdir(input_path):
        #フォルダ名.asm
        input_path=input_path.rstrip('/')
        output_file=input_path+"/"+os.path.basename(input_path)+".asm"

        for f in os.listdir(input_path):
            if f.endswith(".vm"):
                vm_files.append(os.path.join(input_path, f))
    else:
        #~.vm->~.asm
        output_file=input_path.replace(".vm",".asm")
        vm_files.append(input_path)

    code_writer=CodeWriter(output_file)

    if os.path.isdir(sys.argv[1]):
        code_writer.writeInit()
    
    for vm_file in vm_files:
        translate(vm_file, code_writer)
    
    code_writer.close()
    print(f"Complete!: {output_file}")


            


