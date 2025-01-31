import csv
from tqdm import tqdm
import os
from collections import Counter


class WordleSolver:
    def __init__(self, wordlen):
        self.wordlen = wordlen
        self.databaseDir = r"database"
        self.workDir = os.path.join(self.databaseDir, str(wordlen) + "Letter")
        self.states = ["Grey", "Yellow", "Green"]
        self.wordsFilepath = self.getWordListpath()
        self.possibleWords = self.loadWords()
        self.totalPossibleWords = len(self.possibleWords)
        self.stateCombinations = self.generateStates(wordlen)
        self.used_guesses = set()  # Track words we've already suggested

    def preSetup(self):
        os.makedirs(self.workDir, exist_ok=True)
        
        if not os.path.exists(self.wordsFilepath):
            raise FileNotFoundError(f"Word list not found at {self.wordsFilepath}")
        if not os.path.exists(os.path.join(self.workDir, "eliminations.csv")):
            self.writeEliminations()
        if not os.path.exists(os.path.join(self.workDir, "initialEntropy.csv")):
            self.writeInitialEntropy()

    def writeEliminations(self):
        headers = ["Word"] + ["".join(state) for state in self.stateCombinations]
        print("Computing eliminations csv...")
        with open(os.path.join(self.workDir, "eliminations.csv"), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for word in tqdm(self.possibleWords, total=self.totalPossibleWords, desc="Processing words"):
                eliminations = self.findPossibleEliminations(word)
                writer.writerow([word] + eliminations)
        print(f"Eliminations csv written (path: {self.workDir}/eliminations.csv)")

    def writeInitialEntropy(self):
        headers = ["Word", "Entropy"]
        print("Computing initial entropy csv...")
        with open(os.path.join(self.workDir, "initialEntropy.csv"), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for word in tqdm(self.possibleWords, total=self.totalPossibleWords, desc="Processing words"):
                entropy = self.computeEntropy(word)
                writer.writerow([word, entropy])
        print(f"Initial entropy csv written (path: {self.workDir}/initialEntropy.csv)")

    def getWordListpath(self):
        filename = f"database-{self.wordlen}L.txt"
        path = os.path.join(self.databaseDir, f"{self.wordlen}Letter", filename)
        return path

    def loadWords(self):
        with open(self.wordsFilepath, "r") as file:
            words = file.read().splitlines()
            return [word.strip().lower() for word in words if len(word.strip()) == self.wordlen]

    def generateStates(self, n):
        if n == 0:
            return [[]]
        return [[state] + pattern for state in self.states for pattern in self.generateStates(n - 1)]

    def getTemplate(self, originalword, guessedword):
        if len(originalword) != len(guessedword):
            raise ValueError("Words must be the same length")
            
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

    def validateFeedback(self, feedback):
        if len(feedback) != self.wordlen:
            raise ValueError(f"Feedback must be {self.wordlen} states long")
        for state in feedback:
            if state not in self.states:
                raise ValueError(f"Invalid state: {state}. Must be one of {self.states}")
        return True

    def findPossibleEliminations(self, word):
        eliminationCounter = Counter()
        for posword in self.possibleWords:
            feedback = self.getTemplate(posword, word)
            eliminationCounter[feedback] += 1

        return [eliminationCounter.get(tuple(state), 0) for state in self.stateCombinations]

    def computeEntropy(self, word):
        eliminations = self.findPossibleEliminations(word)
        total = sum(eliminations)
        if total == 0:
            return 0
        return sum([-count / total * (count / total) for count in eliminations if count > 0])

    def filterWords(self, feedback, guess):
        filtered = [word for word in self.possibleWords if self.getTemplate(word, guess) == feedback]
        self.possibleWords = filtered
        return filtered

    def getBestGuess(self, entropyData):
        # Sort words by entropy, highest to lowest
        sorted_words = sorted(entropyData.items(), key=lambda x: x[1], reverse=True)
        
        # Return the highest entropy word that hasn't been used
        for word, entropy in sorted_words:
            if word not in self.used_guesses:
                return word
                
        # If all words have been used (unlikely), clear the used_guesses and start over
        self.used_guesses.clear()
        return sorted_words[0][0] if sorted_words else None

    def run(self):
        self.preSetup()

        initialEntropyPath = os.path.join(self.workDir, "initialEntropy.csv")
        with open(initialEntropyPath, "r") as file:
            reader = csv.reader(file)
            next(reader)
            entropyData = {row[0]: float(row[1]) for row in reader}

        possibleWords = self.possibleWords
        guess_count = 0

        print("\nWordle Solver Initialized!")
        print(f"Word length: {self.wordlen}-letters")
        print(f"Total possible words: {len(possibleWords)}\n")
        print("Note: Press Enter without input to get next best word suggestion")

        while len(possibleWords) > 1:
            guess_count += 1
            print(f"\nGuess #{guess_count}")
            print(f"Remaining possible words: {len(possibleWords)}")

            bestGuess = self.getBestGuess(entropyData)
            if not bestGuess:
                print("No more valid words available!")
                break
                
            print(f"Best guess: {bestGuess}")

            while True:
                try:
                    feedback = input(f"Enter feedback for {bestGuess} (e.g., Grey,Yellow,Green,...) or press Enter for next suggestion: ").strip()
                    
                    if not feedback:  # Empty input
                        self.used_guesses.add(bestGuess)  # Mark current word as used
                        bestGuess = self.getBestGuess(entropyData)  # Get next best word
                        if bestGuess:
                            print(f"Next suggestion: {bestGuess}")
                            continue
                        else:
                            print("No more suggestions available!")
                            break
                    
                    feedback = tuple(feedback.split(','))
                    if self.validateFeedback(feedback):
                        break
                except (ValueError, IndexError) as e:
                    print(f"Error: {e}")
                    print("Please try again.")

            # If we broke the inner loop due to no more suggestions
            if not bestGuess:
                break

            possibleWords = self.filterWords(feedback, bestGuess)
            self.used_guesses.add(bestGuess)  # Add the used word to our set

            if len(possibleWords) > 1:
                entropyData = {word: self.computeEntropy(word) for word in possibleWords}

        if len(possibleWords) == 1:
            print(f"\nSolution found in {guess_count} guesses!")
            print(f"The solution is: {possibleWords[0]}")
        else:
            print("\nNo solution found!")


if __name__ == "__main__":
    WordleSolver(7).run()