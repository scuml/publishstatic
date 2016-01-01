import gzip
from io import BytesIO

try:
    from jsmin import jsmin
    from cssmin import *
except:
    jsmin = None
    cssmin = None

def gzip_content(headers, stream):
    "Gzips a file"
    headers['Content-Encoding'] = 'gzip'
    buff = BytesIO()
    gz = gzip.GzipFile(filename="tmp", fileobj=buff, mode='w')
    gz.write(stream.read())
    gz.close()
    stream.close()
    stream = BytesIO(buff.getvalue())
    return headers, stream


def minify(filename, filetype, stream):

    if ".min" in filename or ".pack" in filename:
        return stream, 'already minified'

    if filetype == 'application/javascript':

        # Remove console statements
        js = re.sub("console.\\w+\\(.*?\\);?", "", stream.read())
        js = jsmin(js)
        stream = BytesIO(js)


    elif filetype == 'text/css':
        css = cssmin(stream.read())
        stream = BytesIO(css)

    return stream, 'minified'
