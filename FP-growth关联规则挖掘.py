"""

@file   : FP-growth关联规则挖掘.py

@author : xiaolu

@time1  : 2019-06-10

"""

def read_data(path):
    data = []
    with open(path, 'r', encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('\n', '')
            temp = line.split('\t')
            data.append(temp)
    return data


class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue      # 节点名字
        self.count = numOccur      # 节点计数值
        self.nodeLink = None       # 用于链接相似的元素项
        self.parent = parentNode   # needs to be updated
        self.children = {}         # 子节点

    def inc(self, numOccur):
        '''
        对count变量增加给定值
        '''
        self.count += numOccur

    def disp(self, ind=1):
        '''
        将树以文本形式展示
        '''
        print('  '*ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind+1)


def loadSimpDat():
    simpDat = [
                ['I1', 'I2', 'I5'],
                ['I2', 'I4'],
                ['I2', 'I3'],
                ['I1', 'I2', 'I4'],
                ['I1', 'I3'],
                ['I2', 'I3'],
                ['I1', 'I3'],
                ['I1', 'I2', 'I3', 'I5'],
                ['I1', 'I2', 'I3']
              ]
    return simpDat


def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
        retDict[frozenset(trans)] = retDict.get(frozenset(trans), 0) + 1   # 若没有相同事项，则为1；若有相同事项，则加1
    return retDict


def createTree(dataSet, minSup=1):
    '''
    创建FP树
    '''
    headerTable = {}
    # 第一次扫描数据集
    for trans in dataSet:   # 计算item出现频数
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
    headerTable = {k:v for k,v in headerTable.items() if v >= minSup}
    freqItemSet = set(headerTable.keys())
    # print ('freqItemSet: ',freqItemSet)
    if len(freqItemSet) == 0: return None, None     # 如果没有元素项满足要求，则退出
    for k in headerTable:
        headerTable[k] = [headerTable[k], None]     # 初始化headerTable
    # print ('headerTable: ',headerTable)
    # 第二次扫描数据集
    retTree = treeNode('Null Set', 1, None)  # 创建树
    for tranSet, count in dataSet.items():
        localD = {}
        for item in tranSet:  # put transaction items in order
            if item in freqItemSet:
                localD[item] = headerTable[item][0]
        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]
            updateTree(orderedItems, retTree, headerTable, count)   # 将排序后的item集合填充的树中
    return retTree, headerTable     # 返回树型结构和头指针表


def updateTree(items, inTree, headerTable, count):
    if items[0] in inTree.children:     # 检查第一个元素项是否作为子节点存在
        inTree.children[items[0]].inc(count)     # 存在，更新计数
    else:   # 不存在，创建一个新的treeNode,将其作为一个新的子节点加入其中
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        if headerTable[items[0]][1] == None:    # 更新头指针表
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    if len(items) > 1:  # 不断迭代调用自身，每次调用都会删掉列表中的第一个元素
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)


def updateHeader(nodeToTest, targetNode):
    '''
    更新头指针表，确保节点链接指向树中该元素项的每一个实例
    '''
    while nodeToTest.nodeLink != None:
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode


def ascendTree(leafNode, prefixPath): #迭代上溯整棵树
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)


def findPrefixPath(basePat, treeNode): #treeNode comes from header table
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats


def mineTree(inTree, headerTable, minSup, preFix, freqItemList):
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1][0])]  # 1.排序头指针表
    for basePat in bigL:   # 从头指针表的底端开始
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        print('finalFrequent Item: ',  newFreqSet)    # 添加的频繁项列表
        freqItemList.append(newFreqSet)
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])
        print('condPattBases :', basePat, condPattBases)
        # 2.从条件模式基创建条件FP树
        myCondTree, myHead = createTree(condPattBases, minSup)
        # print ('head from conditional tree: ', myHead)
        # 3. 挖掘条件FP树
        if myHead != None:
            print('conditional tree for: ', newFreqSet)
            myCondTree.disp(1)
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList)


if __name__ == '__main__':
    minSup = 5
    # 加载数据
    path = './data/com-dblp.top5000.cmty.txt'
    simpDat = read_data(path)
    # simpDat = loadSimpDat()
    initSet = createInitSet(simpDat)
    myFPtree, myHeaderTab = createTree(initSet, minSup)
    myFPtree.disp()
    myFreqList = []
    mineTree(myFPtree, myHeaderTab, minSup, set([]), myFreqList)
