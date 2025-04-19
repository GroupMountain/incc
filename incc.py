# pip install libclang
# if you want use newer version of libclang, you can download file like "LLVM-20.1.3-win64.exe" from https://github.com/llvm/llvm-project/releases
import getopt
import os
import sys
import threading
from typing import List
import clang.cindex as CX

if os.path.exists("""C:\\Program Files\\LLVM\\bin\\libclang.dll"""):
    CX.Config.set_library_file("""C:\\Program Files\\LLVM\\bin\\libclang.dll""")

opts, args = getopt.getopt(sys.argv[1:], "", ["compile-commands=", "result="])
res_path = "result.txt"
for opt in opts:
    if "--compile-commands" in opt:
        path = opt[1]
    if "--result" in opt:
        res_path = opt[1]

cdb: CX.CompilationDatabase = CX.CompilationDatabase.fromDirectory(path)
incs = set()
threads: List[threading.Thread] = []
for i in cdb.getAllCompileCommands():
    print(i.filename)
    args = []
    for arg in i.arguments:
        if arg != i.filename:
            args.append(arg)
    index = CX.Index.create()

    def parse(filename, args):
        try:
            tu = index.parse(path + filename, args)
            for inc in tu.get_includes():
                file: str = str(inc.location.file)
                if "include\mc" in file:
                    name = file[file.find("include\mc") + 8 :]
                    incs.add(name)
        except Exception as e:
            print(filename, e)
        print(filename, "finished")

    threads.append(threading.Thread(target=parse, args=(i.filename, args)))
    threads[-1].start()

for i in threads:
    i.join()

with open(res_path, "w") as res:
    for i in incs:
        res.write(i + "\n")
