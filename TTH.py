import pygame
from random import randint

def crop(img):
    """
    crop(img): crops an image at the center of a black subject\n
    img : image to be cropped\n
    returns cropped image
    """
    xl = img.get_width()
    xr = 0
    yt = img.get_height()
    yb = 0
    for y in range(img.get_height()):
        for x in range(img.get_width()):
            c = img.get_at((x,y))
            if c[0] < 150 and c[1] < 150 and c[2] < 150:
                if x < xl: xl = x
                if x > xr: xr = x
                if y < yt: yt = y
                if y > yb: yb = y
        
    w = xr - xl + 1
    h = yb - yt + 1

    #print(w,h, img.get_size(), (xr,xl,yt,yb))

    new = pygame.Surface((w,h))
    new.blit(img, (-xl,-yt))

    return new

def generateFourm(letters):
    """
    generateFourm(letters) : generates a fourm with a list of letters\n
    letters : list of lettersn
    returns number of rows used
    """
    f = pygame.font.SysFont("", 40, True)

    l = len(letters)
    r = l/12

    if r > int(r):
        r = int(r) + 1


    out = pygame.Surface((12*256, r*320))
    out.fill((255,255,255))

    x = 0
    y = 0
    letter = 0
    for row in range(r):
        for column in range(12):
            #print(letter)
            t = f.render(letters[letter], True, (0,0,0))
            out.blit(t, (x+128-(t.get_width()/2),y + 32 - (t.get_height()/2)))
            letter += 1

            if letter == l: break

            x += 256
        y += 320
        x = 0

    for column in range(11):
        pygame.draw.line(out, (0,0,0), ((column+1)*256, 0), ((column+1)*256, out.get_height()), 3)

    s = 64
    for row in range(r-1):
        pygame.draw.line(out, (0,0,0), (0, (row+1)*320), (out.get_width(), (row+1)*320), 3)

        #print(s)

        pygame.draw.line(out, (0,0,0), (0, s), (out.get_width(), s), 3)
        s += 320
        pygame.draw.line(out, (0,0,0), (0, s), (out.get_width(), s), 3)
    
    pygame.image.save(out, "images/fourm.png")

    return r


            
def readFourm(letters, fourm, out, numRows):
    """
    readFourm(letters, fourm, out, numRows): reads a fourm image and saves it as letter images\n
    letters : a list of characters to read for\n
    out : the output folder for the images\n
    numRows : the number of rows in the fourm\n
    """
    characters = ".?"
    alternate = ["dot", "question"]

    fourm = pygame.image.load(fourm)
    w,h = fourm.get_size()
    w = w /12
    h = h /(1.25*numRows)
    
    #print(w,h)

    x = 0
    y = h/4
    count = 1
    for letter in letters:
        s = pygame.Surface((w-8,h-8))
        s.blit(fourm, (-x - 4,-y - 4))



        if letter in characters:
            letter = alternate[characters.index(letter)]

        if letter.isupper():
            letter = "upper/" + letter
        pygame.image.save(s, out + "/" + letter + ".png")
        count += 1
        x += w
        if count > 12:
            count = 1
            x = 0
            y += h + h/4
        




#generateFourm(letters)
#readFourm(letters, "EvansFourm.png", "images/" + str(num), 6)

def loadImages(num, letters):
    """
    loadImages(num, letters) : loads all text images into a dictionary\n
    num : the file number to open\n
    letters : a list of letters and characters to search for
    """
    imgs = {}
    for letter in letters:
        s = ""
        if letter.isupper(): s = "upper/"

        cropped = pygame.image.load("images/" + str(num) + "/" + s + letter + ".png")
        print("images/" + str(num) + "/" + s + letter + ".png")
        cropped = crop(cropped)
        imgs[letter] = cropped
        pygame.image.save(cropped, "images/" + str(num) + "/" + s + letter + ".png")

    
    space = pygame.Surface((30,5))
    space.fill((255,255,255))

    imgs[" "] = space

    return imgs


def parseFile(path):
    """
    parseFile(): parses a text file into a list of string\n
    name : str containing the file name\n
    returns list of string
    """
    f = open(path, "r")
    lines = f.readlines()
    f.close()

    text = []
    for line in lines:
        line = line.rstrip()
        text.append(line)
    
    return text

def renderHandWriting(text, imgs, modifier=0):
    """
    renderHandWriting(text, imgs, modifier=0) : renders text into handwritten\n
    text : list of strings\n
    modifier : multiplier for random height variarion\n
    returns Surface of handwriting
    """

    out = []
    for s in text:
        w = 0
        h = 0
        for letter in s: #get width and height nessecary
            if letter == ".":
                letter = "dot"
            if letter == "?":
                letter = "question"
                
            if letter in letters or letter in [".", "?", " "]:
                w1,h1 = imgs[letter].get_size()
                w += w1 + 5
                if h1 > h: h = h1
            else:
                print("not allowed:" , letter)

        wordP = pygame.Surface((w,h+40), pygame.SRCALPHA)
        wordP.fill((255,0,255, 0))
        x = 0
        for letter in s: #add letter images to line

            if letter == ".":
                letter = "dot"
            if letter == "?":
                letter = "question"
            if letter in letters or letter in [".", "?", " "]:
                y = h/2 - imgs[letter].get_height()/2
                r = randint(0,15) * ((randint(0,1)*2)-1) * modifier
                if letter == "dot":
                    y = wordP.get_height()/2 + 25
                    r = randint(0,5) * ((randint(0,1)*2)-1) * modifier


                
                y += r

                wordP.blit(imgs[letter], (x+5, y))
                x += imgs[letter].get_width() + 5
            else:
                print("not allowed:" , letter)
        out.append(wordP)

    w,h = 0,0
    for img in out: #add all lines into big image
        w1,h1 = img.get_size()

        if w1 > w: w= w1
        h += h1

    final = pygame.Surface((w,h))
    final.fill((255,255,255))

    y = 0
    for img in out:
        final.blit(img, (0,y))
        y += img.get_height()

    return final


if "__main__" in __name__:
    pygame.init()

    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    chars = ["question", "dot"]

    temp = []
    for l in letters:
        temp.append(l)
    temp += chars
    letters = temp

    num = 0

    #generateFourm(letters)
    #readFourm(letters, "EthanFourm.png", "images/0",  6)

    text = parseFile("input.txt")
    imgs = loadImages(num, letters)
    final = renderHandWriting(text, imgs)


    pygame.image.save(final, "images/out.png")


