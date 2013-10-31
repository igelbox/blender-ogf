#! /usr/bin/python

import io, struct

class Chunks:
    OGF_HEADER      = 0x1
    OGF4_S_DESC     = 0x12
    OGF4_CHILDREN   = 0x9
    OGF4_TEXTURE    = 0x2
    OGF4_VERTICES   = 0x3
    OGF4_INDICES    = 0x4

class rawr:
    def __init__(self, data):
        self.offs = 0
        self.data = data
    def read(sz=1):
        v = data[self.offs:self.offs+sz]
        self.offs+=sz
        return v;
    def unpack(self, fmt):
        s = struct.calcsize(fmt)
        self.offs += s
        return struct.unpack_from(fmt, self.data, self.offs-s)
    def unpack_asciiz(self):
        zpos = self.data.find(0, self.offs);
        if (zpos == -1):
            zpos = len(self.data);
        return self.unpack('={}sx'.format(zpos - self.offs))[0].decode('cp1251');
def ogfr(data):
    MASK_COMPRESSED = 0x80000000
    offs = 0
    while (offs < len(data)):
        i, s = struct.unpack_from('=II', data, offs);
        if ((i & MASK_COMPRESSED) != 0):
            raise Exception('compressed')
        offs += 8 + s
        yield (i & ~MASK_COMPRESSED, data[offs-s:offs])
def cfrs(tupl, expected):
    if (tupl[0] != expected):
        raise Exception('expected {}, but found: {}'.format(expected, tupl[0]))
    return tupl[1]

def load_ogfX(h, ogr):
    raise Exception('unsupported OGF format version: {}'.format(h[0]))

def load_ogf4_m05(ogr):
    c = rawr(cfrs(next(ogr), Chunks.OGF4_TEXTURE))
    tex = c.unpack_asciiz()
    shd = c.unpack_asciiz()
    #~ print ('texture:{}, shader:{}'.format(tex, shd));
    c = rawr(cfrs(next(ogr), Chunks.OGF4_VERTICES))
    vf, vc = c.unpack('=II')
    if (vf != 0x12071980):
        raise Exception('expected vertex format {:#x}, but found: {:#x}'.format(0x12071980, vf))
    vv = []
    #~ print('vf:{:#x}, vc:{}'.format(vf, vc))
    for _ in range(vc):
        v = c.unpack('=fff')
        vv.append(v)
        n = c.unpack('=fff')
        c.unpack('=fff')#tangen
        c.unpack('=fff')#binorm
        t = c.unpack('=ff')
        f = c.unpack('=I')[0]
        #~ print(v, n, b, t, f)
    c = rawr(cfrs(next(ogr), Chunks.OGF4_INDICES))
    ic = c.unpack('=I')[0]
    ii = []
    for _ in range(ic//3):
        ii.append(c.unpack('=HHH'))
    #~ print('{},[],{}'.format(vv, ii))
    return (vv, ii)
def load_ogf4_m10(ogr):
    c = rawr(cfrs(next(ogr), Chunks.OGF4_S_DESC))
    src = c.unpack_asciiz()
    #~ print ('source:{}'.format(src));
    exptool = c.unpack_asciiz()
    exptime, crttime, modtime = c.unpack('=III')
    result = []
    for i, c in ogfr(cfrs(next(ogr), Chunks.OGF4_CHILDREN)):
        result.append(load_ogf(c))
    return result

def load_ogf4(h, ogr):
    mt, shid = h.unpack('=BH')
    print ('modeltype:{}, shaderid:{}'.format(mt, shid))
    bbox = h.unpack('=ffffff')
    #~ print ('bbox:{}'.format(bbox))
    bsphere = h.unpack('=ffff')
    #~ print ('bsphere:{}'.format(bsphere))
    return {
     5: load_ogf4_m05,
    10: load_ogf4_m10
    }.get(mt)(ogr)

def load_ogf(data):
    ogr = ogfr(data)
    cr = rawr(cfrs(next(ogr), Chunks.OGF_HEADER))
    ver = cr.unpack('=B')[0]
    #~ print ('version:{}'.format(ver))
    return {
     4: load_ogf4
    }.get(ver, load_ogfX)(cr, ogr)

def load(fname):
    with io.open(fname, mode = 'rb') as f:
        return load_ogf(f.read())
if __name__ == '__main__':
    load('test.ogf')
