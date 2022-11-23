# configure the environmental path

from mfpml.design_of_experiment.sf_samplers import LatinHyperCube
from mfpml.problems.sf_functions import Branin
from mfpml.utils.plot_figures import plot_sf_sampling

# define function
function = Branin()
design_space = function.design_space
## test sampling part
sampler = LatinHyperCube(design_space=design_space,
                         seed=12)
samples = sampler.get_samples(num_samples=10)

# sampler.plot_samples(figure_name='test_sampling', save_plot=True)

sample_x = samples['inputs'].to_numpy()
sample_y = function.f(sample_x)

plot_sf_sampling(samples=sample_x, responses=sample_y, function=function, save_figure=True)