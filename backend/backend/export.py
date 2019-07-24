from tempfile import NamedTemporaryFile
from slugify import slugify
from datetime import datetime

try:
    import pdfkit
except ImportError:
    pdfkit = None


def export_entries_as_pdf(logbook, entries):

    """
    Super basic "proof-of-concept" PDF export
    No proper formatting, and does not embed images.
    Note that pdfkit relies on the external library "wkhtmltopdf".
    TODO: pdfkit seems a bit limited, look for a more flexible alternative.
    "reportlab" looks pretty good (https://bitbucket.org/rptlab/reportlab)
    """

    if pdfkit is None:
        return None
    entries_html = []
    for entry in entries:
        html = '<div class="content'
        if entry.follows:
            html += ', followup'
            
        html += """
        ">        
        <p><b>Created at:</b> {created_at}</p>
        <p><b>Title:</b> {title}</p>
        <p><b>Authors:</b> {authors}</p>
        <p>{content}</p>
        <div>
        """.format(title=entry.title or "(No title)",
                   authors=", ".join(a["name"] for a in entry.authors),
                   created_at=entry.created_at,
                   content=entry.content or "---")
        entries_html.append(html)

    with NamedTemporaryFile(prefix=logbook.name,
                            suffix=".pdf",
                            delete=False) as f:
        options = {
            "load-error-handling": "ignore",
            "load-media-error-handling": "ignore",
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
        }
        try:
            pdfkit.from_string("<hr>".join(entries_html), f.name, options)
        except OSError:
            # Apparently there's some issue with wkhtmltopdf which produces
            # errors, but it works anyway. See
            # https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2051
            pass
        return f.name

def export_entries_as_html(logbook, entries):

    """
    Super basic "proof-of-concept" html export
    No proper formatting, and does not embed images.
    """

#    export = ""
    entries_html = []
    for entry in entries:
        if entry.follows:
            html = """
            <div class="followup">
            <div class="header">
            <p><b>Created at:</b> {created_at}</p>
            <p><b>Authors:</b> {authors}</p>
            </div>
            <div class="content">{content}</div>
            </div>
            """.format(authors=", ".join(a["name"] for a in entry.authors),
                       created_at=entry.created_at,
                       content=entry.content or "---")
        else:
            html = """
            <div>
            <div class="header">
            <p><b>Created at:</b> {created_at}</p>
            <p><b>Title:</b> {title}</p>
            <p><b>Authors:</b> {authors}</p>
            </div>
            <div class="content">{content}</div>
            </div>
            """.format(title=entry.title or "(No title)",
                       authors=", ".join(a["name"] for a in entry.authors),
                       created_at=entry.created_at,
                       content=entry.content or "---")
                  
        entries_html.append(html)
    with NamedTemporaryFile(prefix=slugify(logbook.name),
                            suffix=".html",
                            delete=False) as f:
        f.write(
        """<!doctype html>
        
        <script src="/static/tinymce/tinymce.min.js"></script>
        <link rel="stylesheet" href="/static/font-awesome/css/font-awesome.min.css">
        <link rel="stylesheet" href="https://code.cdn.mozilla.net/fonts/fira.css">
        
        <html lang="en">
        <head>
        <meta charset="utf-8">
        <link rel="shortcut icon" href="/favicon.ico">
        <style>
        a {
           color: #6482d2;
           outline: 0;  /* get rid of annoying selection rectangle in FF */
        }
        
        body {
            font-family: 'Fira Sans', 'Avenir', Helvetica, Arial, sans-serif;
            color: #3c415a;
            background-color: #f0f0f0;
            width: 100%;
            height: 100%;    
            margin:auto;
            position:relative;
            top: 0px;
            left: 0px;
        }
        h1 {
            padding-left: 15px;
            padding-bottom: 2px;
            padding-top: 2px;
        }
        
        .header {
            padding-left: 15px;
            padding-bottom: 2px;
            padding-top: 2px;
            border-bottom: 1px #333 solid;
        }
        .content {
            padding-left: 15px;
            padding-bottom: 2px;
            padding-top: 2px;
            background-color: #ffffff;
            border-bottom: 1px #333 solid;
        }
        p {
            margin: 5px 0px
        }
        .followup {
            padding-left: 50px;
            padding-bottom: 5px;            
            border-bottom: 1px #333 solid;
        }
        </style>
        <title>Elogy HTML Export</title>
        </head>
        <body>
        """.encode('utf8')
        )
        f.write('<h1>{}</h1>'.format(logbook.name).encode('utf8'))
        f.write('<div class="header"><b>Created at:</b> {}</div>'.format(datetime.now()).encode('utf8'))
        f.write('<div class="content">{}</div>'.format(logbook.description).encode('utf8'))
        for entry_html in entries_html:
            f.write(entry_html.encode('utf8'))
        f.write('</body></html>'.encode('utf8'))
        f.close()
    return f.name