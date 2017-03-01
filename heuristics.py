import os

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
# Top line is information
#
#
# Each line is a layer
# Values are seperated by semi colons
#
# Number of nodes in layer; Subsequent weights;

class node:
    def __init__(self, weights):
        self.weights = weights


def readNeuralFile(path):
    lines = open(path).read().split("\n")

    for line in lines:
        if(line[0] == "l"):
            values = line.split(";")
            del values[0]



















