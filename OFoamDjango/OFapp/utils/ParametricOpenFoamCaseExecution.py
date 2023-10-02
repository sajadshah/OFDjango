import os

class ParametricOpenFoamCaseExecution:
     
    # Variables dependent on local OpenFOAM installation and server folder structure
    path_to_case_root = os.path.abspath('./OFCases')
    path_to_template_source = path_to_case_root + '/pitzDaily_template'
    path_to_target = path_to_case_root + '/case'
    path_to_U = path_to_target + '/0/U'
    path_to_geom = path_to_target + '/system/blockMeshDict'
    path_to_VTK = path_to_target + '/VTK'
    path_to_converged_VTK_solution_file = '' # to be updated after solution
    path_to_gltf_3D_U = path_to_VTK + '/U.gltf'
    path_to_gltf_3D_p = path_to_VTK + '/p.gltf'
    path_to_U_png = path_to_VTK + '/U.png'
    path_to_p_png = path_to_VTK + '/p.png'
    figure_width = 1200
    figure_height = 600

    def __init__(self, u_in=10.0, dx1=20.6, dx2=206.0, dx3=84.0, dy1=25.4, dy2=16.6):
        
        # Variables dependent on user input
        self.u_in = u_in
        self.dx1 = dx1
        self.dx2 = dx2
        self.dx3 = dx3
        self.dy1 = dy1
        self.dy2 = dy2
        
    def prepareFolder(self):
        from distutils.dir_util import copy_tree
        import shutil

        # Erase earlier case and results
        try:
            shutil.rmtree(ParametricOpenFoamCaseExecution.path_to_target)
            print(f"Folder '{ParametricOpenFoamCaseExecution.path_to_target}' and its contents have been removed successfully.")
        except OSError as e:
            print(f"Error: {e}")

        # Copy template folder
        #copy_tree(ParametricOpenFoamCaseExecution.path_to_template_source, ParametricOpenFoamCaseExecution.path_to_target)
        #print(f"THis is passed-1")

        import subprocess
        subprocess.run('cp -r pitzDaily_template/ case', shell=True, cwd=ParametricOpenFoamCaseExecution.path_to_case_root,timeout=20)
        #print(f"THis is passed-2")

    def processFiles(self):
        
        # U
        with open(ParametricOpenFoamCaseExecution.path_to_U, 'r') as file:
            data = file.read()
        
        data = data.replace("REPLACEME_U", str(self.u_in))

        with open(ParametricOpenFoamCaseExecution.path_to_U, "w") as file:
            file.write(data)

        # Geometry
        with open(ParametricOpenFoamCaseExecution.path_to_geom, 'r') as file:
            geomdata = file.read()
        
        geomdata = geomdata.replace("REPLACEME_DX1", str(self.dx1))
        geomdata = geomdata.replace("REPLACEME_DX2", str(self.dx2))
        geomdata = geomdata.replace("REPLACEME_DX3", str(self.dx3))
        geomdata = geomdata.replace("REPLACEME_DY1", str(self.dy1))
        geomdata = geomdata.replace("REPLACEME_DY2", str(self.dy2))

        with open(ParametricOpenFoamCaseExecution.path_to_geom, "w") as file:
            file.write(geomdata)
        

    def execFoam(self):
        import subprocess
        subprocess.run('blockMesh > log.blockMesh', shell=True, cwd=ParametricOpenFoamCaseExecution.path_to_target,timeout=20)
        subprocess.run('simpleFoam > log.solver', shell=True, cwd=ParametricOpenFoamCaseExecution.path_to_target,timeout=200)
        subprocess.run('foamToVTK > log.foamToVTK', shell=True, cwd=ParametricOpenFoamCaseExecution.path_to_target,timeout=50)
 
    def findConvergedSolutionFolder(self):
        # Finds the folder with highest integer number in the name (prouced by OpenFOAM as the converged sol'n)
        import os        
        intlistfolders = []
        list_subfolders_with_paths = [f.name for f in os.scandir(ParametricOpenFoamCaseExecution.path_to_target) if f.is_dir()]
        for x in list_subfolders_with_paths:
            try:
                intval = int(x)
                intlistfolders.append(intval)
            except:
                pass
        ParametricOpenFoamCaseExecution.path_to_converged_VTK_solution_file = ParametricOpenFoamCaseExecution.path_to_VTK + '/case_' + str(max(intlistfolders)) + '.vtk'

    def visualize_vtk(self, scalarField='U'):
        import pyvista as pv
        # Load the VTK file
        mesh = pv.read(ParametricOpenFoamCaseExecution.path_to_converged_VTK_solution_file)

        # Create a plotter and add the mesh with pressure data
        plotter = pv.Plotter(window_size=(ParametricOpenFoamCaseExecution.figure_width, ParametricOpenFoamCaseExecution.figure_height),off_screen=True)

        # Add the mesh to the plotter with the pressure data and colormap
        mesh_actor = plotter.add_mesh(mesh, scalars=scalarField, cmap='viridis', show_edges=False)

        # Customize the visualization settings
        plotter.set_background('white')

        # Reset the camera to zoom and center the scene
        plotter.reset_camera()

        # Remove the default colorbar
        plotter.remove_scalar_bar()
        
        # Add the colorbar to the plotter
        if scalarField == 'U':
            # Velocity magnitude
            label_txt = 'Velocity [m/s]'
            png_file = ParametricOpenFoamCaseExecution.path_to_U_png
            # Export the scene to GLTF format
            plotter.export_gltf(ParametricOpenFoamCaseExecution.path_to_gltf_3D_U)
        else:
            # Pressure
            label_txt = 'Pressure [Pa]'
            png_file = ParametricOpenFoamCaseExecution.path_to_p_png
            # Export the scene to GLTF format
            plotter.export_gltf(ParametricOpenFoamCaseExecution.path_to_gltf_3D_p)

        colorbar = plotter.add_scalar_bar(
            title='', n_labels=5, italic=False, shadow=False, width=0.5, above_label=label_txt
        )

        # Center the colormap horizontally
        colorbar_position_x = 0.5 - colorbar.GetWidth() / 2
        colorbar.SetDisplayPosition(int(colorbar_position_x*ParametricOpenFoamCaseExecution.figure_width), int(0.25*ParametricOpenFoamCaseExecution.figure_height))

        # Set view - this is a 2D model, so xy works
        plotter.camera_position = 'xy'

        # Do not display, but make a png file
        plotter.show(screenshot=png_file)


#OFC = ParametricOpenFoamCaseExecution()
#OFC.prepareFolder()
#OFC.processFiles()
#OFC.execFoam()
#OFC.findConvergedSolutionFolder()
#OFC.visualize_vtk(scalarField='U')
#OFC.visualize_vtk(scalarField='p')
jyki = 1

