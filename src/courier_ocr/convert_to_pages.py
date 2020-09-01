import os
#import tempfile
import pathlib

import click
from pdf2image import convert_from_bytes, convert_from_path

DATA_FOLDER = './data'

#convert_from_path(pdf_path, dpi=200, output_folder=None, first_page=None, last_page=None, fmt='ppm', jpegopt=None, thread_count=1, userpw=None, use_cropbox=False, strict=False, transparent=False, single_file=False, output_file=str(uuid.uuid4()), poppler_path=None, grayscale=False, size=None, paths_only=False, use_pdftocairo=False, timeout=600)


@click.command()
@click.argument('filename')
@click.option('--dpi', default=200, help='dpi', type=int)
@click.option('--first_page', '-f', default=None, help='First page', type=int)
@click.option('--last_page', '-l', default=None, help='Last page', type=int)
@click.option('--fmt', default='tiff', help='Output format', type=str)
def convert(filename, dpi, first_page, last_page, fmt):

    basename = os.path.basename(filename).split('.')[0]
    output_folder = os.path.join(DATA_FOLDER, basename, fmt)

    path = pathlib.Path(output_folder)
    path.mkdir(parents=True, exist_ok=True)

    images_from_path = convert_from_path(
        filename,
        dpi=dpi,
        first_page=first_page,
        last_page=last_page,
        fmt=fmt,
        output_file=basename,
        output_folder=output_folder
    )

    # Do something here


if __name__ == '__main__':
    convert()
