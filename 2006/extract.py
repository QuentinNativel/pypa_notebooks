from path import Path

TAG = {
    "ID": "ID",
    "HOSPITAL": "HO",
    "DATE": "DA",
    "DOCTOR": "DO",
    "PATIENT": "PA",
    "LOCATION": "LO",
    "PHONE": "PH",
    "AGE": "AG",
}


def get_string(input_path):
    with open(input_path, "r") as f:
        return f.read()


def clean_text(txt, to_remove=[":", ";", ", "]):
    txt = txt.replace("&apos;", "'").replace("\n", " ").replace("<PHI", " <PHI")
    for c in to_remove:
        txt = txt.replace(c, "")
    return txt


def extract_entities(cleaned_txt):
    result = []
    phrase = 0  # phrases are indexed from 0
    words = cleaned_txt.split(" ")
    i = 0
    while i < len(words):
        w = words[i]
        if w in {".", "?", "!"}:
            phrase += 1
        elif w == "":
            pass
        elif "<PHI" not in w:
            result.append(
                [phrase, "O   ", w]
            )  # ending spaces to make the output easy to read
        else:
            local_tag = TAG[words[i + 1].split('TYPE="')[1].split('"')[0]]
            result.append(
                [  # handling the first word of the entity
                    phrase,
                    "B-" + local_tag,
                    words[i + 1].split('">')[1].split("</PHI>")[0],
                ]
            )
            if (
                "</PHI>" in words[i + 1]
            ):  # the entity is like : '<PHI TYPE="[TAG]">WORD</PHI>'
                w2 = words[i + 1].split("</PHI>")[1]
                if (
                    w2 != ""
                ):  # the entity is like : '<PHI TYPE="[TAG]">WORD1</PHI>WORD2'
                    result.append(
                        [phrase, "O   ", w2]
                    )  # ending spaces to make the output easy to read
                i += 1
            else:  # the entity is like : '<PHI TYPE="[TAG]">WORD1 WORD2 WORD3</PHI>'
                j = 2
                while "</PHI>" not in words[i + j]:
                    result.append([phrase, "I-" + local_tag, words[i + j]])
                    j += 1
                w1, w2 = words[i + j].split("</PHI>")
                result.append([phrase, "I-" + local_tag, w1])
                if (
                    w2 != ""
                ):  # the end is like : '<PHI TYPE="[TAG]">WORD1 WORD2 WORD3</PHI>WORD4'
                    result.append(
                        [
                            phrase,
                            "O   ",  # ending spaces to make the output easy to read
                            w2,
                        ]
                    )
                    i += 1
                i += j
        i += 1
    return result


def output(result):
    with open("result.txt", "w+") as f:
        for row in result:
            f.write(("\t".join([str(x) for x in row]) + "\n"))


if __name__ == "__main__":
    output(extract_entities(clean_text(get_string(Path("test.xml")))))
