import csv


def parse_row(row, num):
    assert len(row) == num

    links = list()
    for i in range(len(row)):
        if int(row[i]) > 0:
            links.append((i, float(row[i])))

    return links


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


def parse_inits(path):
    paths = list()
    with open(path, "r") as f:
        for line in f:
            pth, tick, start, lifetime = line.split('\t')
            paths.append((path_to_map(pth), float(tick), float(start), float(lifetime)))
    return paths

