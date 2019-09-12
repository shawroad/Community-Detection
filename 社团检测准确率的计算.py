"""

@file   : 社团检测准确率的计算.py

@author : xiaolu

@time1  : 2019-06-05

"""
import numpy as np
import math


def NMI(A, B):
    # 社团检测评估算法 NMI 基于归一化互信息向量的匹配方法

    # 1. len(A) 应该等于 len(B)
    total = len(A)
    A_ids = set(A)
    B_ids = set(B)

    # 2. 互信息
    MI = 0
    eps = 1.4e-45
    for idA in A_ids:
        for idB in B_ids:
            idAOccur = np.where(A == idA)   # 找出A 在A_ids中的编号
            idBOccur = np.where(B == idB)   # 找出B 在B_ids中的编号
            idABOccur = np.intersect1d(idAOccur, idBOccur)  # 返回两个数组中相同值的个数
            px = 1.0 * len(idAOccur[0]) / total   # 每种类别所占比例
            py = 1.0 * len(idBOccur[0]) / total   # 每种类别所占比例
            pxy = 1.0 * len(idABOccur) / total   # 两种类别直接的联合概率
            MI = MI + pxy * math.log(pxy / (px*py) + eps, 2)

    # 3.归一化互信息
    Hx = 0
    for idA in A_ids:
        idAOccurCount = 1.0 * len(np.where(A == idA)[0])
        Hx = Hx - (idAOccurCount / total) * math.log(idAOccurCount / total + eps, 2)
    Hy = 0
    for idB in B_ids:
        idBOccurCount = 1.0 * len(np.where(B == idB)[0])
        Hy = Hy - (idBOccurCount / total) * math.log(idBOccurCount / total + eps, 2)
    MIhat = 2.0 * MI / (Hx + Hy)
    return MIhat


def load_data(path):
    data = {}
    with open(path, 'r', encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            g, t = line.replace('\n', '').split('\t')
            data[g] = t
    return data


if __name__ == '__main__':
    path_real = './data/community.dat'
    path_predict = './data/Louvain_predict.txt'

    data_real = load_data(path_real)
    data_predict = load_data(path_predict)

    # print("真实数据:", data_real)
    # print("预测数据:", data_predict)
    # print(len(data_real))
    # print(len(data_predict))

    real, predict = [], []
    for i in range(0, 115):
        i = str(i)
        real.append(data_real.get(i))
        predict.append(data_predict.get(i))
    real = np.array(real)
    predict = np.array(predict)
    print("准确率:", NMI(real, predict))
