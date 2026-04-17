def encrypt(text, shift1, shift2):
    result = ""
    for character in text:
        if "a" <= character <= "m":
            position = ord(character) - ord("a")
            new_position = (position + shift1 * shift2) % 13
            result += chr(ord("a") + new_position)
        elif "n" <= character <= "z":
            position = ord(character) - ord("n")
            new_position = (position - (shift1 + shift2)) % 13
            result += chr(ord("n") + new_position)
        elif "A" <= character <= "M":
            position = ord(character) - ord("A")
            new_position = (position - shift1) % 13
            result += chr(ord("A") + new_position)
        elif "N" <= character <= "Z":
            position = ord(character) - ord("N")
            new_position = (position + shift2 * shift2) % 13
            result += chr(ord("N") + new_position)
        else:
            result += character
    return result