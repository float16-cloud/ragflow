#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import fitz

from .ocr import OCR
from .recognizer import Recognizer
from .layout_recognizer import LayoutRecognizer
from .table_structure_recognizer import TableStructureRecognizer


def init_in_out(args):
    from PIL import Image
    import os
    import traceback
    from api.utils.file_utils import traversal_files
    images = []
    outputs = []

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    def pdf_pages(fnm, zoomin=3):
        nonlocal outputs, images
        pdf = fitz.open(fnm)
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(zoomin, zoomin))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
            outputs.append(os.path.split(fnm)[-1] + f"_{page_num}.jpg")

    def images_and_outputs(fnm):
        nonlocal outputs, images
        if fnm.split(".")[-1].lower() == "pdf":
            pdf_pages(fnm)
            return
        try:
            images.append(Image.open(fnm))
            outputs.append(os.path.split(fnm)[-1])
        except Exception as e:
            traceback.print_exc()

    if os.path.isdir(args.inputs):
        for fnm in traversal_files(args.inputs):
            images_and_outputs(fnm)
    else:
        images_and_outputs(args.inputs)

    for i in range(len(outputs)): outputs[i] = os.path.join(args.output_dir, outputs[i])

    return images, outputs