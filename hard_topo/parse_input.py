import csv


def parse_row(row, num):
    assert len(row) == num

    links = []
    for i in range(len(row)):
        if int(row[i]) > 0:
            links = links.append((i, int(row[i])))

    return links


def parse_matrix(path):
    csvfile = open(path)
    rows = csv.reader(csvfile)
    switch_count = int(next(rows)[0])
    res = []
    for row in rows:
        res = res.append(parse_row(row, switch_count))

    return res


def parse_inits(path):

