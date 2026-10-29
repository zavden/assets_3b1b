"""Builds the support files of the 2017 neural network videos (nn/part1-3).

The original code loads the real MNIST dataset (`mnist.pkl.gz`, ~16 MB) from the author's disk. That file is not
in the repo, so this script builds a small SYNTHETIC substitute from the 100 real MNIST digits that ship in the
repo (`image_map`, 10 per digit): each sample is a randomly shifted / slightly noisy / slightly blurred copy of one of
them. It also writes a Python 3 compatible `network.py` (binary-mode pickle files) and a `mnist_loader.py` that reads
the small dataset. Run from anywhere:  python make_nn_support.py
Output (next to this script, in `nn_pkg/`): network.py, mnist_loader.py, mnist_mini.npz
"""
import pickle
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_NN = HERE.parents[5] / "videos" / "_2017" / "nn"   # converted/../videos/_2017/nn
OUT = HERE / "nn_pkg"
N_TRAIN, N_VALID, N_TEST = 3000, 500, 1000


def shift(img, dx, dy):
    out = np.zeros_like(img)
    h, w = img.shape
    ys = slice(max(dy, 0), h + min(dy, 0))
    yd = slice(max(-dy, 0), h + min(-dy, 0))
    xs = slice(max(dx, 0), w + min(dx, 0))
    xd = slice(max(-dx, 0), w + min(-dx, 0))
    out[ys, xs] = img[yd, xd]
    return out


def make_split(rng, base, n):
    images, labels = [], []
    for i in range(n):
        digit = int(rng.integers(10)) if i >= 10 else i % 10
        img = np.asarray(base[digit][int(rng.integers(len(base[digit])))]).reshape(28, 28)
        img = shift(img, int(rng.integers(-2, 3)), int(rng.integers(-2, 3)))
        img = np.clip(img * rng.uniform(0.85, 1.0) + rng.normal(0, 0.03, img.shape), 0, 1)
        images.append((img * 255).astype(np.uint8).reshape(784))
        labels.append(digit)
    return np.array(images), np.array(labels, dtype=np.int64)


def main():
    OUT.mkdir(exist_ok=True)
    base = pickle.load(open(REPO_NN / "image_map", "rb"), encoding="latin1")
    rng = np.random.default_rng(2017)
    tr = make_split(rng, base, N_TRAIN)
    va = make_split(rng, base, N_VALID)
    te = make_split(rng, base, N_TEST)
    np.savez_compressed(OUT / "mnist_mini.npz", tr_x=tr[0], tr_y=tr[1], va_x=va[0], va_y=va[1], te_x=te[0], te_y=te[1])

    net = (REPO_NN / "network.py").read_text()
    # CHANGE: pickle files must be opened in binary mode in Python 3
    net = net.replace("open(IMAGE_MAP_DATA_FILE, mode = 'r')", "open(IMAGE_MAP_DATA_FILE, mode = 'rb')")
    net = net.replace("open(PRETRAINED_DATA_FILE, mode = 'w')", "open(PRETRAINED_DATA_FILE, mode = 'wb')")
    # CHANGE: Python 3 zip() is not subscriptable
    net = net.replace("zip(self.biases, self.weights)[:n_layers]", "list(zip(self.biases, self.weights))[:n_layers]")
    net = net.replace("# from utils.space_ops import get_norm", "from numpy.linalg import norm as get_norm")
    (OUT / "network.py").write_text(net)

    (OUT / "mnist_loader.py").write_text('''"""Small synthetic stand-in for the MNIST loader (see make_nn_support.py).
Same interface as the original `mnist_loader` (load_data, load_data_wrapper, vectorized_result)."""
import os

import numpy as np

_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mnist_mini.npz")


def load_data():
    d = np.load(_FILE)
    f = lambda x: x.astype(np.float32) / 255.0
    return (
        (f(d["tr_x"]), d["tr_y"]),
        (f(d["va_x"]), d["va_y"]),
        (f(d["te_x"]), d["te_y"]),
    )


def load_data_wrapper():
    tr_d, va_d, te_d = load_data()
    training_data = list(zip([np.reshape(x, (784, 1)) for x in tr_d[0]], [vectorized_result(y) for y in tr_d[1]]))
    validation_data = list(zip([np.reshape(x, (784, 1)) for x in va_d[0]], va_d[1]))
    test_data = list(zip([np.reshape(x, (784, 1)) for x in te_d[0]], te_d[1]))
    return (training_data, validation_data, test_data)


def vectorized_result(j):
    e = np.zeros((10, 1))
    e[j] = 1.0
    return e
''')


if __name__ == "__main__":
    main()
