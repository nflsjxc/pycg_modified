from logging import exception
import os
import json
import sys
from stdlib_list import stdlib_list
import utility as utils

stdlib=stdlib_list("3.9")

class AnalyzeFailError(Exception):
    pass

class jsonAnalyzer(object):
    def __init__(self,filename,listarg,pkgdir,analyzed_ext_modules):
        # listarg: excluded files(self modules)
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
        self.package_dir=pkgdir
        self.analyzed_ext_modules=analyzed_ext_modules
        for i in listarg.split(' '):
            try:
                name=i.split('/')[-1].split('.')[-2]
                self.self_module.append(name)
            except:
                pass
        self.self_module=list(set(self.self_module))
        try:
            with open(filename) as f:
                self.data=json.load(f)
        except FileNotFoundError:
            raise AnalyzeFailError
        self.graph_construct() #complete call graph
        self.module_graph_construct() #module call graph
    
    def module_graph_construct(self):
        
        def construct_external_no_std(cur,par): #construct external module graph no std
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
                    construct_external_no_std(tar,cur)
                else:
                    construct_external_no_std(tar,par)

        def construct_external(cur,par,ext_root): #construct external module graph
          #  print(cur, par)
            if cur in vis:
                return
            else:
                vis[cur]=True
            if cur in self.external_module_list:
                if par==None:
                    # pass
                    ext_root.append(cur)
                else:
                    self.ext_module_graph[par].append(cur)
                    self.ext_module_graph[par]=list(set(self.ext_module_graph[par]))
            for tar in self.module_graph[cur]:
                if cur not in self.internal_module_list:
                    construct_external(tar,cur,ext_root)
                else:
                    construct_external(tar,par,ext_root)

        def find_forest_root(names,graph): #find forest root
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
                try:
                    srcmod=self.id_to_module[i]
                    tarmod=self.id_to_module[j]

                    self.module_graph[srcmod].append(tarmod)
                    self.module_graph[srcmod]=list(set(self.module_graph[srcmod])) #could be more efficient?

                    if i=='649' or i=='650':
                        print("found!")
                except:
                    pass
        
        self.forest_roots=find_forest_root(self.module_names,self.module_graph)
        
        vis=dict()
        for i in self.external_module_list:
            self.ext_module_graph[i]=[]
        self.ext_forest_roots=[]
        for i in self.forest_roots:
            construct_external(i,None,self.ext_forest_roots)

        # self.ext_forest_roots=find_forest_root(self.external_module_list,self.ext_module_graph)
        

        #delete package modules
        from main import getAllPyFile
        package_mods=getAllPyFile(self.package_dir,[],True)
        for i in range(len(package_mods)):
            package_mods[i]=package_mods[i].split('/')[-1].split('.')[-2]
        package_mods_new=[] #get extra dependency to analyze
        self.all_external_mods=[] #serve as tree node
        for i in self.external_module_list:
            if i not in package_mods and i not in self.analyzed_ext_modules:
                package_mods_new.append(i)
            if i not in package_mods:
                self.all_external_mods.append(i)
        self.external_module_list_nostd=list(set(package_mods_new))
        self.external_module_list_nostd=[i for i in self.external_module_list_nostd if i not in stdlib]
        try:
            self.external_module_list_nostd.remove('.builtin')
        except:
            pass

        self.all_external_mods=list(set(self.all_external_mods))
        self.all_external_mods=[i for i in self.all_external_mods if i not in stdlib]
        try:
            self.all_external_mods.remove('.builtin')
        except:
            pass
        
        from main import merge
        self.analyzed_ext_modules=merge(self.external_module_list_nostd,self.analyzed_ext_modules)

        vis=dict()
        for i in self.external_module_list_nostd:
            self.ext_module_graph_nostd[i]=[]
        for i in self.ext_forest_roots:
            construct_external_no_std(i,None)
        self.ext_forest_roots_nostd=find_forest_root(self.external_module_list_nostd,self.ext_module_graph_nostd)

    def struct_output(self):
        for i in self.forest_roots:
            self.output_tree(self.module_graph,i,1)

    def struct_output_external(self):
        for i in self.ext_forest_roots:
            self.output_tree(self.ext_module_graph,i,1)
    
    def struct_output_external_no_std(self):
        for i in self.ext_forest_roots_nostd:
            self.output_tree(self.ext_module_graph_nostd,i,1)

    def output_tree(self,graph,node,deep=0):
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
            print("  (standard library)")
        
        
        for i in graph[node]:
            if i == node: # self calling, ignore...
                continue
            self.output_tree(graph,i,deep+4)

    def graph_construct(self):
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
    
    def get_extra_dependency(self):
        paths=[]
        for i in self.external_module_list_nostd:
            print(i)
            path=utils.get_package_dir(i)
            print(path)
            paths.append((i,path))
        return paths

if __name__=='__main__':
    ext=[]
    jan=jsonAnalyzer('./Tempfile/output1.json','','/home/cabbage/.conda/envs/sci/lib/python3.9/site-packages/torchvision',ext)
    # jan.struct_output()
    # jan.struct_output_external()
    print("---------------Result------------------")
    jan.struct_output_external_no_std()
    jan.get_extra_dependency()
    print(ext)
    print()
