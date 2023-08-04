# OFDjango

This is a Django project demonstrating execution of an open source Computational Fluid Dynamics solver (OpenFOAM) through a web browser interface.

The demo is set up on the pizDaily tutorial (axisymmetric 2D flow over backward facing step towards a contracting nozzle). The user can input inlet velocity as well as the main geometry dimensions on a html form. Submitting the form data invokes the following through Python/Django:

1) Instantiation of the parametric geometry
2) Meshing (execute blockMesh)
3) CFD solution (execute simpleFOAM)
4) Post-processing (execute foamToVTK followed by custom code execution to produce png snapshots of velocity magnitude and static pressure)
5) Feeding the flow field solution figures to the html template and re-render the user interface

   
