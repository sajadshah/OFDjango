import pyvista as pv
import os
dir = os.listdir('postProcessing/planes')
dir = [int(value) for value in dir]

        # Load the VTK file
mesh = pv.read('postProcessing/planes/'+ str(max(dir)) +'/U_xy.vtk')

        # Create a plotter and add the mesh with pressure data
plotter = pv.Plotter(window_size=(1024, 568),off_screen=True)
scalarField = 'U'
        # Add the mesh to the plotter with the pressure data and colormap
mesh_actor = plotter.add_mesh(mesh, scalars=scalarField, cmap='jet', show_edges=False)

        # Customize the visualization settings
plotter.set_background('#FFFFFF')

        # Reset the camera to zoom and center the scene
plotter.reset_camera()

#plotter.camera.zoom(1.0)
        # Remove the default colorbar
plotter.remove_scalar_bar()
        
        # Add the colorbar to the plotter
            # Velocity magnitude
label_txt = 'Velocity'
png_file = 'U_'+ str(max(dir)) +'_xy.png'
            # Export the scene to GLTF format
#plotter.export_gltf('U_330.gltf')
plotter.add_title('Time: '+ str(max(dir)) + ' s')
colorbar = plotter.add_scalar_bar(
            title='', n_labels=5, italic=False, shadow=False, width=0.5, above_label=label_txt)

        # Center the colormap horizontally
colorbar_position_x = 0.5 - colorbar.GetWidth() / 2
colorbar.SetDisplayPosition(int(colorbar_position_x*800), int(0.25*400))

        # Set view - this is a 2D model, so xy works
plotter.camera_position = 'xy'

        # Do not display, but make a png file
plotter.show(screenshot=png_file)
