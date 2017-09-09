from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import click

CHARS = " .`-_':,;=/\"|)\\)ivxclrs{*}I?!][1taeo7zjLunT#JCwfy325Fp6mqSghVd4EgXPGZbYkOA&8U$@KHDBWNMR0QQ"

def lum_to_char(lum):
    """Map a luminosity value to a character."""
    return CHARS[int(lum // 2.86)]


def lum_matrix_by_point(image, fontsize, font, threshold=0):
    """Sample each point at font size dimensions and return matrix of lum values."""
    fnt = ImageFont.truetype('fonts/' + font + '.ttf', fontsize)
    fntsize = fnt.getsize("A")
    return [[image.getpixel((x, y)) if image.getpixel((x,y)) > threshold else 0
            for x in range(0, image.width, fntsize[0])]
            for y in range(0, image.height, fntsize[1])]

def compress_lum_matrix(lum_matrix, degree):
    return [[i - (i % degree) for i in row] for row in lum_matrix]

def reduce_flicker(lum_frames, amt):
    """Lower tolerance for changes in luminosity to reduce flickering between frames."""
    width = len(lum_frames[0][0])
    height = len(lum_frames[0])
    prev = lum_frames[0]
    for i in range(1, len(lum_frames)):
        current = lum_frames[i]
        for y in range(height):
            for x in range(width):
                clum = current[y][x]
                plum = prev[y][x]

                if abs(clum - plum) < amt:
                    current[y][x] = prev[y][x]

        prev = current



def lum_matrix_to_char_matrix(lum_matrix):
    """Convert luminecience matrix to char matrix."""
    return [[lum_to_char(lum) for lum in row] for row in lum_matrix]

def print_chars(char_matrix, image, fontsize, font):
    """Print a char array over an image."""
    # get a font
    fnt = ImageFont.truetype('fonts/' + font + '.ttf', fontsize)
    y = 0
    fntheight = fnt.getsize("A")[1]

    # get a drawing context
    d = ImageDraw.Draw(image)

    txt_rows = [''.join(row) for row in char_matrix]
    for txt_row in txt_rows:
        # draw text
        d.text((0, y), txt_row, font=fnt, fill=(0, 0, 0, 255))
        y += fntheight



def image_to_ascii(infile_name, outfile_name, font_size):
    """Convert a file to an ascii art file."""
    img = Image.open(infile_name)
    img = img.convert('L')

    outimg = Image.new('RGBA', img.size, (255, 255, 255))

    lums = lum_matrix_by_point(img, font_size, 'arial')
    char_matrix = lum_matrix_to_char_matrix(lums)

    print_chars(char_matrix, outimg, font_size, 'arial')

    outimg.save(outfile_name, 'PNG')


def process_sequence(folder_name, font_size, font, dejitter, threshold, ext='png'):
    """Convert a folder of images to a folder of ascii images."""

    print "BEEP BEEP BOOP PROCESSING FOLDER " + folder_name

    out_folder = folder_name + '_out'
    from os import listdir, path, makedirs

    filenames = listdir(folder_name)

    imgs = [name for name in filenames if name[-len(ext):] == ext]
    print "{0} frames to process".format(len(imgs))

    # Create output folder
    if path.exists(out_folder):
        import shutil
        shutil.rmtree(out_folder)

    makedirs(out_folder)

    print "Opening files."
    imgfiles = [Image.open(folder_name + '/' + img) for img in imgs]
    if len(imgfiles) == 0:
        print """
        Could not find any images with extension '.{0}' in folder '{1}'
        """.format(ext, folder_name)
        return


    print "Converting to BnW"
    bwimgs = [img.convert('L') for img in imgfiles]

    print "Converting to lum matrices."
    lum_matrices = [lum_matrix_by_point(bwimg, font_size, font, threshold)
                    for bwimg in bwimgs]

    print "De-jittering lum matrices."
    if dejitter > 0:
        lum_matrices = [compress_lum_matrix(matrix, dejitter) for matrix in lum_matrices]

    print "Converting to char matrices."
    char_matrices = [lum_matrix_to_char_matrix(lum) for lum in lum_matrices]

    print "Writing imgs"
    for index, img in enumerate(imgs):
        if index % 50 == 0:
            print "on #" + str(index)
        outimg = Image.new('RGBA', bwimgs[index].size, (0, 0, 0, 0))
        print_chars(char_matrices[index], outimg, font_size, font)

        outpath = out_folder + '/' + img
        outimg.save(outpath, 'PNG')




# TODO: Enable print char matrix regradless of font size, use 'threshold' argument
# in lum_matrix_by_point instead of lum_matrix_to_char_matrix, lum_to_char.

@click.command()
@click.option('--infile', default='')
@click.option('--fontsize')
@click.option('--ext')
@click.option('--dejitter')
@click.option('--threshold')
@click.option('--font')
def process(infile, fontsize, font, dejitter, threshold, ext):
    from settings import settings
    if fontsize is None:
        fontsize = settings['fontsize']
    else:
        fontsize = int(fontsize)
    if font is None:
        font = settings['font']
    if dejitter is None:
        dejitter = settings['dejitter']
    else:
        dejitter = int(dejitter)
    if threshold is None:
        threshold = settings['threshold']
    else:
        threshold = int(threshold)
    if ext is None:
        ext = settings['ext']

    process_sequence(infile, fontsize, font, dejitter, threshold, ext)


if __name__ == '__main__':
    process()
