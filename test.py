import matplotlib.pyplot as plt
from time import time

from gem.utils      import graph_util, plot_util
from gem.evaluation import visualize_embedding as viz
from gem.evaluation import evaluate_graph_reconstruction as gr

from gem.embedding.gf       import GraphFactorization
from gem.embedding.hope     import HOPE
from gem.embedding.lap      import LaplacianEigenmaps
from gem.embedding.lle      import LocallyLinearEmbedding
from gem.embedding.node2vec import node2vec
from gem.embedding.sdne     import SDNE
import os
import keras.backend.tensorflow_backend as K

# File that contains the edges. Format: source target
# Optionally, you can add weights as third column: source target weight
#edge_f = os.environ['SEML_DATA']+'/output/all/all.edgelist'
edge_f = os.environ['SEML_DATA']+'/output/all2/all2.edgelist'

# Specify whether the edges are directed
isDirected = True

# Load graph
G = graph_util.loadGraphFromEdgeListTxt(edge_f, directed=isDirected)
G = G.to_directed()

models = []
# You can comment out the methods you don't want to run
#models.append(("GraphFactorization",GraphFactorization(2, 50000, 1*10**-4, 1.0)))
#models.append(("HOPE",HOPE(4, 0.01)))
#models.append(("LaplacianEigenmaps",LaplacianEigenmaps(2)))
#models.append(("LocallyLinearEmbedding",LocallyLinearEmbedding(2)))
#models.append(("node2vec",node2vec(2, 1, 80, 10, 10, 1, 1)))
models.append(("SDNE",SDNE(d=2, beta=5, alpha=1e-5, nu1=1e-6, nu2=1e-6, K=3,n_units=[50, 15,], rho=0.3, n_iter=50, xeta=0.01,n_batch=500,
                modelfile=['./intermediate/enc_model.json', './intermediate/dec_model.json'],
                weightfile=['./intermediate/enc_weights.hdf5', './intermediate/dec_weights.hdf5'])))


print(G.number_of_nodes())
print(G.number_of_edges())
for (name,embedding) in models:

    print ('Num nodes: %d, num edges: %d' % (G.number_of_nodes(), G.number_of_edges()))
    t1 = time()
    # Learn embedding - accepts a networkx graph or file with edge list
    with K.tf.device('/gpu:3'):
        K.get_session()#K.tf.Session(config=K.tf.ConfigProto(allow_soft_placement=True, log_device_placement=True)))
        Y, t = embedding.learn_embedding(graph=G, edge_f=None, is_weighted=True, no_python=True)
        print (embedding._method_name+':\n\tTraining time: %f' % (time() - t1))
        # Evaluate on graph reconstruction
        MAP, prec_curv = gr.evaluateStaticGraphReconstruction(G, embedding, Y, None)
    #---------------------------------------------------------------------------------
    print(("\tMAP: {} \t preccision curve: {}\n\n\n\n"+'-'*100).format(MAP,prec_curv))
    #---------------------------------------------------------------------------------
    # Visualize
    viz.plot_embedding2D(embedding.get_embedding(), di_graph=G, node_colors=None)
    plt.savefig(name+".png")
    #plt.show()
    plt.clf()
    
