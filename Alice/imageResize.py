from PIL import Image, ImageFilter
from io import BytesIO

def resize(image: BytesIO, size: tuple[int, int], blur_radius=4) -> Image:
    img = Image.open(image)
    imgW, imgH = img.size
    targetW, targetH = size

    imgMult = min(targetW / imgW, targetH / imgH)
    backgroundMult = max(targetW / imgW, targetH / imgH)

    result = img.resize(map(round, (imgW * backgroundMult, imgH * backgroundMult)))
    resultW, resultH = result.size
    left, upper = round((resultW - targetW) / 2), round((resultH - targetH) / 2)

    result = result.crop((left, upper, left + targetW, upper + targetH))
    result = result.filter(ImageFilter.GaussianBlur(blur_radius))
    resultW, resultH = result.size

    img = img.resize(map(round, (imgW * imgMult, imgH * imgMult)))
    imgW, imgH = img.size
    offset = round((resultW - imgW) / 2), round((resultH - imgH) / 2)
    
    result.paste(img, offset)
    return result

with open(r"Z:\Картинки\Beluga.jpg", 'rb') as file:
    resize(BytesIO(file.read()), (1000, 700)).show()