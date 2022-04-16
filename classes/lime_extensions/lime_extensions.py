import spacy
nlp = spacy.load('en_core_web_sm')
from classes.ml_file_loader import load_ml_model_from_file
import numpy as np
import scipy as sp
import sklearn
import itertools
import pandas as pd
import time
import re
import math
from sklearn.utils import check_random_state
import matplotlib.pyplot as plt
from lime.lime_text import LimeTextExplainer, IndexedString, TextDomainMapper


from lime.lime_text import LimeTextExplainer, IndexedString, TextDomainMapper
import itertools
import time


def map_multiple_results_to_string(results, combined_coefficients):
    explanations_as_dict = {x[0] : x[1] for x in combined_coefficients}
    
    #Initial sentence as indexed string
    string_as_list = []
    
    for result in results:
        string_as_list.extend(result.domain_mapper.indexed_string.as_list)
        
    string_exps_as_list = [explanations_as_dict[x] if x in explanations_as_dict else 0 for x in string_as_list]
    
    return string_as_list, string_exps_as_list

def map_result_to_string(result):
    #Explanations
    explanations_as_list = result.as_list()
    explanations_as_dict = {x[0] : x[1] for x in explanations_as_list}
    
    #Initial sentence as indexed string
    string_as_list = result.domain_mapper.indexed_string.as_list
    
    string_exps_as_list = [explanations_as_dict[x] if x in explanations_as_dict else 0 for x in string_as_list]
    
    return string_as_list, string_exps_as_list
    
    
def extend_explanation_words(r1, r2):
    """
    Extends tokens not in one explanation with coefficient 0
    """
    rc1 = r1.copy()
    rc2 = r2.copy()
    tokens1 = {k[0] for k in r1}
    tokens2 = {k[0] for k in r2}
    
    for t in tokens1:
        if t not in tokens2:
            rc2.append((t, 0))
    for t in tokens2:
        if t not in tokens1:
            rc1.append((t,0))
    return sorted(rc1), sorted(rc2)


def combine_results(results):
    h = [x for x in results]
    comb = []
    for e in h:
        comb = extend_explanation_words(comb, e)[0]

    comb_all_other = []
    for e in h:
        comb_all_other.append(extend_explanation_words(comb, e)[1])
    comb_all_other_values = [np.array([y[1] for y in x]) for x in comb_all_other]
    for i in range(len(comb_all_other_values)):
        comb_all_other_values[i][comb_all_other_values[i]==0] = np.nan 
    values_mean = np.nanmean(comb_all_other_values, axis=0)

    output = []
    for i in range(len(comb)):
        output.append((comb[i][0], values_mean[i]))
    return output

def bitmask_to_inverse(bitmask):
    """
    Index of every 0 in boolean array
    """
    if not type(bitmask) == np.array:
        bitmask = np.array(bitmask)
    return np.where(bitmask==0)[0]


def map_bitmask_to_lower(inverse_remove, ids_h, split_expression):
    """
    Maps higher level indizes to bitmask for lower level
    
    """
    temp_indstr1 = IndexedString(ids_h.raw_string(), split_expression=split_expression)

    temp_indstr2 = IndexedString(ids_h.inverse_removing(inverse_remove), split_expression=split_expression)
    return np.array([1 if x in temp_indstr2.inverse_vocab else 0 for x in temp_indstr1.inverse_vocab ])

def split_sentence(raw):
    return [sent.text for sent in nlp(raw).sents]

def create_baseline_sampling(size, advanced=True):
    if advanced == False:
        return np.ones((1, size))
    output = np.zeros((1+ 2*size, size))
    output[0, :] = np.ones((1, size))
    output[1:size+1, :] = np.eye(size)
    output[size+1:] = np.eye(size)*-1 +1
    return output


class MultiLevelSampling():
    def __init__(self, *args, **kwargs):
        self.parameters = kwargs
        self.explainers = []
        self.results_object = []
        self.results = []
        self.levels = len(self.parameters['split_expression'])
        self.individual = False
        for i in range(self.levels):
            explainer = IterativeLimeTextExplainer(**{j:self.parameters[j][i] for j in self.parameters})
            self.explainers.append(explainer)
        
    def explain_instance(self, text_instance, classifier_fn, **kwargs):
        
        #Combined mode: results from upper level will be combined to one string
        if not self.individual:
            blacklist_indexes = []
            for i in range(self.levels):
                #Explain
                self.explainers[i].blacklist = blacklist_indexes
                result = self.explainers[i].explain_instance(text_instance, classifier_fn, **kwargs)
                self.results.append(result)
                

                #Stop if no deeper level
                #TODO outsource this part to own function for better output
                if i +1 == self.levels:
                    return result

                #Sum together relevant strings
                combined_coefficients = ''
                for coeff in result.as_list():
                    combined_coefficients += ' ' + coeff[0]
                combined_coefficients
                t = [coeff[0] for coeff in result.as_list()]


                idx = IndexedString(text_instance, split_expression=self.parameters['split_expression'][i])
                def reverse_to_bitmask(idx, term):
                    return [1 if x in term else 0 for x in idx.inverse_vocab]

                bitmask = map_bitmask_to_lower(bitmask_to_inverse(reverse_to_bitmask(idx, t)), idx, split_expression='\W+')
                blacklist_indexes = np.where(bitmask==0)[0]
        
        #individual mode: results from upper level will be treated individually
        else:
            text_instances = [text_instance]
            
            results_individual = []
            results_combined = []
            for i in range(self.levels):
                temp_results = []
                for text in text_instances:
                    print(f'Explain string: {text}')
                    print('\n')
                    result = self.explainers[i].explain_instance(text, classifier_fn, **kwargs)
                    temp_results.append(result)
                results_individual.append(temp_results)
                temp_results_combined = combine_results([t.as_list() for t in temp_results])
                results_combined.append(temp_results_combined)
                text_instances = []
                for t in temp_results:
                    text_instances.extend([x[0] for x in t.as_list()])
                
                print(f'Data for next level:')
                for t in text_instances:
                    print(t)
                    print('\n')
                print('\n')
                if i +1 == self.levels:
                    self.results_individual = results_individual
                    self.results_combined = results_combined
                    return result

                


class Sampler:
    def __init__(self, size):
        self.data = []
        self.data.append(np.ones(size))
        self.size = size
        self.possible_indizes = np.arange(size)
        self.heat = 1
        self.heatCreated = 0
        self.current_permutations = itertools.combinations(np.arange(size), 1)
        
    def _to_bool(self, data):
        output = np.ones(self.size)
        output[data] = 0
        return output
    
    def sample(self, num_samples):
        if len(self.data) >= num_samples:
            return self.data[:num_samples]
        

        while(len(self.data) < num_samples and not self.heat > self.size):

            smpls_to_generate = num_samples - len(self.data)
            created = [self._to_bool(list(x)) for x in list(itertools.islice(self.current_permutations,
                                                                                    smpls_to_generate))]
            self.data.extend(created)
            if(len(created) == 0):
                self.heat+=1
                self.current_permutations = itertools.combinations(np.arange(self.size), self.heat)
        

        return self.data
    
class CacheLimeTextExplainer(LimeTextExplainer):
    def __init__(self, *args, **kwargs):
        super(CacheLimeTextExplainer, self).__init__(*args, **kwargs)
        self.number_of_generated_samples = 0
        self.accumulatedTime = 0
        self.cached_string = None
        self.labels = None
        self.distances = None
        self.data = []
        self.baseLineCreated = False
        self.advancedSampler = True
        self.samples = None
        self.blacklist = []
        self.random_state_choice = check_random_state(None if not 'random_state' in kwargs else kwargs['random_state']+10)
    
    
    def advanced_sampling(self, num_samples, samples_to_generate):
        
        data = np.ones((samples_to_generate, self.doc_size))
        data[:, self.blacklist]=0
        data_sampler = self.sampler.sample(num_samples)
        inverse_blacklist = np.array([x for x in np.arange(data.shape[1]) if x not in self.blacklist])
        
        
        sampled_arr = np.array(data_sampler[self.number_of_generated_samples:])
        if len(sampled_arr) == 0:
            return []
        if len(sampled_arr) < len(data):
            data = data[:len(sampled_arr)]
        
        data[:, inverse_blacklist] = sampled_arr
        return data
    
    def random_sampling(self, samples_to_generate):
        offset = 0
        data = np.ones((samples_to_generate, self.doc_size))
        data[:, self.blacklist]=0
        #If baseline is not created, we create it
        if not self.baseLineCreated:
            baseline = np.ones((1, self.doc_size))
            samples_to_generate -= len(baseline)
            if samples_to_generate <= 0:
                data = baseline
                samples_to_generate = 0
            else:
                data[:len(baseline), :] = baseline
            self.baseLineCreated = True
            offset = len(baseline)



        #sample number of features to pertubate

        sample = self.random_state.randint(1, self.doc_size+1-len(self.blacklist), samples_to_generate)
        inverse_blacklist = np.array([x for x in np.arange(data.shape[1]) if x not in self.blacklist])
        features_range = range(len(inverse_blacklist))
        for i, size in enumerate(sample):
            inactive = self.random_state_choice.choice(features_range, size, replace=False)
            data[i+offset, inverse_blacklist[inactive]] = 0
        return data
    
    def _LimeTextExplainer__data_labels_distances(self,
                                indexed_string,
                                classifier_fn,
                                num_samples,
                                distance_metric='cosine'):
        """Generates a neighborhood around a prediction.
        Generates neighborhood data by randomly removing words from
        the instance, and predicting with the classifier. Uses cosine distance
        to compute distances between original and perturbed instances.
        Args:
            indexed_string: document (IndexedString) to be explained,
            classifier_fn: classifier prediction probability function, which
                takes a string and outputs prediction probabilities. For
                ScikitClassifier, this is classifier.predict_proba.
            num_samples: size of the neighborhood to learn the linear model
            distance_metric: the distance metric to use for sample weighting,
                defaults to cosine similarity.
        Returns:
            A tuple (data, labels, distances), where:
                data: dense num_samples * K binary matrix, where K is the
                    number of tokens in indexed_string. The first row is the
                    original instance, and thus a row of ones.
                labels: num_samples * L matrix, where L is the number of target
                    labels
                distances: cosine distance between the original instance and
                    each perturbed instance (computed in the binary 'data'
                    matrix), times 100.
        """

        def distance_fn(x):
            return sklearn.metrics.pairwise.pairwise_distances(
                x, x[0], metric=distance_metric).ravel() * 100
        
        #Reset cache when prediction is new
        if self.cached_string != indexed_string.raw_string():
            self.cached_string = indexed_string.raw_string()
            self.sampler = Sampler(indexed_string.num_words() - len(self.blacklist))
            self.doc_size = indexed_string.num_words()
            self.number_of_generated_samples = 0
            self.labels = None
            self.distances = None
            self.data = None
            self.accumulatedTime = 0
            self.baseLineCreated = False
        
        
        doc_size = indexed_string.num_words()
        samples_to_generate = num_samples - self.number_of_generated_samples
        
        #If all wanted samples are already generated, we return them
        if samples_to_generate <= 0:
            return self.data[:num_samples], self.labels[:num_samples], self.distances[:num_samples]
        
        
        
        
        
        if self.advancedSampler:
            data = self.advanced_sampling(num_samples, samples_to_generate)
        else:
            data =self.random_sampling(samples_to_generate)
        
        
        if len(data) == 0:
            #no new sampled, return
            return self.data, self.labels, self.distances
        
        inverse_data = [indexed_string.inverse_removing(np.where(inactive==0)[0]) for inactive in data]
        labels = classifier_fn(inverse_data)
        distances = distance_fn(sp.sparse.csr_matrix(data))
        
        #cache results
        self.number_of_generated_samples += len(data)
        if self.labels  is not None:
            self.labels = np.append(self.labels, labels, axis=0)
        else:
            self.labels = labels
        if self.distances is not None:
            self.distances = np.append(self.distances, distances, axis=0)
        else:
            self.distances = distances
        if self.data  is not None:
            self.data = np.append(self.data, data, axis=0)
        else:
            self.data = data
        return self.data, self.labels, self.distances 



class IterativeLimeTextExplainer(CacheLimeTextExplainer):
    def __init__(self, *args, min_samples = 2,
                 max_samples=10000, step_size=1000,
                 error_measure=sklearn.metrics.mean_squared_error,
                 error_cutoff=0.001,
                 **kwargs):
        
        self.min_samples = min_samples
        self.max_samples = max_samples
        self.step_size = step_size
        self.error_measure = error_measure
        self.error_cutoff=error_cutoff
        self.results = []
        super(IterativeLimeTextExplainer, self).__init__(*args, **kwargs)
        
    def explain_instance(self, *args, **kwargs):
        #baseline
        kwargs['num_samples'] = self.min_samples
        exp = super(IterativeLimeTextExplainer, self).explain_instance(*args, **kwargs)
        last_coefficients = sorted(exp.as_list())
        base_offset = self.number_of_generated_samples
        last_sample_size = 0
        
        for i in np.arange(self.step_size + base_offset,
                           self.max_samples+self.step_size+base_offset,
                           self.step_size):
            kwargs['num_samples'] = i
            exp = super(IterativeLimeTextExplainer, self).explain_instance(*args, **kwargs)
            new_coefficients = sorted(exp.as_list())
            self.results.append(new_coefficients)
            padded = extend_explanation_words(last_coefficients, new_coefficients)
            error = self.error_measure(np.array([x[1] for x in padded[0]]), np.array([x[1] for x in padded[1]]))
            
            if len(self.data) == last_sample_size:
                return exp
            else:
                last_sample_size = len(self.data)
            if error <= self.error_cutoff:
                return exp
            last_coefficients = new_coefficients
        return exp    

class ES_LimeTextExplainer(LimeTextExplainer):
    def _LimeTextExplainer__data_labels_distances(self,
                                indexed_string,
                                classifier_fn,
                                num_samples,
                                distance_metric='cosine'):

        def distance_fn(x):
            return sklearn.metrics.pairwise.pairwise_distances(
                x, x[0], metric=distance_metric).ravel() * 100

        doc_size = indexed_string.num_words()
        sample = self.random_state.randint(1, doc_size + 1, num_samples - 1)
        features_range = range(doc_size)
        inverse_data = [indexed_string.raw_string()]
        data = np.flip(np.array([list(i) for i in itertools.product([0, 1], repeat = indexed_string.num_words())]))
        data = data[:-1]
        #ndata = data
        #for i in range(5):
        #    ndata = np.append(ndata, data, axis=0)
        #data = ndata
        inverse_data = [indexed_string.inverse_removing(np.where(inactive==0)[0]) for inactive in data]
        labels = classifier_fn(inverse_data)
        distances = distance_fn(sp.sparse.csr_matrix(data))
        return data, labels, distances