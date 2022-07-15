import os
import pycgmain as pycg
import json_analyze 

# get all py file in current dir
def getAllPyFile(path,pylist):
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
    for dl in curPathDirList:
        getAllPyFile(path + "/" + dl,pylist)
    return pylist


def filefeeder():
    pyfilelist=getAllPyFile(targetdir,[])
    allPyFile=""
    for i in pyfilelist:
        allPyFile+=i+" "
        # print(i)
    return allPyFile

if __name__=="__main__":
    targetdir=input("Plese enter target dir: ")
    targetdir=os.path.abspath(targetdir)

    if os.path.exists("./Tempfile/output.json"):
        os.remove("./Tempfile/output.json")
    #can be changed?
    
    allPyFile=filefeeder()
    # allPyFile=os.path.join(targetdir,"*.py")
    #allPyFile=targetdir

    operation="pycg --package " + targetdir + " " + allPyFile+ " -o ./Tempfile/output.json --fasten" #seems to have problems, need solve
    print(operation)
    os.system(operation)
    janalyzer=json_analyze.jsonAnalyzer("./Tempfile/output.json",allPyFile)

    #Too much
    # print("All graph:")
    # janalyzer.structOutput()
    print("Ext graph:")
    janalyzer.structOutputExternalNoStd()