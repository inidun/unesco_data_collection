from pdf2image import convert_from_path, convert_from_bytes
import os
import tempfile

#convert_from_path(pdf_path, dpi=200, output_folder=None, first_page=None, last_page=None, fmt='ppm', jpegopt=None, thread_count=1, userpw=None, use_cropbox=False, strict=False, transparent=False, single_file=False, output_file=str(uuid.uuid4()), poppler_path=None, grayscale=False, size=None, paths_only=False, use_pdftocairo=False, timeout=600)

filename = './data/012656engo.pdf'
basename  = os.path.basename(filename).split('.')[0]
images_from_path = convert_from_path(filename, dpi=200, fmt='tiff', output_file=basename, output_folder='./data')
    # Do something here