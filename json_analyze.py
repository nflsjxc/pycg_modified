import os
import json
import sys
from stdlib_list import stdlib_list

stdlib=stdlib_list("3.9")

class jsonAnalyzer(object):
    def __init__(self,filename,listarg):
        sys.setrecursionlimit(10000)
        self.filename=filename
        self.module_graph=dict()
        self.forest_roots=[]
        self.module_to_id=dict()
        self.id_to_module=dict()
        self.module_names=[]
        self.all_modules=None
        self.internal_modules=None
        self.external_modules=None
        self.graphinfo=None
        self.internal_calls=None
        self.external_calls=None
        self.external_module_list=None
        self.internal_module_list=None
        self.ext_module_graph=dict()
        self.ext_module_graph_nostd=dict()
        self.self_module=[]
        for i in listarg.split(' '):
            try:
                name=i.split('/')[-1].split('.')[-2]
                self.self_module.append(name)
            except:
                pass
        self.self_module=list(set(self.self_module))

        with open(filename) as f:
            self.data=json.load(f)
        self.graphConstruct()
        self.moduleGraphConstruct()
    
    def moduleGraphConstruct(self):
        
        def constructExternalNoStd(cur,par):
           # print(cur, par)
            if cur in vis:
                return
            else:
                vis[cur]=True
            if par==None:
                pass
            else:
                self.ext_module_graph_nostd[par].append(cur)
                self.ext_module_graph_nostd[par]=list(set(self.ext_module_graph_nostd[par]))
            for tar in self.ext_module_graph[cur]:
                if cur not in stdlib_list:
                    constructExternalNoStd(tar,cur)
                else:
                    constructExternalNoStd(tar,par)

        def constructExternal(cur,par):
          #  print(cur, par)
            if cur in vis:
                return
            else:
                vis[cur]=True
            if cur in self.external_module_list:
                if par==None:
                    pass
                else:
                    self.ext_module_graph[par].append(cur)
                    self.ext_module_graph[par]=list(set(self.ext_module_graph[par]))
            for tar in self.module_graph[cur]:
                if cur in self.external_module_list:
                    constructExternal(tar,cur)
                else:
                    constructExternal(tar,par)

        def findforestroot(names,graph):
            indeg=dict()
            for i in names:
                indeg[i]=0
            
            for i in graph:
                for j in graph[i]:
                    #from i to j
                    if i==j:
                        continue
                    indeg[j]+=1

            forest_roots=[]
            for i in names:
                if indeg[i]==0:
                    forest_roots.append(i)
            
            return forest_roots

        for i in self.module_to_id:
            self.module_graph[i]=[]
        
        for i in self.graph:
            for j in self.graph[i]:
                # i,j: '0',...
                srcmod=self.id_to_module[i]
                tarmod=self.id_to_module[j]

                self.module_graph[srcmod].append(tarmod)
                self.module_graph[srcmod]=list(set(self.module_graph[srcmod])) #could be more efficient?
        
        self.forest_roots=findforestroot(self.module_names,self.module_graph)
        
        vis=dict()
        for i in self.external_module_list:
            self.ext_module_graph[i]=[]
        for i in self.forest_roots:
            constructExternal(i,None)

        self.ext_forest_roots=findforestroot(self.external_module_list,self.ext_module_graph)
        
        self.external_module_list_nostd=[i for i in self.external_module_list if i not in stdlib]
        vis=dict()
        for i in self.external_module_list_nostd:
            self.ext_module_graph_nostd[i]=[]
        for i in self.ext_forest_roots:
            constructExternalNoStd(i,None)
        self.ext_forest_roots_nostd=findforestroot(self.external_module_list_nostd,self.ext_module_graph_nostd)

    def structOutput(self):
        for i in self.forest_roots:
            self.outputTree(self.module_graph,i,1)

    def structOutputExternal(self):
        for i in self.ext_forest_roots:
            self.outputTree(self.ext_module_graph,i,1)
    
    def structOutputExternalNoStd(self):
        for i in self.ext_forest_roots_nostd:
            self.outputTree(self.ext_module_graph_nostd,i,1)

    def outputTree(self,graph,node,deep=0):
        formatstr=""
        for i in range(deep-1):
            formatstr+=' '
        print(formatstr,end="")
        print('|')
        for i in range(deep):
            formatstr+='--'

        print(formatstr,end="")
        print(node,end='')
        if node in self.internal_module_list:
            print("  (internal module)")
        if node in self.external_module_list:
            print("  (external module)")
        if node in stdlib:
            print("  (stdandard library)")
        
        
        for i in graph[node]:
            if i == node: # self calling, ignore...
                continue
            self.outputTree(graph,i,deep+4)

    def graphConstruct(self):
        self.all_modules=self.data['modules']
        self.internal_modules=self.all_modules['internal']
        self.external_modules=self.all_modules['external']

        #internal modules
        self.internal_module_list=[]
        for i in self.internal_modules:
            self.module_to_id[i]=[]
            details=self.internal_modules[i]
            self.internal_module_list.append(i)
            namespace=details['namespaces']
            for j in namespace:
                self.module_to_id[i].append(j)
                self.id_to_module[j]=i
                self.module_names.append(i)

        #external modules
        self.external_module_list=[]
        for i in self.external_modules:
            self.module_to_id[i]=[]
            details=self.external_modules[i]

            self.external_module_list.append(i)
            # if not i in self.self_module: 
            #     self.external_module_list.append(i)
            
            namespace=details['namespaces']
            for j in namespace:
                self.module_to_id[i].append(j)
                self.id_to_module[j]=i
                self.module_names.append(i)

        self.module_names=list(set(self.module_names))

        self.graphinfo=self.data['graph']
        self.internal_calls=self.graphinfo['internalCalls']
        self.external_calls=self.graphinfo['externalCalls']

        self.graph=dict()
        for i in self.id_to_module:
            self.graph[i]=[]

        for i in self.internal_calls: 
            src=i[0]
            tar=i[1]
            self.graph[src].append(tar)

        for i in self.external_calls: 
            src=i[0]
            tar=i[1]
            self.graph[src].append(tar)

if __name__=='__main__':
    jan=jsonAnalyzer('./Tempfile/output.json','')
    # jan.structOutput()
    # jan.structOutputExternal()
    jan.structOutputExternalNoStd()