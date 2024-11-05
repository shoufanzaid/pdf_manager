__all__ = [
    "PDF_Manager",
    ]

import fitz
import re
import uuid

from PIL import Image
from pypdf import PdfWriter


class PDF_Manager(object):

    def __init__(
            self,
            path: str = None,
            ) -> None:
        self._pdfs = []
        if path is not None:
            self.add(files=path)

    def add(
            self,
            files: list|str = None,
            ):
        if files is not None:
            assert isinstance(files, list) or isinstance(files, str), "Must pass list or string."
            if isinstance(files, str):
                files = [files]
            files = [file + ".pdf" if file[-4:] != ".pdf" else file for file in files]
            for file in files:
                self._pdfs.append(PdfWriter(open(file, "rb")))
        return self

    def add_from_images(
            self,
            image_paths: list|str = None,
            ):
        # Read image contents
        images = [Image.open(image_path) for image_path in image_paths]

        # Save as PDF
        filename = str(uuid.uuid4()) + ".pdf"
        images[0].save(
            fp=filename,
            format="PDF",
            resolution=100.0,
            save_all=True,
            append_images=images[1:],
            )

        # Add and delete
        self.add(filename)
        # pathlib.Path.unlink(filename)  # Can't delete, it's protected...
        return self

    def split(
            self,
            PDFs: list|int = None,
            keep_others: bool = True,
            ):
        # Splits all pages of chosen PDFs
        # If PDFs is None, all PDFs are considered
        if PDFs is None:
            PDFs = [i for i in range(len(self._pdfs))]
        if isinstance(PDFs, int):
            PDFs = [PDFs]
        pdfs = []
        for i in range(len(self._pdfs)):
            if i not in PDFs:
                if keep_others:
                    pdfs.append(self._pdfs[i])
            else:
                for page in self._pdfs[i].pages:
                    writer = PdfWriter()
                    writer.add_page(page)
                    pdfs.append(writer)
        self._pdfs = pdfs
        return self

    def rotate(
            self,
            angle: int = 90,
            PDFs: list|int = None,
            keep_others: bool = True,
            ):
        # Rotates all pages of chosen PDFs by given angle in clockwise degrees
        # If PDFs is None, all PDFs are considered
        if PDFs is None:
            PDFs = [i for i in range(len(self._pdfs))]
        if isinstance(PDFs, int):
            PDFs = [PDFs]
        pdfs = []
        for i in range(len(self._pdfs)):
            if i not in PDFs:
                if keep_others:
                    pdfs.append(self._pdfs[i])
            else:
                writer = PdfWriter()
                for page in self._pdfs[i].pages:
                    writer.add_page(page.rotate(angle))
                pdfs.append(writer)
        self._pdfs = pdfs
        return self

    def shrink(
            self,
            quality: int = 10,
            PDFs: list|int = None,
            keep_others: bool = True,
            ):
        # Reduces quality of chosen PDFs
        # If PDFs is None, all PDFs are considered
        if PDFs is None:
            PDFs = [i for i in range(len(self._pdfs))]
        if isinstance(PDFs, int):
            PDFs = [PDFs]
        pdfs = []
        for i in range(len(self._pdfs)):
            if i not in PDFs:
                if keep_others:
                    pdfs.append(self._pdfs[i])
            else:
                writer = self._pdfs[i]
                for page in writer.pages:
                    for img in page.images:
                        img.replace(img.image, quality=quality)
                pdfs.append(writer)
        self._pdfs = pdfs
        return self

    @staticmethod
    def _content_search(
            lines: list,
            search: str,
            search_start: str = None,
            search_end: str = None,
            skip: list|str = None,
            skip_exact: bool = False,
            ):
        searching = False
        if not search_start:
            searching = True
        if skip and isinstance(skip, str):
            skip = [skip]
        for line in lines:
            if search_start and search_start in line:
                searching = True
            if not searching:
                continue
            if re.search(search, line):
                result = re.search(search, line).group()
                if skip is None:
                    yield result
                else:
                    if skip_exact:
                        if not any([element == result for element in skip]):
                            yield result
                    else:
                        if not any([element in result for element in skip]):
                            yield result
            if search_end and search_end in line:
                searching = False

    def hide_content(
            self,
            search: str,
            search_start: str = None,
            search_end: str = None,
            skip: list|str = None,
            skip_exact: bool = False,
            PDFs: list|int = None,
            keep_others: bool = True,
            ):
        # Hides content within chosen PDFs
        # If PDFs is None, all PDFs are considered
        if PDFs is None:
            PDFs = [i for i in range(len(self._pdfs))]
        if isinstance(PDFs, int):
            PDFs = [PDFs]
        pdfs = []
        for i in range(len(self._pdfs)):
            if i not in PDFs:
                if keep_others:
                    pdfs.append(self._pdfs[i])
            else:
                # Save temporary file and load it using fitz
                filename = str(uuid.uuid4()) + ".pdf"
                self._pdfs[i].write(filename)
                pdf = fitz.open(filename)
                # Hide content
                for page in pdf:
                    page.wrap_contents()
                    sensitive = PDF_Manager._content_search(
                        lines=page.get_text("text").split("\n"),
                        search=search,
                        search_start=search_start,
                        search_end=search_end,
                        skip=skip,
                        skip_exact=skip_exact,
                        )
                    for data in sensitive:
                        areas = page.search_for(data)
                        if areas:
                            [page.add_redact_annot(area, fill=(0, 0, 0)) for area in areas]
                    page.apply_redactions()
                # Finish
                pdf.saveIncr()
                pdfs.append(PdfWriter(open(filename, "rb")))
        self._pdfs = pdfs
        return self

    def merge(
            self,
            PDFs: list|int = None,
            ):
        # Merges chosen PDFs and drops others
        # If PDFs is None, all PDFs are considered
        if PDFs is None:
            PDFs = [i for i in range(len(self._pdfs))]
        if isinstance(PDFs, int):
            PDFs = [PDFs]
        merged = PdfWriter()
        for i in PDFs:
            for page in self._pdfs[i].pages:
                merged.add_page(page)
        self._pdfs = [merged]
        return self

    def keep(
            self,
            PDFs: list|int,
            ):
        # Keeps chosen PDFs and drops others
        pdfs = []
        if isinstance(PDFs, int):
            PDFs = [PDFs]
        for i in range(len(self._pdfs)):
            if i in PDFs:
                pdfs.append(self._pdfs[i])
        self._pdfs = pdfs
        return self

    def drop(
            self,
            PDFs: list|int,
            ):
        # Drops chosen PDFs and keeps others
        pdfs = []
        if isinstance(PDFs, int):
            PDFs = [PDFs]
        for i in range(len(self._pdfs)):
            if i not in PDFs:
                pdfs.append(self._pdfs[i])
        self._pdfs = pdfs
        return self

    def save(
            self,
            path: str = None,
            ):
        if path is None:
            path = "output.pdf"
        if path[-4:] != ".pdf":
            path += ".pdf"
        self.merge()._pdfs[0].write(path)
        return self
