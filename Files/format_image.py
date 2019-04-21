from PIL import Image

for block in ['A','B','C','D','E']:
    for num in range(1,13):
        im = Image.open("Images_orig/Block_{}/test-raven-{} {}.png".format(block,block,num))
        rgb_im = im.convert('RGB')
        pixels = rgb_im.load()
        x, y = rgb_im.size
        if block == 'A' or block == 'B':
            first_rect = (0, 0, 340, 220)
            second_rect = (0, 220, 429, 439)
        else:
            first_rect = (0, 0, 300, 250)
            second_rect = (0, 250, 474, 439)
        first_place = rgb_im.crop(first_rect)
        second_place = rgb_im.crop(second_rect)
        background = Image.new('RGB', (1400, 360), (255, 255, 255))
        background.paste(first_place, (300, 90))
        background.paste(second_place, (650, 90))
        background.save('Images/Block_{}/test-raven-{} {}.jpg'.format(block,block,num))

