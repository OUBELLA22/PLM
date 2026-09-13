# KATATOOL — Guide de soutenance

Fichier : **`KATATOOL_Soutenance_Youssef_OUBELLA.pptx`** — 34 diapositives, 16:9, notes de présentateur sur chaque diapositive.

Les notes contiennent, pour chaque diapositive, ce qu'il faut **dire** (pas ce qui est écrit à l'écran) et la durée visée. En mode Présentateur : `Diaporama > Mode Présentateur`.

---

## 5 choses à faire avant la soutenance

| # | Diapo | À faire |
|---|-------|---------|
| 1 | 1 et 34 | Remplacer le cadre **LOGO** par le logo de l'entreprise |
| 2 | 4 | Remplacer le cadre **PHOTO** par votre photo (celle du CV) |
| 3 | 20 | Insérer votre capture **Capital XC — Copy Harness Design** |
| 4 | 23 | Insérer votre capture **ENOVIA — Product ECO** (avec le message d'erreur) |
| 5 | partout | Vérifier le nom de l'entreprise en pied de page |

> **Attention au nom de l'entreprise.** J'ai utilisé **MG2 Engineering** (le logo de votre PPT KATATOOL), alors que votre CV indique **Capgemini Engineering**. Corrigez selon l'entité devant laquelle vous soutenez : `Rechercher / Remplacer` sur `MG2 Engineering`.

Les quatre cadres en pointillés sont des **emplacements** : cliquez sur le cadre, `Insérer > Image`, puis supprimez le cadre. Tant qu'ils sont là, ils se voient — ne les oubliez pas.

---

## Structure et minutage (cible ≈ 22 min)

| Diapos | Chapitre | Durée |
|--------|----------|-------|
| 1–2 | Titre + sommaire | 1 min |
| 3–8 | **01 — Présentation & parcours professionnel** | 4 min 30 |
| 9–14 | **02 — Contexte & problématique** | 4 min 30 |
| 15–27 | **03 — KATATOOL** | 8 min 30 |
| 28–33 | **04 — Bénéfices & perspectives** | 3 min 30 |
| 34 | Merci + questions | reste |

### Si on vous donne moins de temps

Supprimez dans cet ordre, la logique reste intacte :

- **≈ 15 min** — retirez 5, 17, 21, 32
- **≈ 12 min** — retirez en plus 20, 24, 26

Ne retirez **jamais** : 10 (Le constat), 13 (Problématique), 29 (Avant / Après), 33 (Conclusion). Ce sont les quatre diapositives sur lesquelles le jury vous évalue.

---

## Les 4 moments qui décident de la validation

**Diapo 10 — « Le savoir existe. Il est introuvable. »**
Affichez, puis **taisez-vous 2 secondes**. Laissez la phrase s'installer. Tout le monde dans la salle a vécu ça.

**Diapo 13 — La problématique.**
Lisez la question **une seule fois, lentement**. N'ajoutez rien après. C'est la phrase que le jury doit retenir.

**Diapo 29 — Avant / Après.**
La diapositive la plus persuasive. Lisez la colonne de gauche, puis celle de droite, ligne par ligne. Ne vous précipitez pas.

**Diapo 33 — La conclusion.**
« J'ai identifié le problème sur le terrain, et j'ai construit la réponse avec les moyens de l'entreprise. » Regardez le jury. Puis silence.

---

## Le fil narratif

Le déroulé n'est pas « moi, puis mon app ». Il est construit pour que KATATOOL paraisse **inévitable** :

1. **Chapitre 01** installe discrètement votre **double profil** — ingénieur faisceaux 2D *et* développeur / créatif (diapo 8, bloc violet). Sans ce chapitre, l'application semble sortir de nulle part.
2. **Chapitre 02** montre un problème que le jury reconnaît immédiatement, vécu de l'intérieur, pas théorique.
3. **Chapitre 03** répond point par point aux 4 objectifs de la diapo 14.
4. **Chapitre 04** traduit le projet en valeur : intégration, autonomie, capitalisation, image client.

Si un membre du jury demande « pourquoi vous ? », la réponse est déjà à l'écran depuis la diapo 8.

---

## Questions probables — réponses préparées

Elles sont aussi dans les notes de la diapo 34.

**« Combien de temps pour le développer ? »**
Donnez un chiffre honnête, et précisez : sur mon temps, sans impact sur les livrables projet.

**« Qui met le contenu à jour ? »**
Un référent par équipe. Je reste garant de la structure. Le contenu est séparé du code, donc une mise à jour ne demande pas de développement.

**« Et la confidentialité des données ? »**
100 % local. Aucune donnée ne sort du poste, aucun serveur externe, aucune connexion sortante.

**« Pourquoi pas simplement SharePoint ? »**
La meilleure question, et la meilleure réponse : SharePoint **stocke**. KATATOOL **guide, évalue et fonctionne hors ligne**. Ce n'est pas un espace de fichiers, c'est un parcours avec un niveau mesuré.

**« Est-ce maintenable si vous partez ? »**
Structure simple et documentée, contenu séparé du code, et je peux former un référent par équipe.

**« Est-ce que ça a été validé par la hiérarchie / l'IT ? »**
Si ce n'est pas le cas, dites-le franchement et présentez-le comme une initiative personnelle mise à disposition de l'équipe. C'est un point fort, pas une faiblesse — mais ne laissez pas croire à une validation qui n'existe pas.

---

## Conseils de présentation

- **Ne lisez jamais l'écran.** Les diapositives ne portent que des titres et des mots-clés, exprès. Le contenu, c'est vous.
- **Une idée par diapositive.** Si vous vous surprenez à tout expliquer sur une diapositive, avancez.
- **Les chiffres de la diapo 16** (5 applications, 3 sections PLM, 4 quiz, 2 équipes) : mettez-les à jour s'ils ont changé. Un chiffre faux devant le jury coûte cher.
- **Répétez à voix haute deux fois**, chronomètre en main. Le minutage des notes suppose un débit posé.
- **Si vous pouvez faire une démonstration live de 2 minutes**, faites-la après la diapo 27, puis revenez sur la 28. Testez-la avant : hors ligne, c'est votre meilleur argument.

---

## Régénérer le fichier

Le deck est produit par script, dans `build/` :

```bash
cd build
python3 build_deck.py      # génère le .pptx
python3 validate.py        # structure OOXML et relations
python3 fit_check.py       # aucun texte ne dépasse de son cadre
python3 overlap_check.py   # aucune collision, aucun texte hors carte
```

Modifiez le texte dans `build_deck.py` puis relancez : la mise en page se recalcule (hauteurs de titres, taille de corps de texte uniforme par rangée). Vous pouvez aussi éditer directement le `.pptx` dans PowerPoint — dans ce cas, ne relancez plus le script, il écraserait vos modifications.

---

## Vérifications effectuées

- Structure OOXML, relations et types de contenu : **valides**, 151 parts, 501 formes
- 34 diapositives, **notes de présentateur sur chacune**
- 394 blocs de texte contrôlés : **aucun débordement estimé**
- **Aucune collision** de texte, aucun texte sortant de sa carte

Ces contrôles sont géométriques et calculés à partir de métriques Segoe UI approchées. **Ouvrez le fichier dans PowerPoint pour un contrôle visuel final** avant la soutenance — c'est la seule vérification que je ne peux pas faire à votre place.
