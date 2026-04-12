from encrypt import encrypt
from decrypt import decrypt


def verify():
    f = open("raw_text.txt", "r", encoding="utf-8")
    raw_text = f.read()
    f.close()

    f = open("decrypted_text.txt", "r", encoding="utf-8")
    decrypted_text = f.read()
    f.close()

    if raw_text == decrypted_text:
        print("The decryption was successful.")
    else:
        print("The decryption was not successful.")


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

    decrypted = decrypt(encrypted, shift1, shift2)

    f = open("decrypted_text.txt", "w", encoding="utf-8")
    f.write(decrypted)
    f.close()

    verify()


if __name__ == "__main__":
    main()
