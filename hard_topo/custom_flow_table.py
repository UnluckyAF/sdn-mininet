def dijkstra(graph, s, f):
    INF = 999999999
    path = dict()
    d = [float(INF) for _ in range(len(graph))]
    used = [False for _ in range(len(graph))]
    #print("GRAPH\n", graph)
    d[s] = 0
    path[s] = str(s + 1)
    for i in range(len(graph)):
        v = None
        for j in range(len(graph)):
            if not used[j] and (v is None or d[j] < d[v]):
                v = j
        if d[v] == INF:
            break
        #print("here", v)
        used[v] = True
        for edge in graph[v]:
            if d[v] + edge[1] < d[edge[0]]:
                path[edge[0]] = path[v] + '/' + str(edge[0] + 1)
                d[edge[0]] = d[v] + edge[1]
        #print("DIJKSTRA", d)
    #print("MAP\n", path)
    return path[f]


def reverse_weights(flows, max_weight=1000):
    graph = list()
    for host in flows:
        v = list()
        for link in host:
            v.append((link[0], max_weight - link[1]))
        graph.append(v)

    return graph


def create_table(matrix, flows):
    #print("MATRIX\n", matrix, "\nFLOWS\n", flows)
    graph = reverse_weights(matrix)
    f = open("flow_table", "w")
    for flow in flows:
        #in flows real nubers of hosts/switches are used (from 1 to ...), but in graph numerating starts
        #from 0, because graph is a list of links for every host 
        path = dijkstra(graph, flow[0][1][0] - 1, flow[0][1][1] - 1)
        f.write(path + '\n')
    f.close()
