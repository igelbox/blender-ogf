from .ogf_utils import *


def load_ogf4_m05(ogr):
    c = rawr(cfrs(next(ogr), Chunks.OGF4_TEXTURE))
    tex = c.unpack_asciiz()
    c.unpack_asciiz()  # shader
    c = rawr(cfrs(next(ogr), Chunks.OGF4_VERTICES))
    vf, vc = c.unpack('=II')
    vv, nn, tt = [], [], []
    if vf == 0x12071980:  # OGF4_VERTEXFORMAT_FVF_1L
        for _ in range(vc):
            v = c.unpack('=fff')
            vv.append(v)
            n = c.unpack('=fff')
            nn.append(n)
            c.unpack('=fff')  # tangen
            c.unpack('=fff')  # binorm
            tt.append(c.unpack('=ff'))
            c.unpack('=I')
    elif vf == 0x240e3300:  # OGF4_VERTEXFORMAT_FVF_2L
        for _ in range(vc):
            c.unpack('=HH')
            vv.append(c.unpack('=fff'))
            nn.append(c.unpack('=fff'))
            c.unpack('=fff')  # tangen
            c.unpack('=fff')  # binorm
            c.unpack('=f')
            tt.append(c.unpack('=ff'))
    else:
        raise Exception('unexpected vertex format: {:#x}'.format(vf))
        #~ print('vf:{:#x}, vc:{}'.format(vf, vc))
    c = rawr(cfrs(next(ogr), Chunks.OGF4_INDICES))
    ic = c.unpack('=I')[0]
    ii = []
    for _ in range(ic // 3):
        ii.append(c.unpack('=HHH'))
        #~ print('{},[],{}'.format(vv, ii))
    return vv, ii, nn, tt, tex


def load_ogf4_m10(ogr):
    c = rawr(cfrs(next(ogr), Chunks.OGF4_S_DESC))
    c.unpack_asciiz()  # src
    #~ print ('source:{}'.format(src));
    c.unpack_asciiz()  # exptool
    c.unpack('=III')  # exptime, crttime, modtime
    result = []
    for i, c in ogfr(cfrs(next(ogr), Chunks.OGF4_CHILDREN)):
        result.append(load_ogf(c))
    return result


def load_ogf4(h, ogr):
    mt, shid = h.unpack('=BH')
    print('modeltype:{}, shaderid:{}'.format(mt, shid))
    h.unpack('=ffffff')  # bounding box
    h.unpack('=ffff')  # bounding sphere
    return {
        5: load_ogf4_m05,
        10: load_ogf4_m10
    }.get(mt)(ogr)


def load_ogf(data):
    ogr = ogfr(data)
    cr = rawr(cfrs(next(ogr), Chunks.OGF_HEADER))
    ver = cr.unpack('=B')[0]
    #~ print ('version:{}'.format(ver))

    #noinspection PyUnusedLocal
    def unsupported(h, _):
        raise Exception('unsupported OGF format version: {}'.format(ver))
    return {
        4: load_ogf4
    }.get(ver, unsupported)(cr, ogr)


def load(fname):
    import io
    with io.open(fname, mode='rb') as f:
        return load_ogf(f.read())
