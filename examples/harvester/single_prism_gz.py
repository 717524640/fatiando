"""
Example of inverting synthetic gz data from a single prism using harvester
"""
try:
    from mayavi import mlab
except ImportError:
    from enthought.mayavi import mlab
from matplotlib import pyplot
from fatiando import potential, vis, logger, utils, gridder
from fatiando.mesher.volume import Prism3D, PrismMesh3D, extract, vfilter
from fatiando.inversion import harvester

vis.mlab = mlab

log = logger.get()
log.info(__doc__)

log.info("First make the synthetic model:\n")
extent = (0, 10000, 0, 10000, 0, 6000)
model = [Prism3D(4000, 6000, 2000, 8000, 2000, 4000, props={'density':800})]

#mlab.figure(bgcolor=(1,1,1))
#vis.prisms3D(model, extract('density', model), vmin=0)
#outline = mlab.outline(color=(0,0,0), extent=extent)
#vis.add_axes3d(outline)
#vis.wall_bottom(extent)
#vis.wall_north(extent)
#mlab.show()

log.info("\nSecond calculate the synthetic data:")
shape = (50,50)
#x, y, z = gridder.scatter(extent[0:4], 200, z=-1)
x, y, z = gridder.regular(extent[0:4], shape, z=-1)
#gz = utils.contaminate(potential.prism.gz(x, y, z, model), 0.1)
gz = potential.prism.gz(x, y, z, model)

#pyplot.figure()
#pyplot.axis('scaled')
#pyplot.title('Synthetic gz data')
#levels = vis.contourf(y, x, gz, shape, 10)
#vis.contour(y, x, gz, shape, levels)
#pyplot.plot(y, x, 'xk')
#pyplot.xlabel('East (km)')
#pyplot.ylabel('North (km)')
#pyplot.show()

log.info("\nThird make a prism mesh:")
mesh = PrismMesh3D(extent, (15, 25, 25))

#mlab.figure(bgcolor=(1,1,1))
#vis.prisms3D(mesh, (0 for i in xrange(mesh.size)), vmin=0)
#outline = mlab.outline(color=(0,0,0), extent=extent)
#vis.add_axes3d(outline)
#mlab.show()

log.info("\nFourth sow the seeds:")
rawseeds = [((5000, 5000, 3000), {'density':800})]
#rawseeds = [((5000, 3000, 3000), {'density':800}),
            #((5000, 7000, 3000), {'density':800})]
seeds = harvester.sow(mesh, rawseeds)

#mlab.figure(bgcolor=(1,1,1))
#vis.prisms3D(model, extract('density', model), opacity=0.3, vmin=0)
#vis.prisms3D((mesh[s] for s, p in seeds), (p['density'] for s, p in seeds),
             #vmin=0)
#outline = mlab.outline(color=(0,0,0), extent=extent)
#vis.add_axes3d(outline)
#vis.wall_bottom(extent)
#vis.wall_north(extent)
#mlab.show()
    
log.info("\nFith harvest the results:")
gzmod = harvester.GzModule(x, y, z, gz)
reg = harvester.ConcentrationRegularizer(10**(-4), seeds, mesh)
def meh(i,j,k):
    return True
#harvester.is_eligible = meh

result = harvester.harvest(seeds, mesh, [gzmod], reg, tol=0.01)
estimate = result['estimate']
for prop in estimate:
    mesh.addprop(prop, estimate[prop])
density_model = vfilter(1, 2000, 'density', mesh)

#import numpy
#for chset in harvester.grow(seeds, mesh, [gzmod], reg, tol=0.1):    
    #estimate = chset['estimate']
    #for prop in estimate:
        #mesh.addprop(prop, estimate[prop])
    #density_model = vfilter(1, 2000, 'density', mesh)
    #neighbors = [mesh[n] for nei in chset['neighborhood'] for n, p in nei]
    #mlab.figure(bgcolor=(1,1,1))
    #vis.prisms3D(model, extract('density', model), style='wireframe', vmin=0)
    #vis.prisms3D(neighbors, numpy.zeros_like(neighbors), style='wireframe')
    #vis.prisms3D(density_model, extract('density', density_model), vmin=0)
    #outline = mlab.outline(color=(0,0,0), extent=extent)
    #mlab.show()

pyplot.figure()
pyplot.subplot(2,1,1)
pyplot.title("Adjustment")
pyplot.axis('scaled')
levels = vis.contourf(y, x, gz, shape, 12)
pyplot.colorbar()
vis.contour(y, x, gzmod.predicted(), shape, 12)
pyplot.xlabel('East (km)')
pyplot.ylabel('North (km)')
pyplot.subplot(2,1,2)
pyplot.title("Residuals")
pyplot.axis('scaled')
vis.pcolor(y, x, gzmod.res, shape)
pyplot.colorbar()
pyplot.xlabel('East (km)')
pyplot.ylabel('North (km)')
pyplot.show()

mlab.figure(bgcolor=(1,1,1))
vis.prisms3D(model, extract('density', model), style='wireframe')
vis.prisms3D(density_model, extract('density', density_model), vmin=0)
outline = mlab.outline(color=(0,0,0), extent=extent)
vis.add_axes3d(outline)
vis.wall_bottom(extent)
vis.wall_north(extent)
mlab.show()    
