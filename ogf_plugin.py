bl_info = {
    'name':     'OGF Tools',
    'author':   'Vakhurin Sergey (igel)',
    'version':  (0, 0, 0),
    'blender':  (2, 68, 0),
    'category': 'Import-Export',
    'location': 'File > Import/Export',
    'description': 'Import STALKER OGF files',
    'warning':  'Under construction!'
}

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
            import ogf_import
            objname = os.path.basename(filepath_lc)
            meshes = ogf_import.load(self.properties.filepath)
            if (self.properties.remesh):
                import ogf_remesh
                meshes = ogf_remesh.remesh(meshes)
            for i in meshes:
                me = bpy.data.meshes.new("mesh")
                ob = bpy.data.objects.new(objname, me)
                bpy.context.scene.objects.link(ob)
                me.from_pydata(i[0],[],i[1])
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
