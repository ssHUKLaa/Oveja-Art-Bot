import os, cv2, wand.image, numpy as np
from PIL import Image
import math


foldername=""
def imagesfromfolder(foldername):
    for filename in os.listdir(foldername):
        img = cv2.imread(os.path.join(foldername, filename))
        imagestoeventpic(img)

def imagefromcropping(image, name):
    return imagestoeventpic(image, name)

def imagestoeventpic(image,name):
    image= cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    height, width = image.shape[:2]
    
    center = (width // 2, height // 2)
    print(image.shape)
    
    rotation = cv2.getRotationMatrix2D(center,6,1.0)
    angrad = math.radians(6)
    sinang = abs(math.sin(angrad))
    cosang = abs(math.cos(angrad))
    newwidth = int(width *cosang + height * sinang)
    newheight = int(height * cosang + width * sinang)
    dx = (newwidth - width) // 2
    dy = (newheight - height) // 2
    rotation[0, 2] += dx
    rotation[1, 2] += dy
    tes=np.zeros((newheight,newwidth,4),np.uint8)
    res=cv2.warpAffine(image,rotation, (newwidth,newheight),tes,flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_TRANSPARENT)

   
    #image= Image.fromarray(image)
    #image=image.rotate(angle=6,expand=True, resample=Image.BICUBIC)
    card=cv2.imread('_Counter_Clockwise_Event_Pic_Frame.png',-1)
    transparent_image = np.zeros((card.shape[0], card.shape[1], 4), dtype=np.uint8)

    card_alpha = card[:,:,3]
    mask = card_alpha >0


    xoff=13
    yoff=13
    xend=xoff+res.shape[1]
    yend=yoff+res.shape[0]

    transparent_image[yoff:yend,xoff:xend]=res

    transparent_alpha = transparent_image[:, :, 3]
    opaque_mask = card_alpha == 255

    result_image = transparent_image.copy()
    blending_factor = 1
    for c in range(3):  # Iterate over color channels (R, G, B)
        result_image[:, :, c] = (
            (1 - card_alpha / 255.0) * transparent_image[:, :, c] +
            (card_alpha / 255.0) * blending_factor * card[:, :, c]
        )
    result_image[:, :, 3] = np.maximum(card_alpha, transparent_alpha)
    result_image[:, :, 3] = np.clip(result_image[:, :, 3], 0, 255).astype(np.uint8)
    
    #result_image=cv2.cvtColor(result_image,cv2.COLOR_BGRA2RGBA)
    resname=[]
    resname.append(result_image)
    resname.append(name)
    return resname
    '''
    result2dds= wand.image.Image.from_array(result_image)
    result2dds.alpha_channel=True
    result2dds.format='dds'
    result2dds.compression='no'
    result2dds.save(filename=f'finalimages/report_event_MEX_{count}.dds')
    '''
    

    

    






