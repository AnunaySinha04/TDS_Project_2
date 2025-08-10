import io
import base64
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

def plot_scatter_with_regression(x, y, dotted_red=True, xlabel=None, ylabel=None, max_bytes=100_000):
    """
    Create a matplotlib scatter + regression line and return base64 data URI
    Try to compress (WEBP) to keep under max_bytes
    """
    plt.figure(figsize=(6,4), dpi=100)
    plt.scatter(x, y)
    if xlabel: plt.xlabel(xlabel)
    if ylabel: plt.ylabel(ylabel)

    # regression line
    X = np.array(x).reshape(-1,1)
    Y = np.array(y)
    if len(X) > 1:
        model = LinearRegression().fit(X, Y)
        xs = np.linspace(X.min(), X.max(), 100)
        ys = model.predict(xs.reshape(-1,1))
        line_style = ':' if dotted_red else '-'
        plt.plot(xs, ys, line_style, color='red', linewidth=1.5)

    buf = io.BytesIO()

    # Try WEBP first to get a smaller size
    plt.tight_layout()
    plt.savefig(buf, format='webp', optimize=True)
    plt.close()
    data = buf.getvalue()

    # If too big, reduce size / quality iteratively
    if len(data) > max_bytes:
        # try resaving at smaller resolution via PIL
        img = Image.open(io.BytesIO(data)).convert("RGB")
        for scale in [0.8, 0.6, 0.45, 0.3]:
            w, h = img.size
            new = img.resize((int(w*scale), int(h*scale)))
            buf2 = io.BytesIO()
            new.save(buf2, format='WEBP', quality=80, method=6)
            data = buf2.getvalue()
            if len(data) <= max_bytes:
                break

    b64 = base64.b64encode(data).decode('ascii')
    return f"data:image/webp;base64,{b64}", len(data)

def encode_png_to_datauri(pil_img, max_bytes=100_000):
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG", optimize=True)
    data = buf.getvalue()
    if len(data) > max_bytes:
        # fallback to webp
        buf = io.BytesIO()
        pil_img.convert("RGB").save(buf, format="WEBP", quality=80)
        data = buf.getvalue()
    b64 = base64.b64encode(data).decode("ascii")
    mime = "image/png" if data[:8] == b"\x89PNG\r\n\x1a\n" else "image/webp"
    return f"data:{mime};base64,{b64}", len(data)
