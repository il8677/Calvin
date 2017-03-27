import os
import math

heuristicsFolder = os.path.dirname(os.path.realpath(__file__)) + "/heuristics"
manifest = heuristicsFolder + "/manifest.mn"


def checkFiles():
    if os.path.isdir(heuristicsFolder):
        print("[HEURISTICS : CHECK] Heuristics folder exists")
    else:
        print("[HEURISTICS : CHECK] Heuristics folder does not exist, creating")
        os.mkdir(heuristicsFolder)
    try:
        open(manifest, "r")
    except FileNotFoundError:
        print("[HEURISTICS : CHECK] Manifest missing, creating")
        open(manifest, "w")
# NEURAL FILE FORMAT
# Each line is a layer
# Values are seperated by semi colons
#
# Number of nodes in layer

networks = {}

class Network:
    def __init__(self, name,layers=[]):
        self.layers=layers
        self.name = name
    def classifyio(self):
        self.layers[0].isInput=True
        self.layers[len(self.layers) - 1].isOutput = True
class Layer:
    def addNode(self):
        self.nodes.append(Node(1))
    def __init__(self, nodes=[], isInput=False, isOutput=False):
        self.nodes = nodes
        self.length = len(nodes)
        self.isInput = isInput
        self.isOutput = isOutput
class Node:
    def sigmoid(x):
        return 1 / (1 + math.exp(-x))

    def __init__(self, weights):
        self.weights = weights

def readNeuralFile(path):
    lines = open(path).read().split("\n")
    name = lines[0]
    del lines[0]
    sizes = []
    layers=[]
    for line in lines:
        sizes.append(int(line))
    for size in sizes:
        nodes=[]
        for i in range (0,size):
            nodes.append(Node(1))
        layers.append(Layer(nodes=nodes))
    networks[name] = Network(name,layers)
    networks[name].classifyio()
    print("Done!")

readNeuralFile("/Users/isaaclewis/PycharmProjects/Calvin/heuristics/neural1.neural")