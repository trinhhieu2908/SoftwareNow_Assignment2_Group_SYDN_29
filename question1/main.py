from encrypt import encrypt
from decrypt import decrypt

def get_number(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")

def read_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None

def verify():
    raw_text = read_file("raw_text.txt")
    if raw_text is None:
        print("Error: raw_text.txt not found. Please ensure the file exists.")
        return

    decrypted_text = read_file("decrypted_text.txt")
    if decrypted_text is None:
        print("Error: decrypted_text.txt not found. Please ensure the file exists.")
        return

    if raw_text == decrypted_text:
        print("The decryption was successful.")
    else:
        print("The decryption was not successful.")


def main():
    shift1 = get_number("Enter shift1: ")
    shift2 = get_number("Enter shift2: ")

    raw_text = read_file("raw_text.txt")
    if raw_text is None:
        print("Error: raw_text.txt not found. Please ensure the file exists.")
        return

    encrypted = encrypt(raw_text, shift1, shift2)

    f = open("encrypted_text.txt", "w", encoding="utf-8")
    f.write(encrypted)
    f.close()

    decrypted = decrypt(encrypted, shift1, shift2)

    f = open("decrypted_text.txt", "w", encoding="utf-8")
    f.write(decrypted)
    f.close()

    verify()


if __name__ == "__main__":
    main()
