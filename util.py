import os
from http.client import HTTPException
from io import BytesIO

import fitz
from pymupdf import TEXT_PRESERVE_LIGATURES, TEXT_PRESERVE_WHITESPACE, TEXT_INHIBIT_SPACES

from fitzcli import get_list, page_simple, page_blocksort, page_layout

ALLOWED_EXTENSIONS = {'pdf'}

class Model(object):
    pass

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def open_file(stream, password, pdf=True):
    """Open and authenticate a document."""
    doc = fitz.Document(stream=stream)
    if not doc.is_pdf and pdf is True:
        raise Exception('Document must be PDF')
    if not doc.needs_pass:
        return doc
    if password or password == '':
        rc = doc.authenticate(password)
        if not rc:
            raise Exception('authentication unsuccessful')
    else:
        raise Exception("'%s' requires a password" % doc.name)
    return doc

def gettext(args) -> BytesIO:
    try:

        doc = open_file(args.stream, args.password, pdf=False)
        pagel = get_list(args.pages, doc.page_count + 1)
        textout = BytesIO()
        flags = TEXT_PRESERVE_LIGATURES | TEXT_PRESERVE_WHITESPACE
        if args.convert_white:
            flags ^= TEXT_PRESERVE_WHITESPACE
        if args.noligatures:
            flags ^= TEXT_PRESERVE_LIGATURES
        if args.extra_spaces:
            flags ^= TEXT_INHIBIT_SPACES
        func = {
            "simple": page_simple,
            "blocks": page_blocksort,
            "layout": page_layout,
        }
        for pno in pagel:
            page = doc[pno - 1]
            func[args.mode](
                page,
                textout,
                args.grid,
                args.fontsize,
                args.noformfeed,
                args.skip_empty,
                flags=flags,
            )
        textout.seek(0)
        return textout

    except SystemExit as e:
        raise Exception(e)
