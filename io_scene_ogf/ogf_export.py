from .ogf_utils import *


class bbox:
    def __init__(self, p):
        self.a = [p[0], p[1], p[2]]
        self.b = [p[0], p[1], p[2]]

    def expand(self, p):
        a = self.a
        b = self.b
        for i in range(3):
            v = p[i]
            if v < a[i]:
                a[i] = v
            if v > b[i]:
                b[i] = v


def calc_bbox(obj):
    import mathutils

    bb = obj.bound_box
    a = mathutils.Vector(bb[0]) * obj.matrix_world
    b = mathutils.Vector(bb[6]) * obj.matrix_world
    r = bbox(a)
    r.expand(b)
    for c in obj.children:
        ca, cb = calc_bbox(c)
        r.expand(ca)
        r.expand(cb)
    return r.a, r.b


def save_ogf(obj, fout):
    import mathutils

    ogw = ogfw(fout)
    cw = raww()
    cw.pack('=B', 4)  # OGF4
    cw.pack('=BH', 3, 0)  # mt:3, si:0
    mi = obj.matrix_world.inverted()
    bb = [(mathutils.Vector(_) * mi) for _ in calc_bbox(obj)]
    bbx = bbox(bb[0])
    bbx.expand(bb[1])
    print(bbx.a, bbx.b)
    cw.pack('=fff', *bbx.a)  # bbox
    cw.pack('=fff', *bbx.b)  # bbox
    sc = (bb[0] + bb[1]) / 2
    sr = max((sc - _).length for _ in bb)
    print(sc, sr)
    cw.pack('=fff', *sc)  # bsphere
    cw.pack('=f', sr)  # bsphere
    ogw.next(Chunks.OGF_HEADER, cw)
    pass


def save(obj, fpath):
    import io

    with io.open(fpath, mode='wb') as f:
        return save_ogf(obj, f.write)
