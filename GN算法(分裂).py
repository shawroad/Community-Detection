"""

@file   : GN算法(分裂).py

@author : xiaolu

@time1  : 2019-06-04

"""
import networkx as nx
import matplotlib.pyplot as plt


def load_graph(path):
    g = nx.Graph()
    with open(path, 'r', encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('\n', '')
            nodex, nodey = line.split('\t')
            # 因为我们是无权图，所以这里将所有的边权重设为1.0
            g.add_edge(nodex, nodey, weight=1.0)
    return g


# 移除边界数最大的边
def removing_based_on_betweeness(g):

    init_ncomp = nx.number_connected_components(g)  # 连通图的数量
    curr_ncomp = init_ncomp
    while curr_ncomp <= init_ncomp:
        # 因为我们删除边界数大的边就是为了不连通  所以只要边界数大的边删除后，连通数量大于原来的数量就停止
        bws = nx.edge_betweenness_centrality(g, weight='weight')  # 计算边界数

        # print(bws)   # 输出{('1', '0'): 0.016091067186605964, ....}
        max_bw = max(bws.values())

        for nodes, bw in bws.items():
            if bw == max_bw:
                g.remove_edge(*nodes)   # 相当于删除当前边界数大的边
        curr_ncomp = nx.number_connected_components(g)   # 更新连通数量


def get_deg(g):
    # 统计每个队和别人打的次数
    adj = nx.adj_matrix(g)
    nodes = g.nodes()
    t = adj.sum(axis=1)  # [[队0和别人打的次数], [对1和别人打得次数], [对2和别人打得次数], [*]...]
    return {node: t[i, 0] for i, node in enumerate(nodes)}


def get_modularity(g, init_deg, m):
    deg = get_deg(g)
    modularity = 0
    for comp in nx.connected_components(g):
        for node in comp:
            modularity += (deg[node] - init_deg[node] ** 2 / (2 * m))
    return modularity / (2 * m)


def gn(g):
    init_n = g.number_of_edges()
    print("总共的边数(相当于两两比赛的总次数):", init_n)    # 统计所有的边数  总共613  也就是613次比赛

    if init_n == 0:
        return None

    # 简单的一个预处理
    m = nx.adj_matrix(g)   # 按第一列从小到大 整理我们的数据
    m = m.sum() / 2  # 总的比赛数

    init_deg = get_deg(g)
    # print(init_deg)   # {"队0": 打的次数, "队1": 打的次数, ...}

    i = 1
    while g.number_of_edges() > 420:
        removing_based_on_betweeness(g)
        # 迭代5词计算一下模块度
        if i % 5 == 0:
            print("迭代次数:{} 模块度的值:{} 边数:{}".format(i, get_modularity(g, init_deg, m), g.number_of_edges()))
        i += 1
    print("模块度最大: {}".format(get_modularity(g, init_deg, m)))

    # 社团中止时的图
    nx.draw_networkx(g)
    plt.show()

    return nx.connected_components(g)


if __name__ == "__main__":
    # 1. 加载数据
    graph = load_graph("./data/network.dat")

    # 2. 画出我们的网络结构图
    nx.draw_networkx(graph)
    plt.show()

    # 3. 进行社团检测
    set_list = gn(graph)
    total = []
    for temp in set_list:
        total.append(list(temp))

    # 4.写入文件  这种写入文件的数据与标签文件的样子相同  但是我们检测预测的准确率
    result = []
    for temp in total:
        for i in temp:
            result.append([i, total.index(temp)])

    f = open('./data/predict.txt', 'w')
    for r in result:
        f.write(str(r[0]) + '\t')
        f.write(str(r[1]) + '\n')
    f.close()
