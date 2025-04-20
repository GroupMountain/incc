# pip install libclang
# if you want use newer version of libclang, you can download file like "LLVM-20.1.3-win64.exe" from https://github.com/llvm/llvm-project/releases
import getopt
import os
import sys
import threading
from typing import List, Set
import clang.cindex as CX

if os.path.exists("""C:\\Program Files\\LLVM\\bin\\libclang.dll"""):
    CX.Config.set_library_file("""C:\\Program Files\\LLVM\\bin\\libclang.dll""")

opts, args = getopt.getopt(sys.argv[1:], "", ["compile-commands=", "result="])
res_path = "result.txt"
path = "./"
for opt in opts:
    if "--compile-commands" in opt:
        path = opt[1]
    if "--result" in opt:
        res_path = opt[1]

cdb: CX.CompilationDatabase = CX.CompilationDatabase.fromDirectory(path)
incs: Set[str] = set()
threads: List[threading.Thread] = []
lock = threading.Lock()
for i in cdb.getAllCompileCommands():
    print(i.filename, "loaded")
    args = []
    for arg in i.arguments:
        if arg != i.filename:
            args.append(arg)

    def parse(filename, args, lock):
        index = CX.Index.create()
        local_data = threading.local()
        local_data.incs = set()
        try:
            tu = index.parse(path + filename, args)
            for inc in tu.get_includes():
                file: str = str(inc.location.file)
                if "include\mc" in file:
                    name = file[file.find("include\mc") + 8 :]
                    local_data.incs.add(name)
        except Exception as e:
            print(e)
        with lock:
            for i in local_data.incs:
                incs.add(i)
        print(filename, "finished")

    threads.append(threading.Thread(target=parse, args=(i.filename, args, lock)))
    while threading.active_count() > 12:
        pass
    threads[-1].start()

for i in threads:
    i.join()

with open(res_path, "w") as res:
    for i in incs:
        res.write(i + "\n")
