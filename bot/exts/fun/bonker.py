from PIL import Image, ImageSequence

LARGE = (55, 55)
SMALL = (48, 48)

pfp = Image.open('pfp3.png')
pfps = [pfp.resize(LARGE), pfp.resize(SMALL)]

bonk_gif = Image.open('tenor.gif')
gif_dimensions = bonk_gif.size

white_bg = Image.new('RGBA', bonk_gif.size, 'WHITE')
out_images = []

for i, frame in enumerate(ImageSequence.Iterator(bonk_gif)):
    frame = frame.convert('RGBA')

    bg = white_bg.copy()
    bg.paste(frame, (0, 0), frame)

    frame = bg.convert('RGBA')

    if i == bonk_gif.n_frames - 1:
        frame.paste(pfps[1], (0, gif_dimensions[1] - SMALL[1]))
    else:
        frame.paste(pfps[0], (0, gif_dimensions[1] - LARGE[1]))
    out_images.append(frame)

out_images[0].save(
    'out.gif', 'GIF', save_all=True, append_images=out_images[1:], loop=0
)
