bl_info = {
    'name':     'OGF Tools',
    'author':   'Vakhurin Sergey (igel)',
    'version':  (0, 0, 0),
    'blender':  (2, 68, 0),
    'category': 'Import-Export',
    'location': 'File > Import/Export',
    'description': 'Import STALKER OGF files',
    'wiki_url': 'https://github.com/igelbox/blender-ogf',
    'tracker_url': 'https://github.com/igelbox/blender-ogf/issues',
    'warning':  'Under construction!'
}

GAMEDATA = '/home/igel/.wine/drive_c/ST/NS/gamedata'

import os.path
import bpy
from bpy.props import *

class OgfImporter(bpy.types.Operator):
    bl_idname = 'import_scene.ogf'
    bl_label = 'Import OGF'
    bl_description = 'Imports compiled STALKER model data'
    bl_options = {'UNDO'}

    # Properties used by the file browser
    filepath = StringProperty(name='File path', description='File filepath used for importing the OGF file', maxlen=1024, default='')
    filter_folder = BoolProperty(name='Filter folders', description='', default=True, options={'HIDDEN'})
    filter_glob = StringProperty(default='*.ogf', options={'HIDDEN'})

    remesh = BoolProperty(
            name='remesh (very slow!)',
            description='divide polygons into smooth groups',
            default=False,
            )
    def execute(self, context):
        filepath_lc = self.properties.filepath.lower()
        if filepath_lc.endswith('.ogf'):
            from . import ogf_import
            objname = os.path.basename(filepath_lc)
            meshes = ogf_import.load(self.properties.filepath)
            if (self.properties.remesh):
                from . import ogf_remesh
                meshes = ogf_remesh.remesh(meshes)
            for i in meshes:
                me = bpy.data.meshes.new("mesh")
                ob = bpy.data.objects.new(objname, me)
                bpy.context.scene.objects.link(ob)
                vv, ff, nn, tt, tx = i
                me.from_pydata(vv,[],ff)
                if (tt):
                    me.uv_textures.new(name='UV')
                    uvl = me.uv_layers.active.data
                    for p in me.polygons:
                        for i in range(p.loop_start, p.loop_start + p.loop_total):
                            uv = tt[me.loops[i].vertex_index];
                            uvl[i].uv = (uv[0], 1-uv[1])
                if (tx != None):
                    tx = tx.lower().replace('/', os.path.sep).replace('\\', os.path.sep)
                    tex = bpy.data.textures.new('diffuse', type='IMAGE')
                    tex.image = bpy.data.images.load('{}/textures/{}.dds'.format(GAMEDATA, tx))
                    mat = bpy.data.materials.new(objname)
                    mtex = mat.texture_slots.add()
                    mtex.texture = tex
                    mtex.texture_coords = 'UV'
                    mtex.use_map_color_diffuse = True
                    me.materials.append(mat)
        else:
            if len(filepath_lc) == 0:
                self.report({'ERROR'},'No file selected')
            else:
                self.report({'ERROR'},'Format of {} not recognised'.format(os.path.basename(self.properties.filepath)))
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(OgfImporter.bl_idname, text='STALKER OGF (.ogf)')

def register():
    bpy.utils.register_class(OgfImporter)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(OgfImporter)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
