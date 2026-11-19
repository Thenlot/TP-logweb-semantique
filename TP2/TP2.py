import subprocess
from functools import reduce

dic = {}
compteur = 1

inutiles = ['et', 'les']

prefixes = [
    ("rdf:",  "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("rdfs:", "http://www.w3.org/2000/01/rdf-schema#"),
    ("owl:",  "http://www.w3.org/2002/07/owl#"),
    (":",     "http://localhost:8080/tp1#")
]


def inc():
    global compteur
    compteur += 1
    return compteur - 1


def var():
    return "V" + str(inc())


def charger(f):
    with open(f, encoding="utf-8") as fichier:
        return fichier.read()


def remplace(onto, p, url):
    return [
        [
            url + t[len(p):] if t.startswith(p) else t
            for t in triplet
        ]
        for triplet in onto
    ]


def remplace_tous(onto, prefixes):
    return reduce(
        lambda o, pu: remplace(o, pu[0], pu[1]),
        prefixes,
        onto
    )

def parse_nt(texte):

    onto = []

    for line in texte.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        elements = line.rstrip(".").split()

        if len(elements) < 3:
            continue

        triplet = []

        for element in elements[:3]:
            element = element.strip("<>")

            element = element.rsplit("#", 1)[-1]
            element = element.rsplit("/", 1)[-1]

            if ":" in element:
                element = element.split(":")[-1]

            triplet.append(element)

        onto.append(triplet)

    return onto


def unparse_dot(onto):
    dot_lines = ["digraph {"]

    for s, p, o in onto:
        dot_lines.append(f'    "{s}" -> "{o}" [label="{p}"];')

    dot_lines.append("}")
    return "\n".join(dot_lines)


def interpret(cmd):
    mots = cmd.split()


    if mots[0] == "declare":

        nom = var()
        dic[nom] = mots[1]

        print(f"Mémorisé dans {nom}")
        return nom

    elif mots[0] == "charge":

  
        nom = var()
        dic[nom] = charger(mots[1])

        print(f"Chargé dans {nom}")
        return nom


    elif mots[0] == "parse" and mots[1] == "nt":

        source = mots[2]

        onto = parse_nt(dic[source])

        onto = remplace_tous(onto, prefixes)

        nom = var()
        dic[nom] = onto

        print(f"Parse NT dans {nom}")
        return nom

    elif mots[0] == "affiche":


        nom = mots[1]

        print(dic[nom])
        return dic[nom]

    elif mots[0] == "unparse" and mots[1] == "dot":
        
        source = mots[2]

        dot = unparse_dot(dic[source])

        nom = var()
        dic[nom] = dot

        print(f"Unparse DOT dans {nom}")
        return nom

    elif mots[0] == "sauvegarde":
        
        source = mots[1]
        fichier = mots[2]

        with open(fichier, "w", encoding="utf-8") as fh:
            fh.write(dic[source])

        print(f"Sauvegardé dans {fichier}")
        return fichier

    elif mots[0]=="compile":
        source = mots[1]
        subprocess.run(["dot", "-o", "tp2.png" , "-Tpng", source])

    else:
        return "Je ne sais pas"



interpret("declare V1")
interpret("charge tp1.nt")
interpret("parse nt V2")
interpret("affiche V3")
interpret("unparse dot V3")
interpret("affiche V4")
interpret("sauvegarde V4 tp2.dot")
interpret("compile tp2.dot")