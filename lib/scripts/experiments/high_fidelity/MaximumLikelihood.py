# Write a class to do the analysis

import numpy as np
import operator
import functools
from scipy.special import factorial
from scipy.optimize import curve_fit

class MaximumLikelihood:

    def __init__(self):

        self.mean_dark = .02
        self.mean_bright = 5.0
        self.number_tbins = 100.0
        self.t_start = 0.000460696
        self.t_stop = 0.01060696
        self.detection_time = 6.0e-3
        self.state_lifetime = 30.0
        self.p_dark = 0
        self.p_bright = 0
        self.err_bright = 0
        self.err_dark = 0

    def poisson(self, x, mean):
        return (np.exp(-mean)*mean**x)/factorial(x)

    def find_mean(self, bins, counts):
        return np.sum(bins*counts)/np.sum(counts)

    def fit_poisson(self, bins, counts):
        guess = self.find_mean(bins, counts)
        fit, err = curve_fit(self.poiss, bins, counts, p0 = guess)
        if abs(fit[0] - guess) < .2*guess:
            return fit[0]
        else:
            return guess

    def set_mean_dark(self, bins, counts):
        self.mean_dark = self.fit_poisson(bins, counts)

    def set_mean_bright(self, bins, counts):
        self.mean_bright = self.fit_poisson(bins, counts)

    def bin_time_tags(self, time_tags):
        #if type(self.t_start) != 'float':
            #raise ValueError(type(self.t_start))
        hist = np.histogram(time_tags, bins = self.number_tbins, range = (self.t_start, self.t_stop))
        bins = hist[1]
        counts = hist[0]
        return bins, counts

    def prob_bright(self, binned_counts):
        p_bins = self.poisson(binned_counts, self.mean_bright/self.number_tbins)
        p_bright = functools.reduce(operator.mul, p_bins)
        self.p_bright = p_bright
        return p_bright

    def prob_dark(self, binned_counts):

        # Calc prob ion did not decay during detection
        p_bins = self.poisson(binned_counts, self.mean_dark/self.number_tbins)
        p_dark_no_decay = functools.reduce(operator.mul, p_bins)
        p_no_decay = (1 - self.detection_time/self.state_lifetime)*p_dark_no_decay

        # Calc prob ion decays during detection time
        p_decay = 0
        for i in range(len(binned_counts)):
            p_bins = np.concatenate((self.poisson(binned_counts[i:], self.mean_bright/self.number_tbins), \
            self.poisson(binned_counts[:i], self.mean_dark/self.number_tbins)))
            p_dark_decay = functools.reduce(operator.mul, p_bins)
            p_decay = p_decay + p_dark_decay
        p_decay = p_decay*self.detection_time/self.state_lifetime/self.number_tbins
        p_dark = p_decay + p_no_decay
        self.p_dark = p_dark
        return p_dark

    def prob_dark_recursive(self, binned_counts):
        M = 1
        S = 0
        for i in range(len(binned_counts)):
            S = (S + M)*self.poisson(binned_counts[i], self.mean_bright/self.number_tbins)
            M = M*self.poisson(binned_counts[i], self.mean_dark/self.number_tbins)

        p_dark = (1 - self.detection_time/self.state_lifetime)*M + \
                S*self.detection_time/self.state_lifetime/self.number_tbins
        self.p_dark = p_dark
        return p_dark

    def err_bright(self):
        self.err_bright = self.p_dark/(self.p_dark + self.p_bright)
        return self.err_bright

    def err_dark(self):
        self.err_dark = self.p_bright/(self.p_dark + self.p_bright)
        return self.err_dark
