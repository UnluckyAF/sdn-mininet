import csv


# [(host_num, bandwidth), ...]
def parse_row(row, num):
    print(row)
    assert len(row) == num

    links = list()
    for i in range(len(row)):
        if int(row[i]) > 0:
            links.append((i, int(row[i])))

    return links


# input: adjacency matrix with weight as bandwidth
# returns:
# [
#  [(host_num, bandwidth), ...],
#  [(host_num, bandwidth), ...]
# ]
def parse_matrix(path):
    res = []
    with open(path) as csvfile:
        rows = csv.reader(csvfile)
        switch_count = int(next(rows)[0])
        for row in rows:
            if len(row) == 0:
                break
            res.append(parse_row(row, switch_count))

    return res


def path_to_map(path):
    res = dict()
    verts = path.split('/')
    if len(verts) == 2:
        return (res, (int(verts[0]), int(verts[1])))

    for i in range(len(verts) - 2):
        res[verts[i] + '/' + verts[i + 1]] = int(verts[i + 2])
    return (res, (int(verts[0]), int(verts[1])))


# input:
# path tickrate(s)
# 2/3/0/7\t0.2
# returns:
# [
#  ((map_path --- {...}, (initiator --- int, its_destination --- int)), tickrate --- float),
#  ...
# }
def parse_inits(path):
    paths = list()
    with open(path, "r") as f:
        for line in f:
            print(line)
            pth, tick = line.split('\t')
            paths.append((path_to_map(pth), float(tick)))
            print("hui")
    return paths
