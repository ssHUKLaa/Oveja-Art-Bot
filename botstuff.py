import os

import discord 
import cv2
import numpy as np
import wand.image
import io
import math,zipfile
from imgtocroppedfaces import startalg
import asyncio

from dotenv import load_dotenv
from gfxshinify import submitloc, implementloc, switchbranch, pushtobranch

class MyClient(discord.Client):
    
    
    async def on_ready(self):
        
        for guild in client.guilds:
            if guild.id == GUILD:
                break

        print(f'{client.user} conn')
        print(f'{guild.name}')
    async def on_message(self,message):
        if message.author == client.user:
            return 
        
        if message.content.startswith('$evpic'):
            tes = message.content.split()
            tes.pop(0)
            files_to_send: list[discord.File] = []
            if message.attachments:
                teslist = []
                namelist= []
                
                count=0
                for i in message.attachments:
                    first_attachment = i
        
                    # Read attachment data into memory
                    attachment_bytes = await first_attachment.read()
                    
                    # Convert attachment data into a numpy array
                    nparr = np.frombuffer(attachment_bytes, np.uint8)
                    
                    # Load and display the image using cv2.imshow()
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    teslist.append(image)
                    namelist.append(tes[count])
                    count+=1
                
                newimgs = startalg(teslist, namelist)
                for i in newimgs:
                    temp = cv2.cvtColor(i[0],cv2.COLOR_BGRA2RGBA)
                    result2dds= wand.image.Image.from_array(temp)
                    result2dds.alpha_channel=True
                    result2dds.format='dds'
                    result2dds.compression='no'
                    ddsblob = result2dds.make_blob()
                    _, encoded_image = cv2.imencode(".png", i[0])

                    dds_file = discord.File(io.BytesIO(ddsblob), filename=f'{i[1]}.dds')
                    
                    reencoded_file = discord.File(io.BytesIO(encoded_image), filename=f'{i[1]}.png')
                    files_to_send.append(reencoded_file)
                    files_to_send.append(dds_file)
                
                await message.reply(files=files_to_send)
        if message.content.startswith('$dds'):
            files_to_send: list[discord.File] = []
            if message.attachments:
                tes = message.content.split()
                tes.pop(0)
                count=0
                for i in message.attachments:
                    first_attachment = i
                    attachment_bytes = await first_attachment.read()
                    nparr = np.frombuffer(attachment_bytes, np.uint8)
                    
                    # Load and display the image using cv2.imshow()
                    image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                    

                    temp = cv2.cvtColor(image,cv2.COLOR_BGRA2RGBA)
                    
                    result2dds= wand.image.Image.from_array(temp)
                    result2dds.alpha_channel=True
                    result2dds.format='dds'
                    result2dds.compression='no'
                    ddsblob = result2dds.make_blob()
                    filename=i.filename
                    filename, sep, tail = filename.partition('.')
                    dds_file=''
                    if tes:
                        dds_file = discord.File(io.BytesIO(ddsblob), filename=f'{tes[count]}.dds')
                    else:
                        dds_file = discord.File(io.BytesIO(ddsblob), filename=f'{filename}.dds')
                    files_to_send.append(dds_file)
                    count+=1
                await message.reply(files=files_to_send)
        elif message.content.startswith('$loc'):
            swag = message.content.split()
            swag.pop(0)
            branch= swag[0]
            namespace = swag[1]
            links=[]
            i=2
            while i<len(swag):
                links.append(swag[i])
                i+=1
            switchbranch(branch)
            loclist=[]
            for link in links:
                loclist.append(submitloc(link))
            implementloc(namespace,loclist)
            pushtobranch(branch)
            
            
        elif message.content.startswith('$noshitposts'):
            
            card=cv2.imread('dontshitpost.jpg')
            _, path = cv2.imencode(".jpg", card)
            discord_file = []
            # Open the image file and create a discord.File
            discord_file.append(discord.File(io.BytesIO(path),filename="noshitposting.jpg"))
            await message.reply(files=discord_file)

        elif message.content.startswith('$portrait'):
            files_to_send: list[discord.File] = []
            card=cv2.imread('ministerframe.png',-1)
            #7px W 6px H
            swag = message.content.split()
            swag.pop(0)
            count=0
            for i in message.attachments:
                attachment_bytes = await i.read()
                nparr = np.frombuffer(attachment_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                image = cv2.cvtColor(image,cv2.COLOR_RGB2RGBA)
                resizedimg = cv2.resize(image, (36, 50), cv2.INTER_AREA)
                flippedimg= cv2.flip(resizedimg,1)
                height, width = resizedimg.shape[:2]
                center = (width // 2, height // 2)

                swagimage = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                    

                swagtemp = cv2.cvtColor(swagimage,cv2.COLOR_BGRA2RGBA)
                
                swagresult2dds= wand.image.Image.from_array(swagtemp)
                swagresult2dds.alpha_channel=True
                swagresult2dds.format='dds'
                swagresult2dds.compression='no'
                swagddsblob = swagresult2dds.make_blob()
                
                rotation = cv2.getRotationMatrix2D(center,6,1.0)
                angrad = math.radians(-4)
                sinang = abs(math.sin(angrad))
                cosang = abs(math.cos(angrad))
                newwidth = int(width *cosang + height * sinang)
                newheight = int(height * cosang + width * sinang)
                dx = (newwidth - width) // 2
                dy = (newheight - height) // 2
                rotation[0, 2] += dx
                rotation[1, 2] += dy
                
                tes=np.zeros((newheight,newwidth,4),np.uint8)
                tes2=np.zeros((newheight,newwidth,4),np.uint8)
                res=cv2.warpAffine(resizedimg,rotation, (newwidth,newheight),tes,flags=cv2.INTER_AREA, borderMode=cv2.BORDER_TRANSPARENT)
                res2=cv2.warpAffine(flippedimg,rotation, (newwidth,newheight),tes2,flags=cv2.INTER_AREA, borderMode=cv2.BORDER_TRANSPARENT)

                transparent_image = np.zeros((card.shape[0], card.shape[1], 4), dtype=np.uint8)
                transparent_image_2 = np.zeros((card.shape[0], card.shape[1], 4), dtype=np.uint8)
                card_alpha = card[:,:,3]
                mask = card_alpha >0


                xoff=6
                yoff=5
                xend=xoff+res.shape[1]
                yend=yoff+res.shape[0]

                transparent_image[yoff:yend,xoff:xend]=res
                transparent_image_2[yoff:yend,xoff:xend]=res2
                transparent_alpha = transparent_image[:, :, 3]
                opaque_mask = card_alpha == 255

                result_image = transparent_image.copy()
                result_image_2 = transparent_image_2.copy()
                blending_factor = 1
                for c in range(3):  # Iterate over color channels (R, G, B)
                    result_image[:, :, c] = (
                        (1 - card_alpha / 255.0) * transparent_image[:, :, c] +
                        (card_alpha / 255.0) * blending_factor * card[:, :, c]
                    )
                result_image[:, :, 3] = np.maximum(card_alpha, transparent_alpha)
                result_image[:, :, 3] = np.clip(result_image[:, :, 3], 0, 255).astype(np.uint8)

                for c in range(3):  # Iterate over color channels (R, G, B)
                    result_image_2[:, :, c] = (
                        (1 - card_alpha / 255.0) * transparent_image_2[:, :, c] +
                        (card_alpha / 255.0) * blending_factor * card[:, :, c]
                    )
                result_image_2[:, :, 3] = np.maximum(card_alpha, transparent_alpha)
                result_image_2[:, :, 3] = np.clip(result_image_2[:, :, 3], 0, 255).astype(np.uint8)

                _, encoded_image = cv2.imencode(".png", result_image)
                temp = cv2.cvtColor(result_image,cv2.COLOR_BGRA2RGBA)
                temp2 = cv2.cvtColor(result_image_2,cv2.COLOR_BGRA2RGBA)
                result2dds= wand.image.Image.from_array(temp)
                result2dds.alpha_channel=True
                result2dds.format='dds'
                result2dds.compression='no'
                ddsblob = result2dds.make_blob()
                
                result2dds2= wand.image.Image.from_array(temp2)
                result2dds2.alpha_channel=True
                result2dds2.format='dds'
                result2dds2.compression='no'
                ddsblob2 = result2dds2.make_blob()

                filename=i.filename
                filename, sep, tail = filename.partition('.')
                dds_file=''
                if swag:
                    reencoded_file = discord.File(io.BytesIO(encoded_image), filename=f'{swag[count]}.png')
                    dds_file = discord.File(io.BytesIO(ddsblob), filename=f'{swag[count]}.dds')
                    dds_file_2 = discord.File(io.BytesIO(ddsblob2), filename=f'{swag[count]}_flipped.dds')
                    dds_file_3 = discord.File(io.BytesIO(swagddsblob), filename=f'{swag[count]}_original.dds')
                else:
                    reencoded_file = discord.File(io.BytesIO(encoded_image), filename=f'{filename}.png')
                    dds_file = discord.File(io.BytesIO(ddsblob), filename=f'{filename}.dds')
                    dds_file_2 = discord.File(io.BytesIO(ddsblob2), filename=f'{filename}_flipped.dds')
                    dds_file_3 = discord.File(io.BytesIO(swagddsblob), filename=f'{filename}_original.dds')
                filelist: list[discord.File] = []
                filelist.append(dds_file)
                filelist.append(dds_file_2)
                filelist.append(reencoded_file)
                filelist.append(dds_file_3)
                files_to_send.append(filelist)
                count+=1
            
            filessending = 0
            while filessending<len(files_to_send):
                outfiles: list[discord.File] = []
                outfiles.append(files_to_send[filessending])
                
                if filessending+1<len(files_to_send):
                    outfiles.append(files_to_send[filessending+1])
                    filessending+=1
                outfiles = [file for sublist in outfiles for file in sublist]
                await message.reply(files=outfiles)
                await asyncio.sleep(1)
                filessending+=1
                
    



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


intents=discord.Intents.default()
intents.message_content = True
intents.messages = True
client = MyClient(intents=intents)
client.run(TOKEN)