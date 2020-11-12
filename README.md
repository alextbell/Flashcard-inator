# cardify

## introduction

**cardify** automatically generates text-occluded image flash cards compatible with [Anki](https://apps.ankiweb.net/) flashcard software.
**cardify** utilizes the [EAST neural network](https://arxiv.org/abs/1704.03155) to identify characters on images, and then **cardify** determines which groups of characters are "text labels" for the image provided. **cardify** redacts every detected label and generates a flashcard for each one. Each flashcard is then automatically filed into an Anki deck that you generate. **cardify's** user interface was developed using the [PyQT5](https://pypi.org/project/PyQt5/) Python package. 

## using cardify

1. Upload an image to **cardify**.

![cardify_homepage](https://user-images.githubusercontent.com/64336024/98883086-c32c0d00-245b-11eb-9c35-3fd386e3153e.png)

2. Choose a deck title, and begin uploading images to be added to your deck. Uploaded images will appear distorted in the **cardify** previewer.
![cardify_eyeball](https://user-images.githubusercontent.com/64336024/98883590-6bda6c80-245c-11eb-9a9d-e27397f28012.png)

3. When finished adding images, generate your deck. Once you press "Make My Anki Deck", Anki will automatically open with your new deck.

![cards_added](https://user-images.githubusercontent.com/64336024/98884025-31250400-245d-11eb-842d-2dd3746831c4.png)

4. Check out your deck in Anki.

![anki_menu](https://user-images.githubusercontent.com/64336024/98884172-7b0dea00-245d-11eb-8bf8-2cf1ba568d61.png)

5. Happy studying!

![eyeball_deck](https://user-images.githubusercontent.com/64336024/98884246-98db4f00-245d-11eb-9965-e3da35b849b2.png)

![eyeball_practice_1](https://user-images.githubusercontent.com/64336024/98884363-d213bf00-245d-11eb-937a-0b03a28ec856.png)

![eyeball_practice_2](https://user-images.githubusercontent.com/64336024/98884345-c45e3980-245d-11eb-82a7-928be53a9800.png)



## Notes

* **cardify** is still a work in progress. The greatest limitation is the optical character detection algorithm. It works well enough for some images, but not well enough for me to use this over the manual cloze deletion package on Anki. 
* **cardify** does not yet have a hide one vs. hide all option. This is another advantage of manual cloze deletion over **cardify**. 
