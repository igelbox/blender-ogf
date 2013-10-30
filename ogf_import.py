#! /usr/bin/python

import io, struct

class Chunks:
    OGF_HEADER      = 0x1
    OGF4_S_DESC     = 0x12
    OGF4_CHILDREN   = 0x9

class Chunk:
    def __init__(self, id, data):
        self.id = id
        self.data = data
        self.offs = 0
    def read(self, fmt):
        v = struct.unpack_from(fmt, self.data, self.offs)
        self.offs += struct.calcsize(fmt);
        return v;
    def read_asciiz(self):
        zpos = self.data.find(0, self.offs);
        if (zpos == -1):
            zpos = len(self.data);
        return self.read('={}sx'.format(zpos - self.offs))[0];
    def read_reader(self):
        def rr(sz=1):
            v = self.data[self.offs:self.offs+sz]
            self.offs += sz
            return v
        return ChunkReader(rr)
class ChunkReader:
    MASK_COMPRESSED = 0x80000000
    MASK_ID         = ~MASK_COMPRESSED
    def __init__(self, read):
        self.read = read
    def next(self, check=0):
        b = self.read(8)
        if (len(b) == 0):
            return None
        i, s = struct.unpack('=II', b);
        if ((i & self.MASK_COMPRESSED) != 0):
            raise Exception('compressed')
        i &= self.MASK_ID
        if ((check != 0) & (i != check)):
            raise Exception('expected chunk {}, but found: {}'.format(check, i))
        return Chunk(i, self.read(s))

def load_ogfX(h, r):
    raise Exception('unsupported OGF format version: {}'.format(h[0]))

def load_ogf4(h, r):
    mt, shid = h.read('=BH')
    #~ print ('modeltype:{}, shaderid:{}'.format(mt, shid))
    bbox = h.read('=ffffff')
    #~ print ('bbox:{}'.format(bbox))
    bsphere = h.read('=ffff')
    #~ print ('bsphere:{}'.format(bsphere))
    c = r.next(Chunks.OGF4_S_DESC)
    src = c.read_asciiz()
    #~ print ('source:{}'.format(src));
    exptool = c.read_asciiz()
    exptime, crttime, modtime = c.read('=III')
    c = r.next(Chunks.OGF4_CHILDREN)
    cr = c.read_reader()

def load(fname):
    f = io.open(fname, 'rb')
    try:
        r = ChunkReader(f.read)
        c = r.next(Chunks.OGF_HEADER)
        ver = c.read('=B')[0]
        print ('header(size:{}, version:{})'.format(len(c.data), ver))
        {4: load_ogf4
        }.get(ver, load_ogfX)(c, r)
    finally:
        f.close();

load('test.ogf')
