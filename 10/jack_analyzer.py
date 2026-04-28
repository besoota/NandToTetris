import sys
import os
from jack_tokenizer import JackTokenizer
from  complie_engine import CompilationEngine

def analyze_file(input_file):
    #"~T.xml" で出力
    output_file = input_file.replace(".jack", "T.xml")
    
    print(f"Compiling: {input_file}  =>  {output_file}")
    
    # TokenizerとEngineを接続
    tokenizer = JackTokenizer(input_file)
    engine = CompilationEngine(tokenizer, output_file)
    
    # すべてのJackファイルは必ずクラス宣言から始まるので、
    # これを1回呼ぶだけで、再帰的にファイル全体のパースが完了する！
    engine.compileClass()
    
    engine.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python jack_analyzer.py <file.jack or directory>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    
    # フォルダが指定された場合は、中の .jack ファイルをすべて処理する
    if os.path.isdir(input_path):
        input_path = input_path.rstrip('/')
        for f in os.listdir(input_path):
            if f.endswith(".jack"):
                analyze_file(os.path.join(input_path, f))
    
    # 単一ファイルが指定された場合
    else:
        if input_path.endswith(".jack"):
            analyze_file(input_path)
        else:
            print("Error: Input must be a .jack file or a directory containing .jack files.")

if __name__ == "__main__":
    main()