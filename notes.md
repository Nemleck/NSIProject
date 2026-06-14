# INFORMATIONS PRINCIPALES

‌Bonjour, voici les détails de mon projet, sur lequel je réalise tout le travail, et qui en conséquences peut se retrouver un peu moins chargé d'ici la date de démo, si le temps manque.

Dans les grandes lignes :

- Je réalise seul mon projet (je fais maquettes, graphismes, puis code (du jeu et de l'IA))
    -> Je n'exclue pas, si ce n'est pas interdit, un peu d'aide extérieure quand à de petites réflexions pour réaliser un algorithme, de l'aide pour des librairies ou des noms de fonction éventuellement

- Je réalise un jeu solo, à l'apparence multijoueur car les autres joueurs seront des IA, apprenant via du machine learning, mais si le temps me le permet, je le rendrais réellement multijoueur.
    -> Le but du jeu est d'être le dernier dans la partie. Pour cela, on doit affronter les autres joueurs.
    -> Chaque joueur a une classe, qui est un personnage doué de caractéristiques comme la vie ou la puissance d'attaque, mais surtout une capacité spéciale, que les IA doivent apprendre à utiliser.
    -> Les informations sur ce jeu que j'ai notées et que j'utiliserai pour le réaliser sont disponibles sur ce __Notion__ : https://messy-countess-b32.notion.site/Projet-NSI-93f780586ac84ba3b8fe93d96536ef09?pvs=4‌

# ETAT DES LIEUX (13/05/2024)

## Avancée globale

- **Le projet est dans la globalité avancé**. Il ne reste que le système de mutation, certaines attaques (attaques basique du chevalier par exemple), mais il y a quelques bugs *(voir section bugs)*

- **La texture de l'eau et des boules de feu pourraient changer**. Via l'utilisation de ma tablette graphique, je peux améliorer ces textures, mais cela rentre dans les détails, donc à la fin.

- **Le système d'entraînement des IA n'est pas encore développé** - ou en tous cas le programme principal de cet entraînement n'est pas testé, et il n'a a pas de `start.bat` non plus, pour mettre le bon chemin pour les images

- **De l'optimisation est à prévoir** - Actuellement, en lançant le jeu en mode non graphique, une seconde permet d'écouler environ 2 secondes de jeu, ce qui n'est pas assez rapide, mais ce qui a été tracé comme étant dû au cerveau des IA (Ironiquement, ce n'est pas vraiment le pathfinding le plus gourmand, puisqu'il prend moins d'2/5 environ du temps d'execution, et ce ne sont pas les collisions non plus, puisque les tuiles sont indexées)

## But du jeu / Comment jouer ?

- Touches z, q, s, d pour se déplacer
- Click de la souris pour attaquer (sauf chevalier pour le moment)
- Touche espace pour la capacité spéciale

- Le but est d'amasser le plus de points en 3 minutes, et de survivre

- Il n'est pour l'instant pas possible de choisir son personnage dans le jeu, il faut le changer manuellement dans `main.py`, à la définition du joueur, en remplaçant `wizard` par `fletcher` ou `knight`

### Personnages

- `wizard` - Pas très rapide, le sorcier peut attaquer à moyenne portée avec sa magie, ou lancer des boules de feu qui réduisent certains élément en poussière (arbres, fleurs)
- `knight` - Bien que lourd et lent, il fait des dégâts non négligeables et possède un large nombre de points de vie. Il ne se regénère pas naturellement, comme le sorcier ou le vendeur de flèches.
- `fletcher` - Le vendeur de flèches est rapide, et bien que ne causant pas beaucoup de dégâts, il tire vite et possède un bouclier protecteur qui ignore tous les dégâts pendant un certain temps. *(Attention, bouclier non fonctionnel pour le moment)*

### Ennemis

- `blob` - Il se déplace plutôt vite, et en groupe, mais ne fait pas beaucoup de dégâts.
- `bat` - Elles sont très rapides et infligent beaucoup de dégâts ! En revanche, si attaquées rapidement, elle n'ont pas beaucoup de points de vie.
- `livingTree` - Cet arbre intrépide est vivant, et fait beaucoup de dégats, de surcroît. En revanche, il ne se déplace pas beaucoup, et lentement.

### Objets

- `heart` - Les coeurs se génèrent de plus en plus vite au fil du temps. Ils permettent de récupérer des pvs facilement, pour échapper ou mieux tuer un ennemi/adversaire.

## Bugs connus

- **L'angle de tir des IA dans l'`InputData` de leur cerveau n'est pas correct dans la plupart des cas** - Le cosinus et le sinus sont probablement mal utilisés, ou alors c'est dû au radian.

- **La méthode de `GameObject` `scheduleMethod` n'est pas fonctionnelle**. Bien que longuement étudié, le bug persiste, et je n'ai pas vraiment compris pourquoi `self.scheduledTime` n'est jamais mis à jour. (À la ligne 25 de `gameElement.py`, changer `self.scheduledMethod` pour `self.scheduledTime` fait ne jamais passer le test, bien que la méthode `scheduleMethod` est appelée, ce qui est sûr puisque `self.scheduledMethod` est bien mis à jour)

- **La génération de la map fait que toute cette dernière n'est pas toujours accessible**. Les cailloux, les arbres, se génèrent devant les ponts, qui sont d'ailleurs toujours générés au même endroit, ce qui est largement un bug, mais qui pour être réglé demanderait probablement l'utilisation du pathfinding, ou peut-être des maths, à voir.

- **IndexError: list index out of range** - Ce bug survient je pense quand une IA essaye de trouver un chemin vers une case qui n'existe pas. Je n'ai pas encore pris le temps de le régler comme il n'arrive pas si souvent que ça, mais ce n'est quand même pas négligeable, et encore moins lorsqu'il s'agit de faire tourner ce programme des heures pour entraîner les IA.

- ~~**Le bouclier du fletcher n'est pas fonctionnel**, - C'est assez embêtant - il s'active en bleu mais ne protège pas vraiment des dégâts~~

## Les prochains ajouts

### Primodiaux

- **Réorganisation des classes** - Actuellement, c'est assez désastreux

- **Ajouter les attaques manquantes, voire de nouveaux personnages**

- **Optimiser le pathfinding** - càd remplir la map avec la distance des cases de manière limitée (ex: qu'une case autour) puis vérifier si un chemin est possible, puis augmenter cette limite, et recommencer... Permet de ne pas remplir inutilement les cases pour les petites distances, ce qui est souvent le cas.

- **Ajouter des nouveaux capteurs / de nouvelles Outputs pour les IA**, Comme les cases alentoures, ou le résultat du dernier pathfinding si pas trouvé (la case la plus haute, ...) ce qui me fait me questionner quant au comportement : Définir dans le code des comportements définis est moins intéressant que laisser les IA faire leur propre stratégie. Ce que je peux faire, au contraire, c'est leur permettre que créer le contenu de leur propre comportement, comme des variables booléennes qui rentrent comme capteur, permettant de faciliter la compréhension du cerveau.

- **Système de points intra-neuronaux**. Dans les secondes qui suivent l'activation d'un neurone, si l'action qui en résulte est positive, attribuer des points aux neurones, pour moins préférer les muter ensuite (Néanmoins, ne pas interdire la mutation du meilleur neurone. Le neurone avec le plus de points n'est pas forcément le plus performant, et laisser les IA évoluer sans ce neurone permet d'éviter aussi d'avoir que le même cerveau final)

### Secondaires

- ~~**Arbres vivants cachés**. Les arbres vivants seraient cachés, et leur vie aussi, mais leur visage serait toujours visible. Ils continueraient de faire des dégâts rapides, et se révèleraient si un joueur les approchent trop.~~

- **Ajouter une caméra défilante** - Cela permettrait de mieux diserner les textures, car on pourrait les afficher en plus gros, en plus d'ajouter de la difficulté quant aux joueurs/ennemis, et leur position

- **Ajouter un écran d'affichage du cerveau des IA**, pour voir en temps réel quel neurone est actif, pourquoi, et pour avoir un aspect visuel de l'évolution

- **Ajouter de la musique**. J'ai un appareil - un tracker - pour faire de la musique, et je peux y importer des ressources 8-bits, pour affirmer le côté retro du jeu. Faire des musiques, voire même des bruitages, pourrait largement augmenter le plaisir de jeu.

### Très secondaires (peut-être à faire après la date de rendu final)

- **Serveur Node.js, pour jouer en ligne**. Cela va demander beaucoup d'optimisation, mais pouvoir y jouer en ligne serait un large ajout, surtout que j'ai déjà fait pas mal de serveurs node.js, et ce jeu est la matière parfaite pour cela.

## Informations complémentaires

- Ce projet est sur gitHub, en privé pour le moment, et sera éventuellement avancé pendant les vacances, donc mis à jour là bas aussi. (https://github.com/Nemleck)

# REQUIREMENTS

- Librairie pygame
`pip install pygame`

- Librairies math, random, time, incluses dans python