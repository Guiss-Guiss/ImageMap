# 🎨 ImageMap

Une application Python pour le traitement d'images qui préserve la vivacité visuelle en évitant le moyennage des couleurs, avec une interface graphique et un support multilingue.

![Langages](https://img.shields.io/badge/Langages-FR%20|%20EN%20|%20DE%20|%20ES-blue)
![Python](https://img.shields.io/badge/Python-3.11.8-green)
![GPU](https://img.shields.io/badge/GPU-Compatible-brightgreen)
![Sans Moyenne](https://img.shields.io/badge/Sans%20Moyennage-✓-orange)

## 🎯 Innovation Principale

ImageMap révolutionne le redimensionnement d'images en éliminant le problème courant du moyennage des couleurs. Les algorithmes traditionnels créent de nouvelles couleurs moyennes qui tendent vers le gris, produisant des images plates et sans vie. ImageMap, au contraire :

- ✅ Ne moyenne jamais les couleurs, évitant l'effet "délavé"
- ✅ Maintient les contrastes vibrants de l'image originale
- ✅ Préserve la netteté des transitions de couleurs
- ✅ Conserve la visibilité et la netteté des petits détails

## 🔍 Le Problème des Méthodes Traditionnelles

Les méthodes classiques de redimensionnement :
- Créent de nouvelles couleurs moyennes inexistantes dans l'original
- Tendent vers le gris à cause du moyennage mathématique
- Perdent les contrastes subtils et les détails
- Produisent des images plus plates et moins vibrantes

## ✨ La Solution

L'approche d'ImageMap :
- Utilise uniquement les couleurs d'origine
- Empêche l'effet de grisaillement dû au moyennage
- Maintient la dynamique des couleurs originales
- Conserve l'impact visuel de l'image source

## 🛠️ Avantages Techniques

- **Sélection Intelligente des Couleurs** : Choisit la couleur d'origine la plus appropriée plutôt que de faire une moyenne
- **Conservation des Contrastes** : Maintient la séparation visuelle entre les zones de couleurs
- **Rétention des Détails** : Garde les petits éléments visuellement distincts
- **Anti-Grisaillement** : Évite l'effet de ternissement courant dans le redimensionnement traditionnel

## 🚀 Fonctionnalités

- 🎨 Zéro moyennage de couleurs lors du redimensionnement
- 📐 Résultats nets et clairs à toute échelle
- 🎯 Conservation de la vivacité des couleurs d'origine
- ⚡ Traitement accéléré par GPU
- 🌍 Interface en français, anglais, allemand et espagnol
- 💻 Interface graphique moderne avec ttkbootstrap
- 📊 Retour en temps réel sur le traitement

## 📋 Prérequis

- Python 3.11.8
- CUDA Toolkit (pour l'accélération GPU)  https://developer.nvidia.com/cuda-downloads
- Dépendances Python listées dans `requirements.txt`

## ⚙️ Installation

```bash
# Cloner le dépôt
git clone https://github.com/Guiss-Guiss/ImageMap.git

# Accéder au répertoire
cd ImageMap

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```

## 💡 Comparaison de Qualité Visuelle

####Redimensionnement Traditionnel :
- ❌ Crée des couleurs moyennées
- ❌ Tend vers le gris
- ❌ Perd en contraste
- ❌ Floute les détails

####ImageMap :
- ✅ Utilise uniquement les couleurs d'origine
- ✅ Maintient la vivacité des couleurs
- ✅ Préserve les contrastes
- ✅ Garde les détails nets

## 🔧 Fonctionnement

1. **Analyse**
   - Identifie toutes les couleurs originales de l'image
   - Cartographie les relations et transitions entre couleurs

2. **Redimensionnement Intelligent**
   - Sélectionne les couleurs d'origine appropriées pour chaque pixel
   - Évite la création de couleurs moyennes grisées

3. **Préservation des Détails**
   - Maintient des transitions nettes entre les couleurs
   - Préserve l'impact visuel des petits détails

## 📝 Détails Techniques

- Traitement RGB natif
- Support des formats PNG, JPG, JPEG, BMP
- Algorithmes optimisés pour GPU
- Zéro interpolation de couleurs

## 💻 Utilisation

1. Lancement via `python main.py`
2. Chargement de votre image
3. Définition du facteur d'échelle
4. Redimensionnement avec maintien de la vivacité des couleurs
5. Sauvegarde de votre résultat net et vibrant

## 🎯 Avantage Clé

Contrairement aux outils de redimensionnement traditionnels qui moyennent les couleurs et créent une image plus terne, ImageMap maintient l'impact visuel de l'image d'origine en évitant complètement le moyennage des couleurs, produisant des résultats plus nets et plus vibrants à n'importe quelle taille.

## 🤝 Contribution

Ce projet est propriétaire. Pour toute suggestion ou rapport de bug, veuillez me contacter.

## 📜 Licence

© 2024 Guillaume Ste-Marie. Tous droits réservés.

---
*Dédié à la préservation de la vivacité des images par un traitement intelligent des couleurs*
