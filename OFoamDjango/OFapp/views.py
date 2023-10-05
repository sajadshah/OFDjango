from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os
import glob
from OFapp.utils.ParametricOpenFoamCaseExecution import ParametricOpenFoamCaseExecution
from django.conf import settings
import shutil
import subprocess
from functools import cmp_to_key

def ResolveOpenFOAM(_U, _dx1, _dx2, _dx3, _dy1, _dy2):
    filename1 = ''
    filename2 = ''
    OFC = ParametricOpenFoamCaseExecution(u_in=_U,dx1=_dx1,dx2=_dx2,dx3=_dx3,dy1=_dy1,dy2=_dy2)
    OFC.prepareFolder()
    OFC.processFiles()
    OFC.execFoam()
    OFC.findConvergedSolutionFolder()
    OFC.visualize_vtk(scalarField='U')
    OFC.visualize_vtk(scalarField='p')
    
    # Iteration count 
    itrs_string = OFC.path_to_converged_VTK_solution_file.split('_')[-1].split('.vtk')[0]

    # Copy the files
    source_path_to_U_png = ParametricOpenFoamCaseExecution.path_to_U_png
    source_path_to_p_png = ParametricOpenFoamCaseExecution.path_to_p_png

    # Define the destination paths in the media folder
    destination_path_to_U_png = os.path.join(settings.MEDIA_ROOT, itrs_string + '_U.png')
    destination_path_to_p_png = os.path.join(settings.MEDIA_ROOT, itrs_string + '_p.png')

    # Copy the PNG files to the media folder
    shutil.copy(source_path_to_U_png, destination_path_to_U_png)
    shutil.copy(source_path_to_p_png, destination_path_to_p_png)

    # Get the relative paths to the images (relative to MEDIA_ROOT)
    relative_path_to_U_png = os.path.relpath(destination_path_to_U_png, start=settings.BASE_DIR)
    relative_path_to_p_png = os.path.relpath(destination_path_to_p_png, start=settings.BASE_DIR)

    return relative_path_to_U_png, relative_path_to_p_png
    

def input_form_view(request):
    context = {}  # Create a dictionary to hold context data
    
    if request.method == 'POST':
        subprocess.run('rm -f ./media/*.png', shell=True, timeout=20)

        U = request.POST.get('U')
        dx1 = request.POST.get('dx1')
        dx2 = request.POST.get('dx2')
        dx3 = request.POST.get('dx3')
        dy1 = request.POST.get('dy1')
        dy2 = request.POST.get('dy2')

        # Validate inputs
        if all(val is not None and val.strip() != '' for val in [U, dx1, dx2, dx3, dy1, dy2]):
            try:
                U = float(U)
                dx1 = float(dx1)
                dx2 = float(dx2)
                dx3 = float(dx3)
                dy1 = float(dy1)
                dy2 = float(dy2)

                # Set previous input values in the context to pre-populate the form
                context['previous_input'] = {
                    'U': U,
                    'dx1': dx1,
                    'dx2': dx2,
                    'dx3': dx3,
                    'dy1': dy1,
                    'dy2': dy2,
                }
                
                # Check validity conditions
                if 0.1 < U < 20 and 10 < dx1 < 100 and 100 < dx2 < 1000 and 50 < dx3 < 1000 and 10 < dy1 < 100 and 10 < dy2 < 100:
                    # Call your custom Python function here, passing the inputs as arguments
                    figure1_filename, figure2_filename = ResolveOpenFOAM(U, dx1, dx2, dx3, dy1, dy2)

                    # Add the filenames to the context to be used in the template
                    context['figure1_filename'] = figure1_filename
                    context['figure2_filename'] = figure2_filename

                    # You can return the result to the user or do anything else you want with it
                    # return HttpResponse(f"Result: Check the figures below.")
                    # return render(request, 'case_inputs.html', context)
                
                else:
                    # Set an error message in the context
                    context['error_message'] = "Invalid input. Please ensure U and the dx, dy values satisfy the conditions."
            except ValueError:
                # Set an error message in the context
                context['error_message'] = "Invalid input. Please enter valid numbers."

        else:
            # Set an error message in the context
            context['error_message'] = "Please fill in all the input fields."
        return JsonResponse(context)
    else:
        # Define your default values here
        context['previous_input'] = {
            'U': 10.0,
            'dx1': 51.2,
            'dx2': 206.0,
            'dx3': 84.0,
            'dy1': 50.8,
            'dy2': 33.2
        }
        
    # Pass the context to the template
    print(context)
    return render(request, 'case_inputs.html', context)


def get_intermediate_images(request):
    if request.method == 'GET':
        subprocess.run('cp -r case/*.png ../media', shell=True, cwd=ParametricOpenFoamCaseExecution.path_to_case_root,timeout=20)
        lf = glob.glob("media/*_xy.png")
        lf = sorted(lf,  key=cmp_to_key(lambda x, y: int(x.split("_")[1]) - int(y.split("_")[1])))
        latest = "" if len(lf) == 0 else lf[-1]
        res = {
            "files": lf,
            "latest": latest
        }
        return JsonResponse(res)

