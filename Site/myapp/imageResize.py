from PIL import Image, ImageFilter
from typing import Tuple

def resize(img: Image, size: Tuple[int, int]=(776, 344), blur_radius=6):
    """Return `PIL.Image` of given :attr:`size` (default 1000x700) with bluring background"""
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

# site = Path(__file__).parent
# for i in (site / 'imagesNotResized').iterdir():
#     for img in i.iterdir():
#         with open(img, 'rb') as bts:
#             image = resize(bts, (776, 344))
#             image.save(site / f'images/{i.name}/{img.name}')

