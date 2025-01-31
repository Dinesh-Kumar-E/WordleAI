import os
from tqdm import tqdm

minwordlength = 4
maxwordlength = 12

corpusPath = r"database\words_alpha.txt"
baseDir = r"database"

def readCorpus():
    with open(corpusPath, 'r') as file:
        corpus = file.read().splitlines()
    return (word.lower() for word in corpus)


for word in tqdm(list(readCorpus()), desc="Processing words"):
    if (len(word) > maxwordlength) or (len(word) < minwordlength):
        continue
    else:
        if not os.path.exists(os.path.join(baseDir, str(len(word))+"Letter")):
            os.makedirs(os.path.join(baseDir, str(len(word))+"Letter"))
            with open(os.path.join(baseDir, str(len(word))+"Letter", f"database-{len(word)}L"+".txt"), 'w') as file:
                file.write(word)
                file.write("\n")
        else:
            with open(os.path.join(baseDir, str(len(word))+"Letter", f"database-{len(word)}L"+".txt"), 'a') as file:
                file.write(word)
                file.write("\n")


        