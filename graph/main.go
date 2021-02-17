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

    var src, rec string
    var dst int
    for srcRec, d := range path {
        dst = d
        splited := strings.Split(srcRec, "/")
        src, rec = splited[0], splited[1]
        graph += src + " -> " + rec + " [label=\"\"];\n"
    }
    fmt.Println(dst, string(dst))
    graph += rec + " -> " + strconv.Itoa(dst) + " [label=\"\"];\n}"
    return graph
}
