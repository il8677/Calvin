import os

heuristicsFolder = os.path.dirname(os.path.realpath(__file__)) + "/heuristics"
manifest = heuristicsFolder+"/manifest.mn"

def checkFiles():
    if(os.path.isdir(heuristicsFolder)):
        print("[HEURISTICS : CHECK] Heuristics folder exists")
    else:
        print("[HEURISTICS : CHECK] Heuristics folder does not exist, creating")
        os.mkdir(heuristicsFolder)
    try:
        open(manifest, "r")
    except FileNotFoundError:
        print("[HEURISTICS : CHECK] Manifest missing, creating")
        open(manifest,"w")

checkFiles()