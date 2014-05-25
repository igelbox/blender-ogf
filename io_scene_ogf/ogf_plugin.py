import bpy


#noinspection PyUnusedLocal
class OgfImporter(bpy.types.Operator):
    bl_idname = 'import_scene.ogf'
    bl_label = 'Import OGF'
    bl_description = 'Imports compiled STALKER model data'
    bl_options = {'UNDO'}

    # Properties used by the file browser
    filepath = bpy.props.StringProperty(
        name='File path', description='File filepath used for importing the OGF file',
        maxlen=1024, default=''
    )
    filter_folder = bpy.props.BoolProperty(name='Filter folders', description='', default=True, options={'HIDDEN'})
    filter_glob = bpy.props.StringProperty(default='*.ogf', options={'HIDDEN'})

    remesh = bpy.props.BoolProperty(
        name='remesh (very slow!)',
        description='divide polygons into smooth groups',
        default=False,
    )

    def execute(self, context):
        filepath_lc = self.properties.filepath.lower()
        if filepath_lc.endswith('.ogf'):
            from .ogf_import import load, ImportContext
            load(ImportContext(
                file_name=self.properties.filepath,
                remesh=self.properties.remesh
            ))
        else:
            if len(filepath_lc) == 0:
                self.report({'ERROR'}, 'No file selected')
            else:
                self.report({'ERROR'}, 'Format of {} not recognised'.format(self.properties.filepath))
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


#noinspection PyUnusedLocal
class OgfExporter(bpy.types.Operator):
    bl_idname = 'export_scene.ogf'
    bl_label = 'Export OGF'
    bl_description = 'Exports compiled STALKER model data'
    bl_options = {'UNDO'}

    # Properties used by the file browser
    filepath = bpy.props.StringProperty(
        name='File path', description='File filepath used for exporting the OGF file',
        maxlen=1024, default=''
    )
    filter_folder = bpy.props.BoolProperty(name='Filter folders', description='', default=True, options={'HIDDEN'})
    filter_glob = bpy.props.StringProperty(default='*.ogf', options={'HIDDEN'})

    def execute(self, context):
        filepath_lc = self.properties.filepath.lower()
        if filepath_lc.endswith('.ogf'):
            obj = bpy.context.scene.objects.active
            if not obj:
                self.report({'ERROR'}, 'No object selected')
                return {'CANCELLED'}
            from .ogf_export import save
            save(obj, self.properties.filepath)
        else:
            if len(filepath_lc) == 0:
                self.report({'ERROR'}, 'No file selected')
            else:
                self.report({'ERROR'}, 'Format of {} not recognised'.format(self.properties.filepath))
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


#noinspection PyUnusedLocal
def menu_func_import(self, context):
    self.layout.operator(OgfImporter.bl_idname, text='STALKER OGF (.ogf)')


#noinspection PyUnusedLocal
def menu_func_export(self, context):
    self.layout.operator(OgfExporter.bl_idname, text='STALKER OGF (.ogf)')


def register():
    bpy.utils.register_class(OgfImporter)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(OgfExporter)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(OgfExporter)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(OgfImporter)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
