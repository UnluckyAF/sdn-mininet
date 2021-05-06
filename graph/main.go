package main

import (
    "fmt"
    "io/ioutil"
    "os"
    "os/exec"
    "strconv"
    "strings"
)

var path = map[string]int {
    "0/1": 2,
    "1/9": 0,
    "1/2": 0,
    "2/0": 3,
    "0/3": 4,
    "3/4": 5,
    "4/5": 6,
    "5/6": 3,
    "6/3": 7,
    "3/7": 8,
    "7/8": 3,
    "8/3": 9,
    "3/9": 0,
}

const (
    input = "tmp.gv"
    output = "graph.png"
)

func main() {
    if err := ioutil.WriteFile(input, []byte(getGraph(path)), 0600); err != nil {
        fmt.Println(err.Error())
        os.Exit(1)
    }

    if _, err := exec.Command("dot", "-Tpng", input, "-o", output).Output(); err != nil {
        fmt.Println(err.Error())
        os.Exit(1)
    }

    if err := os.Remove(input); err != nil {
        fmt.Println(err.Error())
        os.Exit(1)
    }
}

func getGraph(mp map[string]int) string {
    graph := "digraph G{\n"
    graph += "0 [shape=box];\n"
    graph += "1 [shape=box];\n"

    set := make(map[string]struct{})
    var src, rec string
    var dst int
    for srcRec, d := range path {
        dst = d
        splited := strings.Split(srcRec, "/")
        src, rec = splited[0], splited[1]
        graph += src + " -> " + rec + " [label=\"\"];\n"
        break
    }
    set[src + "/" + rec] = struct{}{}
    for {
        src, rec = rec, strconv.Itoa(dst)
        var ok bool
        dst, ok = path[src + "/" + rec]
        if !ok {
            break
        }
        if _, ok := set[src + "/" + rec]; !ok {
            set[src + "/" + rec] = struct{}{}
            graph += src + " -> " + rec + " [label=\"\"];\n"
        } else {
            break
        }
    }
    for srcRec, d := range path {
        if _, ok := set[srcRec]; ok {
            continue
        }
        dst = d
        splited := strings.Split(srcRec, "/")
        src, rec = splited[0], splited[1]
        graph += src + " -> " + rec + " [label=\"\"];\n"
    }
    fmt.Println(dst, string(dst))
    fmt.Println(graph)
    //graph += rec + " -> " + strconv.Itoa(dst) + " [label=\"\"];\n}"
    graph += "}"
    return graph
}
