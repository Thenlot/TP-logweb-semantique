
from functools import reduce


charger = lambda f: open(f, encoding="utf-8").read()
text = charger("tp1.txt")
print(text)

# 3. clean(text)
inutiles = ['et', 'les']
clean = lambda text: [mot[:-1] if mot[-1] == 's' else mot for mot in text.lower().split('.')[0].split(' ') if mot not in inutiles]
mots = clean(text)
print("mots     =", mots)



# 4. to_onto(mots) : groupes de 3 mots
to_onto = lambda mots: [mots[3*i:3*(i+1)] for i in range(len(mots)//3)]
onto = to_onto(mots)
print("onto     =", onto)

# 5. prefixe(onto, p)
prefixe = lambda onto, p: [[p + t for t in triplet] for triplet in onto]
onto = prefixe(onto, ":")
print("prefixe  =", onto)

# 6. remplacement d'un préfixe par une url (slice [:len(prefixe)])
remplace = lambda onto, p, url: [
    [url + t[len(p):] if t[:len(p)] == p else t for t in triplet]
    for triplet in onto
]
prefixes = [(":",     "http://localhost:8080/tp1#"),
            ("rdf:",  "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
            ("rdfs:", "http://www.w3.org/2000/01/rdf-schema#"),
            ("owl:",  "http://www.w3.org/2002/07/owl#")]
remplace_tous = lambda onto, prefixes: reduce(lambda o, pu: remplace(o, pu[0], pu[1]), prefixes, onto)

# 7. unparse_nt(onto) + sauvegarde en n-triples
unparse_nt = lambda onto: "\n".join("<%s> <%s> <%s> ." % tuple(t) for t in onto)
sauve = lambda onto, f: (lambda fh: (fh.write(unparse_nt(onto) + "\n"), fh.close()))(open(f, "w", encoding="utf-8"))

# 8. ontologie delta ajoutée à onto
delta = [[":Personne", "rdf:type", "owl:Class"],
         [":Joueur",   "rdf:type", "owl:Class"],
         [":Amoureux", "rdf:type", "owl:Class"],
         [":joueur",   "rdf:type", ":Joueur"]]
dedup = lambda l: [t for i, t in enumerate(l) if t not in l[:i]]
onto = dedup(onto + delta)

# 9. requete_1 : sujets qui aiment quelqu'un/quelque chose
requete_1 = lambda onto: list(dict.fromkeys(s for s, p, o in onto if p == ":aime"))
print("requete_1 =", requete_1(onto))

# 10. inference_1 : tout sujet qui aime est de type :Personne
inference_1 = lambda onto: dedup(onto + [[s, "rdf:type", ":Personne"] for s in requete_1(onto)])

# 11. personnes connues
personnes = lambda onto: list(dict.fromkeys(s for s, p, o in onto if p == "rdf:type" and o == ":Personne"))

# 12. inference_2 : un Joueur = une personne aimant jouer
inference_2 = lambda onto: dedup(onto + [[s, "rdf:type", ":Joueur"]
                                         for s in personnes(onto) if [s, ":aime", ":jouer"] in onto])

# 13. inference_3 : si un sujet (personne) est de catégorie C != Personne alors C rdfs:subClassOf :Personne
inference_3 = lambda onto: dedup(onto + [[o, "rdfs:subClassOf", ":Personne"]
                                         for s, p, o in onto
                                         if p == "rdf:type" and s in personnes(onto) and o != ":Personne"])

# Application des règles (composition)
inferer = lambda onto: inference_3(inference_2(inference_1(onto)))
onto = inferer(onto)
print("personnes =", personnes(onto))
for t in onto: print(t)

# Sauvegarde finale
sauve(remplace_tous(onto, prefixes), "tp1.nt")
print(open("tp1.nt", encoding="utf-8").read())
