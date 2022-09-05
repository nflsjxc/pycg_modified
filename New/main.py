import time
import shlex
import os,subprocess
import json_analyze 
import shutil
import random
import sys
from treelib import Tree

# get all py file in current dir
def getAllPyFile(path,pylist,recurse_flag):
    curPathDirList=[]
    files=os.listdir(path)
    for f in files:
        if os.path.isdir(path + "/" + f):
            if f[0] == ".": # hidden folder
                pass
            else:
                curPathDirList.append(f)
        if os.path.isfile(path + "/" + f):
            if f.split('.')[-1]=='py':
                pylist.append(os.path.abspath(path + "/" + f))
    if recurse_flag:
        for dl in curPathDirList:
            getAllPyFile(path + "/" + dl,pylist,recurse_flag)
    return pylist


def filefeeder(targetdir):
    pyfilelist=getAllPyFile(targetdir,[],False)
    pyfilelist=random.sample(pyfilelist,min(len(pyfilelist),5)) #choose ? .py file as entry_point (?)
    if os.path.exists(os.path.join(targetdir,'__init__.py')):
        pyfilelist.append(os.path.join(targetdir,'__init__.py'))
        pyfilelist=list(set(pyfilelist))
    allPyFile=""
    for i in pyfilelist:
        allPyFile+=i+" "
        # print(i)
    return allPyFile

def filefeeder_all(targetdir):
    pyfilelist=getAllPyFile(targetdir,[],True)
    if os.path.exists(os.path.join(targetdir,'__init__.py')):
        pyfilelist.append(os.path.join(targetdir,'__init__.py'))
        pyfilelist=list(set(pyfilelist))
    allPyFile=""
    for i in pyfilelist:
        allPyFile+=i+" "
        # print(i)
    return allPyFile

def merge(a:list,b:list)->list:
    return list(set(a+b))

# def main_execute(targetdir,id) -> json_analyze.jsonAnalyzer:
#     global analyzed_ext_modules,direct_dependency,inherited_dependency,process_list,analyzed_dir_list,timeout_const
#     #can be changed?
#     if targetdir in analyzed_dir_list:
#         return None
#     else:
#         analyzed_dir_list.append(targetdir)

#     jsonname="output"+str(id)+".json"
#     if os.path.exists("./Tempfile/"+jsonname):
#         os.remove("./Tempfile/"+jsonname)
#     allPyFile=filefeeder(targetdir)
#     # allPyFile=os.path.join(targetdir,"*.py")
#     #allPyFile=targetdir

    

#     # operation="pycg --package " + targetdir + " " + allPyFile+ " -o ./Tempfile/"+jsonname+" --fasten" #seems to have problems, need solve
#     operation ="pycg --package " + targetdir + " " + "$(find "+targetdir+" -type f -name \"*.py\")"+ " -o ./Tempfile/"+jsonname+" --fasten"
#     # operation ="pycg --package " + targetdir + " " + targetdir+"/*.py"+ " -o ./Tempfile/"+jsonname+" --fasten"
#     print(operation)
#     try:
#         # operation=shlex.split(operation)
#         process=subprocess.Popen("exec "+operation, stdout=subprocess.PIPE,shell=True)
#         process.wait(timeout=timeout_const)  #wait for ? seconds
#         process_list.append(process)
#     except subprocess.TimeoutExpired:
#         process.terminate()
#         print("Timeout... trying another")
#         try:
#             operation ="pycg --package " + targetdir + " " + targetdir+"/*.py"+ " -o ./Tempfile/"+jsonname+" --fasten"
#             print(operation)
#             process=subprocess.Popen("exec "+operation, stdout=subprocess.PIPE,shell=True)
#             process.wait(timeout=timeout_const)  #wait for ? seconds
#             process_list.append(process)
#         except:
#             process.terminate()
#             print("Timeout... trying another")
#             try:
#                 process.terminate()
#                 operation="pycg --package " + targetdir + " " + allPyFile+ " -o ./Tempfile/"+jsonname+" --fasten" 
#                 print(operation)
#                 process=subprocess.Popen("exec "+operation, stdout=subprocess.PIPE,shell=True)
#                 process.wait(timeout=timeout_const)  #wait for ? seconds
#                 process_list.append(process)
#             except:
#                 process.terminate()
#                 print("Failed..")
#     except:
#         process.terminate()
#         print("Failed..")
#     try:
#         allPyFile=filefeeder_all(targetdir)
#         janalyzer=json_analyze.jsonAnalyzer("./Tempfile/"+jsonname,allPyFile,targetdir,analyzed_ext_modules)
#     except json_analyze.AnalyzeFailError:
#         print("Analyze json Failed..")
#         return None
#     analyzed_ext_modules=merge(analyzed_ext_modules,janalyzer.analyzed_ext_modules)
#     #Too much
#     # print("All graph:")
#     # janalyzer.structOutput()
#     print("Ext graph:")
#     janalyzer.struct_output_external_no_std()
#     return janalyzer


import signal

class TimeoutException(Exception):   # Custom exception class
    pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException

# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

def main_execute(targetdir,id) -> json_analyze.jsonAnalyzer:
    global analyzed_ext_modules,direct_dependency,inherited_dependency,process_list,analyzed_dir_list,timeout_const
    #can be changed?
    if targetdir in analyzed_dir_list:
        return None
    else:
        analyzed_dir_list.append(targetdir)

    jsonname="output"+str(id)+".json"
    if os.path.exists("./Tempfile/"+jsonname):
        os.remove("./Tempfile/"+jsonname)
    # allPyFile=filefeeder(targetdir)
    allPyFile=filefeeder_all(targetdir)
    # allPyFile=os.path.join(targetdir,"*.py")
    #allPyFile=targetdir

    # operation="find "+targetdir+" -type f -name \"*.py\""
    # process=subprocess.Popen(operation, stdout=subprocess.PIPE,shell=True)
    # allPyFile=process.stdout.readlines()
    # for i in range(len(allPyFile)):
    #     allPyFile[i]=str(allPyFile[i])
    # print(allPyFile)
    # operation="pycg --package " + targetdir + " " + allPyFile+ " -o ./Tempfile/"+jsonname+" --fasten" 
    operation="pycg --package " + targetdir + " " + allPyFile+ " -o ./Tempfile/"+jsonname+" --fasten --max-iter 50" #seems to have problems, need solve
    operation_output="pycg --package " + targetdir 

    sys.path.append('/home/cabbage/Desktop/sci/Utils/pycg_mod') 
    from hook import activate
    try:
        # signal.signal(signal.SIGALRM, timeout_handler)
        # signal.alarm(timeout_const)
        # print(operation_output)
        # operation=shlex.split(operation)
        # activate(operation[1:])
        # signal.alarm(0)

        print(operation_output)
        operation=shlex.split(operation)
        activate(operation[1:])
    except TimeoutException:
        print("Timeout...")
    except:
        print("Failed..")
    try:
        allPyFile=filefeeder_all(targetdir)
        janalyzer=json_analyze.jsonAnalyzer("./Tempfile/"+jsonname,allPyFile,targetdir,analyzed_ext_modules)
    except json_analyze.AnalyzeFailError:
        print("Analyze json Failed..")
        return None
    analyzed_ext_modules=merge(analyzed_ext_modules,janalyzer.analyzed_ext_modules)
    #Too much
    # print("All graph:")
    # janalyzer.structOutput()
    print("----------------------Result-----------------------")
    print("Ext graph:")
    janalyzer.struct_output_external_no_std()
    print()
    return janalyzer

def recurse(janalyzer,id,depth):
    global analyzed_ext_modules,direct_dependency,inherited_dependency,analyzers,total_id
    global dependency_tree
    if depth>4: #only recurse a fixed depth
        return
    added_nodes=[] #in order to add end nodes
    for i in janalyzer.get_extra_dependency():
        name=i[0]
        i=i[1]
        if i==None:
            continue
        retval=main_execute(i,len(analyzers)+1)
        total_id+=1
        dependency_tree.create_node(tag=name,identifier=total_id,parent=id)
        added_nodes.append(name)
        if retval!=None:
            analyzers.append(retval)
            recurse(retval,total_id,depth+1)
    for i in janalyzer.all_external_mods:
        if i not in added_nodes:
            added_nodes.append(i)
            total_id+=1
            dependency_tree.create_node(tag=i,identifier=total_id,parent=id)
    for i in analyzers:
        inherited_dependency=merge(inherited_dependency,i.analyzed_ext_modules)


if __name__=="__main__":
    timeout_const=30

    if os.path.exists("./Tempfile"):
        shutil.rmtree("./Tempfile")
    if not os.path.exists("Tempfile"):
        os.mkdir("Tempfile")

    # targetdir=input("Plese enter target dir: ")
    # targetdir=os.path.abspath(targetdir)

    targetdir='/home/cabbage/Desktop/sci/Utils/test/testCase'
    # targetdir=os.path.abspath('/home/cabbage/.conda/envs/sci/lib/python3.9/site-packages/urllib3')
    

    # global analyzed_ext_modules,direct_dependency,inherited_dependency
    analyzed_ext_modules=[]
    direct_dependency=[]
    inherited_dependency=[]
    process_list=[]
    analyzers=[]
    analyzed_dir_list=[]
    analyzer_root=(main_execute(targetdir,1))
    analyzers.append(analyzer_root)
    try:
        direct_dependency=analyzer_root.analyzed_ext_modules
        dependency_tree=Tree()
        dependency_tree.create_node(tag=targetdir.split('/')[-1],identifier=1)
        total_id=1
        recurse(analyzer_root,1,1)

        print("--------------Final----------------")
        print(direct_dependency)
        print(inherited_dependency)
        print(analyzed_ext_modules)
        dependency_tree.show()
    except:
        print("root error...")
    try:
        for i in process_list:
            i.terminate()
    except:
        print("find if there's any process left....")
    
    