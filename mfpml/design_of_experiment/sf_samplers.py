import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import scienceplots
from scipy.stats.qmc import Sobol, LatinHypercube
# local modulus
from mfpml.base.sampler import Sampler


class SingleFidelitySampler(Sampler):
    def __init__(self, design_space: dict, seed: int) -> None:
        """
                    
        Parameters
        ----------
        design_space: dict 
            design space 
        seed: int 
            seed
        Returns
        ----------

        """
        super(SingleFidelitySampler, self).__init__(design_space=design_space,
                                                    seed=seed)

    def _create_pandas_frame(self) -> None:
        """
        create pandas frame for samples
        Returns
        -------


        """
        self._samples = pd.DataFrame(self._samples, columns=list(self.design_space.keys()))

    def get_samples(self, num_samples: int, **kwargs) -> pd.DataFrame:
        """
          Get the samples

          Parameters
          ----------
          num_samples: int
              number of samples

          Returns
          ---------
          samples: pd.DataFrame
            samples generated from sampling methods

          Notes
          ---------
          The function should be completed at the sub-sclass

          """

        raise NotImplementedError("Subclasses should implement this method.")

    def plot_samples(self, figure_name: str = None, save_plot: bool = False) -> None:
        """
        Visualization of sampling method
        Parameters
        ----------
        figure_name:str
            figure name
        save_plot: bool
            save the figure or not

        Returns
        -------

        """

        if self.num_dim == 2:

            with plt.style.context(['ieee', 'science', 'high-contrast', 'grid']):
                fig, ax = plt.subplots()
                ax.plot(self.samples.iloc[:, 0], self.samples.iloc[:, 1], '*', label='Samples')
                ax.legend()
                # legend = ax.legend(loc='upper right', shadow=True)
                # legend.get_frame().set_facecolor('b')
                ax.set(xlabel=r'$x_1$')
                ax.set(ylabel=r'$x_2$')
                # ax.autoscale(tight=True)
                # plt.grid('--')
                if save_plot is True:
                    fig.savefig(figure_name, dpi=300)
                plt.show(block=True)
                plt.interactive(False)
        elif self.num_dim == 1:
            with plt.style.context(['ieee', 'science', 'high-contrast', 'grid']):
                fig, ax = plt.subplots()
                ax.plot(self.samples.iloc[:, 0], np.zeros((self.samples.shape[0], 1)), '.', label='Samples')
                ax.legend()
                ax.set(xlabel=r'$x$')
                ax.set(ylabel=r'$y$')
                ax.autoscale(tight=True)
                if save_plot is True:
                    fig.savefig(figure_name, dpi=300)
                plt.show(block=True)
                plt.interactive(False)
        else:
            raise Exception('Can not plot figure more than two dimension! \n ')

    @property
    def samples(self):
        return self._samples

    @property
    def data(self):
        return {'inputs': self._samples}


class FixNumberSampler(SingleFidelitySampler):
    def __init__(self, design_space: dict, seed: int) -> None:
        """

        Parameters
        ----------
        design_space: dict
            design space
        seed: int
            seed

        Returns
        -------
        """
        super(FixNumberSampler, self).__init__(design_space=design_space, seed=seed)

    def get_samples(self, num_samples: int, **kwargs) -> dict:
        """

        Parameters
        ----------
        num_samples: int
            number of samples
        kwargs: additional info

        Returns
        -------
        data: dict
            samples

        """
        fixed_value = list(self.design_space.values())
        self._samples = np.repeat(fixed_value[0], num_samples)
        self._create_pandas_frame()

        return self.data


class LatinHyperCube(SingleFidelitySampler):
    """
    Latin Hyper cube sampling
    """

    def __init__(self, design_space: dict, seed: int) -> None:
        """

        Parameters
        ----------
        design_space: dict
            design space
        seed: int
            seed
        """
        super(LatinHyperCube, self).__init__(design_space=design_space, seed=seed)

    def get_samples(self, num_samples: int, **kwargs) -> dict:
        lhs_sampler = LatinHypercube(d=self.num_dim, seed=self.seed, optimization="random-cd")
        sample = lhs_sampler.random(num_samples)
        for i, bounds in enumerate(self.design_space.values()):
            sample[:, i] = sample[:, i] * (bounds[1] - bounds[0]) + bounds[0]

        self._samples = sample
        self._create_pandas_frame()
        return self.data


class RandomSampler(SingleFidelitySampler):
    """
    Random sampling
    """

    def __init__(self, design_space: dict, seed: int) -> None:
        """

        Parameters
        ----------
        design_space: dict
            design space
        seed: int
            seed
        """
        super(RandomSampler, self).__init__(design_space=design_space, seed=seed)

    def get_samples(self, num_samples: int, **kwargs) -> dict:
        np.random.seed(self.seed)
        sample = np.random.random((num_samples, self.num_dim))
        for i, bounds in enumerate(self.design_space.values()):
            sample[:, i] = sample[:, i] * (bounds[1] - bounds[0]) + bounds[0]

        self._samples = sample
        self._create_pandas_frame()
        return self.data


class SobolSequence(SingleFidelitySampler):
    """
    Sobol Sequence sampling
    """

    def __init__(self, design_space: dict,
                 seed: int,
                 num_skip: int = None) -> None:
        """

        Parameters
        ----------
        design_space: dict
            design space
        seed: int
            seed
        num_skip: int
            cut the first several samples s
        """
        super(SobolSequence, self).__init__(design_space=design_space,
                                            seed=seed)
        if num_skip is None:
            self.num_skip = len(design_space)
        else:
            self.num_skip = num_skip

    def get_samples(self, num_samples: int, **kwargs) -> dict:
        sobol_sampler = Sobol(d=self.num_dim, seed=self.seed)
        # generate lots of samples first
        sobol_sampler.random_base2(m=num_samples)
        _ = sobol_sampler.reset()
        _ = sobol_sampler.fast_forward(n=self.num_skip)
        # get the samples
        sample = sobol_sampler.random(n=num_samples)

        for i, bounds in enumerate(self.design_space.values()):
            sample[:, i] = sample[:, i] * (bounds[1] - bounds[0]) + bounds[0]

        self._samples = sample
        self._create_pandas_frame()

        return self.data