from runner import WordleSolver

for wordlen in range(4, 13):
    print(f"Word length: {wordlen}")
    solver = WordleSolver(wordlen)
    solver.preSetup()
    print("-" * 20)
