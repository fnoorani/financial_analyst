import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import make_response

def buffer_fig(fig):
    img = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(img)
    response = make_response(img.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response