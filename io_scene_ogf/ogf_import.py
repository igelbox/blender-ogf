from .ogf_utils import *

try:
    import bpy
except ImportError:
    bpy = None


class ImportContext:
    def __init__(self, file_name, remesh=False):
        from .settings import GAMEDATA_FOLDER
        self.gamedata = GAMEDATA_FOLDER
        self.file_name = file_name
        import os.path
        self.object_name = os.path.basename(file_name.lower())
        self.__images = {}
        self.__textures = {}

    def image(self, relpath):
        import os.path
        relpath = relpath.lower().replace('/', os.path.sep).replace('\\', os.path.sep)
        result = self.__images.get(relpath)
        if not result:
            self.__images[relpath] = result = bpy.data.images.load('{}/textures/{}.dds'.format(self.gamedata, relpath))
        return result

    def texture(self, relpath):
        result = self.__textures.get(relpath)
        if not result:
            self.__textures[relpath] = result = bpy.data.textures.new('texture', type='IMAGE')
            result.image = self.image(relpath)
        return result


def load_ogf4_m05(ogr, context, parent):
    c = rawr(cfrs(next(ogr), Chunks.OGF4_TEXTURE))
    teximage = c.unpack_asciiz()
    c.unpack_asciiz()  # shader
    c = rawr(cfrs(next(ogr), Chunks.OGF4_VERTICES))
    vertex_format, vertices_count = c.unpack('=II')
    vv, nn, tt = [], [], []
    if vertex_format == 0x12071980:  # OGF4_VERTEXFORMAT_FVF_1L
        for _ in range(vertices_count):
            v = c.unpack('=fff')
            vv.append(v)
            n = c.unpack('=fff')
            nn.append(n)
            c.unpack('=fff')  # tangen
            c.unpack('=fff')  # binorm
            tt.append(c.unpack('=ff'))
            c.unpack('=I')
    elif vertex_format == 0x240e3300:  # OGF4_VERTEXFORMAT_FVF_2L
        for _ in range(vertices_count):
            c.unpack('=HH')
            vv.append(c.unpack('=fff'))
            nn.append(c.unpack('=fff'))
            c.unpack('=fff')  # tangen
            c.unpack('=fff')  # binorm
            c.unpack('=f')
            tt.append(c.unpack('=ff'))
    else:
        raise Exception('unexpected vertex format: {:#x}'.format(vertex_format))
        #~ print('vf:{:#x}, vc:{}'.format(vf, vc))
    c = rawr(cfrs(next(ogr), Chunks.OGF4_INDICES))
    ic = c.unpack('=I')[0]
    ii = []
    for _ in range(ic // 3):
        ii.append(c.unpack('=HHH'))
        #~ print('{},[],{}'.format(vv, ii))
    if bpy:
        # mesh
        bpy_mesh = bpy.data.meshes.new('mesh')
        bpy_mesh.from_pydata(vv, [], ii)
        # uv-map
        bpy_mesh.uv_textures.new(name='UV')
        uvl = bpy_mesh.uv_layers.active.data
        for p in bpy_mesh.polygons:
            for i in range(p.loop_start, p.loop_start + p.loop_total):
                uv = tt[bpy_mesh.loops[i].vertex_index]
                uvl[i].uv = (uv[0], 1-uv[1])
        # material
        if teximage:
            bpy_material = bpy.data.materials.new(context.object_name)
            bpy_texture = bpy_material.texture_slots.add()
            bpy_texture.texture = context.texture(teximage)
            bpy_texture.texture_coords = 'UV'
            bpy_texture.use_map_color_diffuse = True
            bpy_mesh.materials.append(bpy_material)
        # object
        bpy_object = bpy.data.objects.new(context.object_name, bpy_mesh)
        bpy_object.parent = parent
        bpy.context.scene.objects.link(bpy_object)


def load_ogf4_m10(ogr, context, parent):
    c = rawr(cfrs(next(ogr), Chunks.OGF4_S_DESC))
    c.unpack_asciiz()  # src
    #~ print ('source:{}'.format(src));
    c.unpack_asciiz()  # exptool
    c.unpack('=III')  # exptime, crttime, modtime
    if bpy:
        bpy_object = bpy.data.objects.new(context.object_name, None)
        bpy_object.parent = parent
        import math
        bpy_object.rotation_euler.x = math.pi/2
        bpy.context.scene.objects.link(bpy_object)
        parent = bpy_object
    for i, c in ogfr(cfrs(next(ogr), Chunks.OGF4_CHILDREN)):
        load_ogf(c, context, parent)


def load_ogf4(h, ogr, context, parent):
    mt, shid = h.unpack('=BH')
    print('modeltype:{}, shaderid:{}'.format(mt, shid))
    h.unpack('=ffffff')  # bounding box
    h.unpack('=ffff')  # bounding sphere
    return {
        5: load_ogf4_m05,
        10: load_ogf4_m10
    }.get(mt)(ogr, context, parent)


def load_ogf(data, context, parent=None):
    ogr = ogfr(data)
    cr = rawr(cfrs(next(ogr), Chunks.OGF_HEADER))
    ver = cr.unpack('=B')[0]
    #~ print ('version:{}'.format(ver))

    #noinspection PyUnusedLocal
    def unsupported(h, _, p, oname):
        raise Exception('unsupported OGF format version: {}'.format(ver))
    return {
        4: load_ogf4
    }.get(ver, unsupported)(cr, ogr, context, parent)


def load(context):
    import io
    with io.open(context.file_name, mode='rb') as f:
        return load_ogf(f.read(), context)
