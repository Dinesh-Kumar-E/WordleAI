from collections import Counter
import csv
from tqdm import tqdm

States = ["Grey", "Yellow", "Green"]
wordlen = 5
wordsFilepath = r"words\database.txt"

def generateStates(n):
    if n == 0:
        return [[]]
    else:
        return [[state] + pattern for state in States for pattern in generateStates(n-1)]

with open(wordsFilepath, "r") as file:
    possibleWords = file.read().splitlines()
TotalpossibleWords = len(possibleWords)

def getTemplate(originalword, guessedword):

    template = ["Grey"] * len(originalword)
    original_used = [False] * len(originalword)
    guessed_used = [False] * len(guessedword)

    for i in range(len(originalword)):
        if originalword[i] == guessedword[i]:
            template[i] = "Green"
            original_used[i] = True
            guessed_used[i] = True

    for i in range(len(guessedword)):
        if not guessed_used[i]:
            for j in range(len(originalword)):
                if not original_used[j] and guessedword[i] == originalword[j]:
                    template[i] = "Yellow"
                    original_used[j] = True
                    break

    return tuple(template)  

def findPossibleEliminations(word):
    eliminationCounter = Counter()
    for posword in possibleWords:
        feedback = getTemplate(word, posword)
        eliminationCounter[feedback] += 1

    return [eliminationCounter.get(tuple(state), 0) for state in generateStates(wordlen)]

def writeEliminations():

    headers = ["Word"] + ["".join(state) for state in generateStates(wordlen)]

    with open(r'words\eliminations.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        for word in tqdm(possibleWords, total=TotalpossibleWords, desc="Processing words"):
            eliminations = findPossibleEliminations(word)
            writer.writerow([word] + eliminations)

writeEliminations()
