from os import listdir, path, makedirs
import types
import csv
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import click

CHARS = None
with open('chars.txt', 'r') as charstxt:
    for line in charstxt:
        if line[0] == '#':
            continue
        else:
            CHARS = line.rstrip()
            break

if CHARS is None:
    print "chars.txt is messed up..."
    quit()

MIN_CHAR = 0
MAX_CHAR = len(CHARS) - 1



def lum_to_char(lum):
    """Map a luminosity value to a character."""
    # REF: https://stackoverflow.com/questions/345187/math-mapping-numbers
    charidx = int(lum/255.0 * MAX_CHAR)
    return CHARS[charidx]


def lum_matrix_by_point(image, fontsize, font, threshold=0):
    """Sample each point at font size dimensions and return matrix of lum values."""
    fnt = ImageFont.truetype('fonts/' + font + '.ttf', fontsize)
    fntsize = fnt.getsize("A")
    return [[image.getpixel((x, y)) if image.getpixel((x,y)) > threshold else 0
            for x in range(0, image.width, fntsize[0])]
            for y in range(0, image.height, fntsize[1])]

def color_matrix_by_point(image, fontsize, font):
    """Sample each point at font size dimensions and return matrix of lum values."""
    fnt = ImageFont.truetype('fonts/' + font + '.ttf', fontsize)
    fntsize = fnt.getsize("A")
    return [[image.getpixel((x, y)) for x in range(0, image.width, fntsize[0])]
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

def print_chars(char_matrix, image, fontsize, font, color_matrix=None):
    """Print a char array over an image."""
    # get a font
    fnt = ImageFont.truetype('fonts/' + font + '.ttf', fontsize)
    y = 0

    fntsize = fnt.getsize("A")
    fntheight = fntsize[1]
    fntwidth = fntsize[0]

    imgheight = image.size[1]
    imgwidth = image.size[0]

    x = 0
    y = 0

    # get a drawing context
    d = ImageDraw.Draw(image)

    for rownum, row in enumerate(char_matrix):
        for charnum, char in enumerate(row):
            rgba = (0,0,0,255)
            if color_matrix is not None:
                rgb = color_matrix[rownum][charnum]
                rgba = (rgb[0], rgb[1], rgb[2], 255)

            d.text((x,y), char, font=fnt, fill=rgba)
            x += fntwidth
        x = 0
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


def process_sequence(infile, outfile, font_size, font, reduceflicker, threshold, ext='png', nocolor=False):
    """Convert a video file to a folder of images and convert those imges to a folder of ascii images."""    
    print "BEEP BEEP BOOP PROCESSING file " + infile

    temp_folder = infile.split('.')[0] + '_temp'

    out_folder = outfile if outfile is not None else infile.split('.')[0] + '_out'
    mkdir(temp_folder)
    mkdir(out_folder)

    print "Converting video to img sequence..."
    run('ffmpeg -i ' + infile + ' ' + temp_folder + '/0%3d.png')

    filenames = listdir(temp_folder)

    # Just get files with our chosen extension
    imgs = [name for name in filenames if name[-len(ext):] == ext]
    print "{0} frames to process".format(len(imgs))

    print "Opening files."
    imgfiles = [Image.open(temp_folder + '/' + img) for img in imgs]
    if len(imgfiles) == 0:
        print """
        Could not find any images with extension '.{0}' in folder '{1}'
        """.format(ext, temp_folder)
        return

    # Determine if we are using static params or dynamic ones
    if isinstance(font_size, int):
        font_sizes = [font_size] * len(imgfiles)
    else:
        font_sizes = font_size

    

    color_matrices = None
    if not nocolor:
        print "Sampling colors..."
        color_matrices = [color_matrix_by_point(imgfiles[i], 
                                                font_sizes[i%len(font_sizes)], 
                                                font)
                          for i in range(len(imgfiles))]


    print "Converting to BnW"
    bwimgs = [img.convert('L') for img in imgfiles]

    print "Converting to lum matrices."
    lum_matrices = [lum_matrix_by_point(bwimgs[i], font_sizes[i%len(font_sizes)], font, threshold)
                    for i in range(len(bwimgs))]

    
    print "De-jittering lum matrices."
    if reduceflicker > 0:
        lum_matrices = [compress_lum_matrix(matrix, reduceflicker) for matrix in lum_matrices]

    print "Converting to char matrices."
    char_matrices = [lum_matrix_to_char_matrix(lum) for lum in lum_matrices]

    print "Writing imgs"
    for index, img in enumerate(imgs):
        if index % 50 == 0:
            print "on #" + str(index)
        outimg = Image.new('RGBA', bwimgs[index].size, (0, 0, 0, 0))
        color_matrix = (color_matrices[index]
                        if color_matrices is not None else None)
        print_chars(char_matrices[index],
                    outimg,
                    font_sizes[index % len(font_sizes)],
                    font,
                    color_matrix)

        outpath = out_folder + '/' + img.split('.')[0] + '.png'
        outimg.save(outpath, 'PNG')

    print "Cleaning up..."
    rmdir(temp_folder)
    # rmdir(out_folder)


def run(command):
    """Execute a bash command."""
    from subprocess import Popen, PIPE
    commands = command.split(' ')
    process = Popen(commands, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return (stdout, stderr)

def rmdir(folder_name):
    """Remove a dir."""
    if path.exists(folder_name):
        import shutil
        shutil.rmtree(folder_name)

def mkdir(folder_name):
    """Overwrite dir."""
    rmdir(folder_name)
    makedirs(folder_name)

def prep_keyframes(infile):
    fileparts = infile.split('.')
    filename = fileparts[0]
    print "INFILE ARG WAS " + infile
    print "FILE NAME IS " + filename
    ext = fileparts[1]
    # result = run('ascii/bash/keyframes.sh %s %s %s' % (infile, filename, ext))
    # print result
    frame_count, _ = run('ascii/bash/framecount.sh ' + infile)
    frame_count = int(frame_count)
    with open(filename + '_keyframes.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['frame #', 'font_size'])
        for i in range(frame_count):
            writer.writerow([i, ''])
        writer.writerow(['FIN', ''])
    print "Done!"

# BOOOOOKMARRRRRK
def maybe_read_keyframes(infile):
    pathparts = infile.split('/')
    path = '/'.join(pathparts[0:-1])
    filename = pathparts[-1]
    filename = filename.split('.')[0]
    files = listdir(path)
    keyframefile = None
    for name in files:
        if name == filename + '_keyframes.csv':
            keyframefile = name
            break
    if keyframefile is None:
        return None

    font_sizes = None
    with open(path + '/' + keyframefile) as ifile:
        reader = csv.DictReader(ifile)
        font_sizes = [int(row['font_size'] if row['font_size'] else 0)
                      for row in reader]

    return font_sizes





@click.command()
@click.option('--infile', default='',
help="""
Name of folder containing image sequence to be processed. REQUIRED.
""")
@click.option('--outfile',
help="""
Name of output folder. Default: 'infile + _out'
""")
@click.option('--fontsize', type=int,
help="""
Size of letters. Default: 15
""")
@click.option('--ext',
help="""
Extension of input image files (for distinguishing between input images and
other extraneous files). Default: 'jpg'
""")
@click.option('--reduceflicker', type=int,
help="""
Amount (0-255) by which to reduce rapid flickering between characters. Default: 0
""")
@click.option('--threshold', type=int,
help="""
Luminescience (sp?) threshold. Pixels below this threshold are compressed to 0.
""")
@click.option('--font',
help="""
Name of .ttf file in /fonts to use. Must be a monospaced font, case-sensitive.
(Do not include the extension, just the name).
""")
@click.option('--nocolor', is_flag=True,
help="""
Ignore color.
""")
@click.option('--keyframes', is_flag=True,
help="""
Perform keyframe prep. Outputs infile_keyframes.csv in same directory as infile.
""")
def process(infile, outfile, fontsize, font, reduceflicker, threshold, ext, nocolor, keyframes):
    from settings import settings
    if fontsize is None:
        fontsize = settings['fontsize']
    if font is None:
        font = settings['font']
    if reduceflicker is None:
        reduceflicker = settings['reduceflicker']
    if threshold is None:
        threshold = settings['threshold']
    if ext is None:
        ext = settings['ext']

    # Look for a keyframe csv, and if we find it, set font_size to array of values read from csv
    fontsizes = maybe_read_keyframes(infile)
    fontsize = fontsizes if fontsizes is not None else fontsize

    if keyframes:
        prep_keyframes(infile)
    else:
        process_sequence(infile,
                         outfile,
                         fontsize,
                         font,
                         reduceflicker,
                         threshold,
                         ext,
                         nocolor)


if __name__ == '__main__':
    process()

