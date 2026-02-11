# Simple function to pluralize a word on any numeral other than 1. You can optionally put in a non-standard pluralization if the word doesn't just add an S.
def pluralize(numeral: int, word: str, pluralword: str = ""):
    if numeral == 1:
        return word
    elif pluralword:
        return pluralword
    else:
        return word + "s"
    
# Simple function 
def aAn(word: str, capital: bool = False):
    vowels = ["a", "e", "i", "o", "y", "A", "E", "I", "O", "U"]
    if capital:
        a = "A"
        an = "An"
    else:
        a = "a"
        an = "an"
    if word[0] in vowels or word.startswith("X "):
        return f"{an} {word}"
    else:
        return f"{a} {word}"