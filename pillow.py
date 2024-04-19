from PIL import Image, ImageDraw, ImageFont
def get_wellcome(text):
    image = Image.open("media/7d_background.png")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("fonts/FFFFORWA.ttf", size=60)


    ascent, descent = font.getmetrics()

    font_width = font.getmask(text).getbbox()[2]
    font_height = font.getmask(text).getbbox()[3] + descent

    width = 1280
    height = 640

    new_width = (width - font_width) / 2
    new_height = (height - font_height) / 1.5
    draw.text((new_width, new_height), text, font=font, fill="#dbc5db")

    image.save("media/wellcome.png")
if __name__ == "__main__":
    get_wellcome("Wellcome, @capbanana")