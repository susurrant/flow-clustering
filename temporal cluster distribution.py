# -*- coding: utf-8 -*-：

from PIL import Image, ImageDraw, ImageFont
import math

def arrowCo(draw, x, y, lenth, direction = 'e'):
    if direction == 'e':
        dx = int(round(lenth * math.cos(math.pi / 6.0)))
        dy = int(round(lenth * math.sin(math.pi / 6.0)))
        return x-dx, y-dy, x, y, x-dx, y+dy
    elif direction == 'n':
        dy = int(round(lenth * math.cos(math.pi / 6.0)))
        dx = int(round(lenth * math.sin(math.pi / 6.0)))
        return x-dx, y+dy, x, y, x+dx, y+dy


def f(fileName):
    image = Image.new('RGB', (600, 400), '#ffffff')
    draw = ImageDraw.Draw(image)
    draw.line((40, 360, 580, 360), width=1, fill='#000000')
    draw.line((40, 360, 40, 20), width=1, fill='#000000')
    ac = arrowCo(draw, 580, 360, 10, 'e')
    draw.line(ac, fill='#000000', width=1)
    ac = arrowCo(draw, 40, 20, 10, 'n')
    draw.line(ac, fill='#000000', width=1)

    xlen = 540
    ylen = 340

    with open(fileName, 'r') as f:
        lines = f.readlines()
        del lines[0]
        for line in lines:
            sl = line.strip().split(',')
            x1 = int(round(40 + float(sl[1])*xlen/1440))
            x2 = int(round(40 + float(sl[2])*xlen/1440))
            y = int(round(20 + ylen - float(sl[3])*ylen/73))

            draw.line((x1,y,x2,y), fill='#000000', width=2)
            #ac = arrowCo(draw, x2, y, 10, 'e')
            #draw.line(ac, fill='#000000', width=2)
    iquality = 1000
    idpi = (800,800)
    image.save('tempdraw.jpg', quality=iquality, dpi=idpi)


if __name__ == '__main__':
    f('new_st_c(May 13) 25 0.25 c318 0.5.csv')