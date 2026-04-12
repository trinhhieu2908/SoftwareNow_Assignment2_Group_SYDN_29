from encrypt import encrypt


def main():
    shift1 = int(input("Enter shift1: "))
    shift2 = int(input("Enter shift2: "))

    f = open("raw_text.txt", "r", encoding="utf-8")
    raw_text = f.read()
    f.close()

    encrypted = encrypt(raw_text, shift1, shift2)

    f = open("encrypted_text.txt", "w", encoding="utf-8")
    f.write(encrypted)
    f.close()


if __name__ == "__main__":
    main()
