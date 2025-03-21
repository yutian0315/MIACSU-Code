from __future__ import division
from __future__ import print_function

import time

from utils import *
from models import GCN, MLP, ResGCN
from visualize import *
import numpy as np
from sklearn.metrics import confusion_matrix, roc_auc_score
from scipy import sparse

# Set random seed
seed = 123
np.random.seed(seed)
# tf.set_random_seed(seed)

# Settings
flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string('adj_type', 'age', 'Adjacency matrix creation')
# 'cora', 'citeseer', 'pubmed', 'tadpole' # Please don't work with citation networks!!
flags.DEFINE_string('dataset', 'tadpole', 'Dataset string.')
# 'gcn(re-parametrization trick)', 'gcn_cheby(simple_gcn)', 'dense', 'res_gcn_cheby(our model)'
flags.DEFINE_string('model', 'res_gcn_cheby', 'Model string.')
flags.DEFINE_float('learning_rate', 0.005, 'Initial learning rate.')
flags.DEFINE_integer('epochs', 150, 'Number of epochs to train.')
flags.DEFINE_integer('hidden1', 30, 'Number of units in hidden layer 1.')
flags.DEFINE_integer('hidden2', 3, 'Number of units in hidden layer 2.')
flags.DEFINE_integer('hidden3', 3, 'Number of units in hidden layer 3.')
flags.DEFINE_float('dropout', 0.3, 'Dropout rate (1 - keep probability).')
flags.DEFINE_float('weight_decay', 5e-4, 'Weight for L2 loss on embedding matrix.')
flags.DEFINE_integer('start_stopping', 100, 'Number of epochs before checking early stopping')
flags.DEFINE_integer('early_stopping', 30, 'Tolerance for early stopping (# of epochs).')
flags.DEFINE_bool('featureless', False, 'featureless')
flags.DEFINE_bool('is_pool', True, 'Use max-pooling for InceptionGCN model')
flags.DEFINE_bool('is_skip_connection', False, 'Add skip connections to model')


# Loading data
# def load_data():
    # if FLAGS.dataset == 'tadpole':
        # features is in sparse format
        # node weights used for weighted loss
###........ Please see utils to check the load_ABIDE_data

    # else:
    # adj, features, y_train, y_val, y_test, train_mask, val_mask, test_mask, all_labels, one_hot_labels = load_citation_data(FLAGS.dataset)
    #     adj, features, all_labels, one_hot_labels = load_citation_data(FLAGS.dataset)
    #     dense_features = features
    #     node_weights = np.ones((dense_features.shape[0],))
    #     Some preprocessing
        # features = preprocess_features(features)
        # if FLAGS.dataset == 'cora':
        #     num_class = 7
        # elif FLAGS.dataset == 'citeseer':
        #     num_class = 6
        # else:
        #     num_class = 3
    # return features, all_labels, one_hot_labels, node_weights, dense_features, num_class


# creating placeholders and support based on number of supports fed to network
def create_support_placeholder(model_name, num_supports, adj):
    if model_name == 'gcn' or model_name == 'dense':
        support = [preprocess_adj(adj)]
    else:
        support = chebyshev_polynomials(adj, num_supports - 1)
    placeholders = {
        'support': [tf.sparse_placeholder(tf.float32, name='support_{}'.format(i)) for i in range(num_supports)],
     ##............ Shape is explicitly defined.
        'features': tf.sparse_placeholder(tf.float32, shape=tf.constant([871,2000], dtype=tf.int64)), ##
        'labels': tf.placeholder(tf.float32, shape=(None, one_hot_labels.shape[1])),
        'labels_mask': tf.placeholder(tf.float32),
        'dropout': tf.placeholder_with_default(0., shape=()),
        'num_features_nonzero': tf.placeholder(tf.int32)  # helper variable for sparse dropout
    }
    return support, placeholders


def avg_std_log(train_accuracy, val_accuracy, test_accuracy,test_Acc,test_auc,test_sen,test_spe,test_f1):
    # average
    train_avg_acc = np.mean(train_accuracy)
    val_avg_acc = np.mean(val_accuracy)
    test_avg_acc = np.mean(test_accuracy)

    test_avg_Acc = np.mean(test_Acc)
    test_avg_auc = np.mean(test_auc)
    test_avg_sen = np.mean(test_sen)
    test_avg_spe = np.mean(test_spe)
    test_avg_f1 = np.mean(test_f1)



    # std
    train_std_acc = np.std(train_accuracy)
    val_std_acc = np.std(val_accuracy)
    test_std_acc = np.std(test_accuracy)
    test_std_Acc = np.std(test_Acc)
    test_std_auc = np.std(test_auc)
    test_std_sen = np.std(test_sen)
    test_std_spe = np.std(test_spe)
    test_std_f1 = np.std(test_f1)

    print('Average accuracies:')
    print('train_avg: ', train_avg_acc, '±', train_std_acc)
    print('val_avg: ', val_avg_acc, '±', val_std_acc)
    print('test_avg: ', test_avg_acc, '±', test_std_acc)

    print('test_avg_Acc: {:.4}% ± {:.4}% '.format(test_avg_Acc*100, test_std_Acc*100))
    print('test_avg_auc: {:.4}% ± {:.4}% '.format(test_avg_auc*100, test_std_auc*100))
    print('test_avg_sen: {:.4}% ± {:.4}% '.format(test_avg_sen*100, test_std_sen*100))
    print('test_avg_spe: {:.4}% ± {:.4}% '.format(test_avg_spe*100, test_std_spe*100))
    print('test_avg_f1: {:.4}% ± {:.4}% '.format(test_avg_f1*100, test_std_f1*100))



    return train_avg_acc, train_std_acc, val_avg_acc, val_std_acc, test_avg_acc, test_std_acc


def train_k_fold(model_name, support, placeholders, is_pool=False, is_skip_connection=True,
                 locality1=1, locality2=2, locality_sizes=None):
    """model_name: name of model (using option defined for FLAGS.model in top
       locality1 & locality2: values of k for 2 GC blocks of gcn_cheby(simple gcn model)
       locality_sizes: locality sizes included in each GC block for res_gcn_cheby(our proposed model)
    """
    # Create model
    logging = False
    if model_name == 'res_gcn_cheby':
        model = ResGCN(placeholders, input_dim=2000, logging=logging, locality_sizes=locality_sizes,
                       is_pool=is_pool, is_skip_connection=is_skip_connection)

    elif model_name == 'gcn':
        model = GCN(placeholders, input_dim=2000, logging=logging)

    elif model_name == 'gcn_cheby':
        locality = [locality1, locality2]  # locality sizes of different blocks
        model = GCN(placeholders, input_dim=2000, logging=logging, is_simple=True,
                    is_skip_connection=is_skip_connection, locality=locality)

    elif model_name == 'dense':
        model = MLP(placeholders, input_dim=2000, logging=logging)

    else:
        raise ValueError('Invalid argument for model: ' + str(model_name))

    # Define model evaluation function
    def evaluate(features, support, labels, mask, placeholders):
        t_test = time.time()
        feed_dict_val = construct_feed_dict(features, support, labels, mask, placeholders)
        outs_val = sess.run([model.loss, model.accuracy, merged_summary], feed_dict=feed_dict_val)
        return outs_val[0], outs_val[1], outs_val[2], (time.time() - t_test)

    ##...........change to dense_features
    num_nodes = dense_features.shape[0]
    num_folds = 10
    fold_size = int(num_nodes / num_folds)

    # list of results including accuracy, auc, confusion matrix
    train_accuracy = []
    val_accuracy = []
    test_accuracy = []
    test_Acc = []
    test_auc = []
    test_sen = []
    test_spe = []
    test_f1 = []
    test_confusion_matrices = []
    test_auc = []

    # index of fold for validation set and test set
    val_part = 0
    test_part = 1

    # storing number of epochs of each fold
    num_epochs = []

    # shape of features
    print('whole features shape: ', dense_features.shape)

    # Num_folds cross validation
    for fold in range(num_folds):
        print('Starting fold {}'.format(fold + 1))

        # rotating folds of val and test
        val_part = (val_part + 1) % 10
        test_part = (test_part + 1) % 10

        # defining train, val and test mask
        train_mask = np.ones((num_nodes,), dtype=np.bool)
        val_mask = np.zeros((num_nodes,), dtype=np.bool)
        test_mask = np.zeros((num_nodes,), dtype=np.bool)
        train_mask[val_part * fold_size: min((val_part + 1) * fold_size, num_nodes)] = 0
        train_mask[test_part * fold_size: min((test_part + 1) * fold_size, num_nodes)] = 0
        val_mask[val_part * fold_size: min((val_part + 1) * fold_size, num_nodes)] = 1
        test_mask[test_part * fold_size: min((test_part + 1) * fold_size, num_nodes)] = 1

        # defining train, val and test labels
        y_train = np.zeros(one_hot_labels.shape)
        y_val = np.zeros(one_hot_labels.shape)
        y_test = np.zeros(one_hot_labels.shape)
        y_train[train_mask, :] = one_hot_labels[train_mask, :]
        y_val[val_mask, :] = one_hot_labels[val_mask, :]
        y_test[test_mask, :] = one_hot_labels[test_mask, :]

        # number of samples in each set
        print('# of training samples: ', np.sum(train_mask))
        print('# of validation samples: ', np.sum(val_mask))
        print('# of testing samples: ', np.sum(test_mask))

        # 没看懂
        tmp_labels = [item + 1 for item in all_labels]
        train_labels = train_mask * tmp_labels
        val_labels = val_mask * tmp_labels
        test_labels = test_mask * tmp_labels

        # distribution of train, val and test set over classes
        train_class = [train_labels.tolist().count(i) for i in range(1, num_class + 1)]
        print('train class distribution:', train_class)
        val_class = [val_labels.tolist().count(i) for i in range(1, num_class + 1)]
        print('val class distribution:', val_class)
        test_class = [test_labels.tolist().count(i) for i in range(1, num_class + 1)]
        print('test class distribution:', test_class)

        # saving initial boolean masks for later use
        init_train_mask = train_mask
        init_val_mask = val_mask
        init_test_mask = test_mask

        # changing mask for having weighted loss
        #train_mask = node_weights * train_mask
        #val_mask = node_weights * val_mask
        #test_mask = node_weights * test_mask

        labeled_ind = [i for i in range(num_nodes) if train_mask[i] == True]

        ###..........dense_features and no of features
        features_modi = Reader.feature_selection(dense_features, all_labels, labeled_ind, 2000)

        features_modi = sparse_to_tuple(sp.coo_matrix(features_modi)) # 871 * 2000 转三元组稀疏矩阵
        #features_modi = sparse.coo_matrix(features_modi)
        #features_modi = sparse_to_tuple(features_modi)
        # Initialize session
        config = tf.ConfigProto(device_count={'GPU': 1})
        sess = tf.Session(config=config)

        # Session with GPU
        # config = tf.ConfigProto()
        # config.gpu_options.allow_growth = True
        # gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.9)
        # sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))

        # Initialize variables
        sess.run(tf.global_variables_initializer())

        # loss and accuracy scalar curves
        if model_name == 'res_gcn_cheby':
            l1 = locality_sizes[0]
            l2 = locality_sizes[1]
        else:
            l1 = locality1
            l2 = locality2
        tf.summary.scalar(name='{}_{}_loss_fold_{}'.format(l1, l2, fold + 1), tensor=model.loss)
        tf.summary.scalar(name='{}_{}_accuracy_fold_{}'.format(l1, l2, fold + 1),
                          tensor=model.accuracy)
        merged_summary = tf.summary.merge_all()

        # defining train, test and val writers in /tmp/model_name/ path
        train_writer = tf.summary.FileWriter(logdir='/tmp/' + model_name +
                                                    '_{}_{}/train_fold_{}/'.format(l1, l2, fold + 1))
        test_writer = tf.summary.FileWriter(logdir='/tmp/' + model_name +
                                                   '_{}_{}/test_fold_{}/'.format(l1, l2, fold + 1))
        val_writer = tf.summary.FileWriter(logdir='/tmp/' + model_name +
                                                  '_{}_{}/val_fold_{}/'.format(l1, l2, fold + 1))
        # Train model
        cost_val = []
        train_results = []
        for epoch in range(FLAGS.epochs):
            t = time.time()

            # Construct feed dictionary for training
            ##...........Feature_modi
            feed_dict = construct_feed_dict(features_modi, support, y_train, train_mask, placeholders)
            feed_dict.update({placeholders['dropout']: FLAGS.dropout})

            # Training step
            train_results = sess.run([model.opt_op, model.loss, model.accuracy, merged_summary], feed_dict=feed_dict)
            train_writer.add_summary(train_results[-1], epoch)

            ##...........Feature_modi
            # Evaluation on val set
            val_cost, val_acc, val_summary, duration = evaluate(features_modi, support, y_val, val_mask, placeholders)
            cost_val.append(val_cost)
            val_writer.add_summary(val_summary, epoch)

            ##...........Feature_modi
            # Evaluation on test set
            test_cost, test_acc, test_summary, test_duration = evaluate(features_modi, support, y_test, test_mask, placeholders)
            test_writer.add_summary(test_summary, epoch)

            # Print results of train, val and test
            print("Epoch:", '%04d' % (epoch + 1), "train_loss=", "{:.5f}".format(train_results[1]),
                  "train_acc=", "{:.5f}".format(train_results[2]), "val_loss=", "{:.5f}".format(val_cost),
                  "val_acc=", "{:.5f}".format(val_acc), "time=", "{:.5f}".format(time.time() - t))
            print("Test set results:", "test_loss=", "{:.5f}".format(test_cost),
                  "test_accuracy=", "{:.5f}".format(test_acc))

            # Check val loss for early stopping
            if epoch > max(FLAGS.early_stopping, FLAGS.start_stopping) and cost_val[-1] > np.mean(cost_val[-(FLAGS.early_stopping+1):-1]):
                print("Early stopping on epoch {}...".format(epoch + 1))
                break

        num_epochs.append(epoch)
        print("Optimization Finished!")

        # Collecting final results of train, test & val
        train_accuracy.append(train_results[2])
        val_accuracy.append(val_acc)
        test_accuracy.append(test_acc)

        # Visualizing layers' embedding
        # if model_name == 'res_gcn_cheby':
            # path = '/tmp/' + model_name + '_{}_{}'.format(l1, l2) + '/layers/' + \
            #        'fold_{}/'.format(fold)
            # layer_writer = tf.summary.FileWriter(logdir=path)
            # write_meta_data_labels(all_labels, path)
            # visualize_node_embeddings_resgcn(features, support, placeholders, sess, model, layer_writer, FLAGS.is_pool,
            #                                  path, len(locality_sizes))
            # layer_writer.close()
            # activations = get_activations(features, support, placeholders, sess, model)
            # l1_act = activations[0][1]
            # l2_act = activations[1][1]
            # graph_visualize(adj, dense_features, all_labels, 15, l1_act)
            # graph_visualize(adj, dense_features, all_labels, 15, l2_act)
        def result(output, labels):
            from scipy.special import softmax
            # output = output.detach().numpy()
            # label = labels.detach().numpy()
            pred_score = softmax(output, axis=1)
            # preds = output.max(1)[1]
            preds = (pred_score == pred_score.max(axis=1, keepdims=1)).astype(int)
            preds = preds[:, 1]
            import sklearn
            result = []

            acc = sklearn.metrics.accuracy_score(labels, preds)
            auc = sklearn.metrics.roc_auc_score(labels, preds)
            f1 = sklearn.metrics.f1_score(labels, preds)
            cm = sklearn.metrics.confusion_matrix(labels, preds)
            # recall = sklearn.metrics.recall_score(labels, preds)
            sen = cm[1][1] / (cm[1][1] + cm[1][0])
            spe = cm[0][0] / (cm[0][0] + cm[0][1])

            result.append(acc)
            result.append(auc)
            result.append(sen)
            result.append(spe)
            result.append(f1)

            return result, pred_score, preds, labels
        # Confusion matrix on test set
        def write_raw_score(f, preds, preds_labels, labels, results):
            for index, pred in enumerate(preds):
                label = str(labels[index])
                preds_label = str(preds_labels[index])
                pred = "__".join(map(str, list(pred)))
                f.write(pred + '__' + preds_label + '__' + label + '\n')
            f.write('ACC:  ' + str(results[0]) + '\n')
            f.write('AUC:  ' + str(results[1]) + '\n')
            f.write('SEN:  ' + str(results[2]) + '\n')
            f.write('SPE:  ' + str(results[3]) + '\n')
            f.write('F1:  ' + str(results[4]) + '\n')



        feed_dict = dict()
        feed_dict.update({placeholders['features']: features_modi})##...........Feature_modi
        feed_dict.update({placeholders['support'][i]: support[i] for i in range(len(support))})
        feed_dict.update({placeholders['num_features_nonzero']: features_modi[1].shape})##...........Feature_modi
        model_outputs = sess.run(model.outputs, feed_dict=feed_dict)
        prediction = np.argmax(model_outputs, axis=1)[init_test_mask]
        confusion_mat = confusion_matrix(y_true=np.asarray(all_labels)[init_test_mask], y_pred=prediction,
                                         labels=[i for i in range(num_class)])
        y_true = np.asarray(all_labels)[init_test_mask]-1
        results, pred, preds_label, lab = result(model_outputs[init_test_mask], np.asarray(all_labels)[init_test_mask]-1)
        test_Acc.append(results[0])
        test_auc.append(results[1])
        test_sen.append(results[2])
        test_spe.append(results[3])
        test_f1.append(results[4])
        f = open('./checkpoint/fold_{}.txt'.format(fold), 'w')
        write_raw_score(f, pred, np.squeeze(preds_label.astype(int)), np.squeeze(lab.astype(int)), results)
        f.close()

        test_confusion_matrices.append(confusion_mat)
        print('Confusion matrix of test set:')
        print(confusion_mat)

        # Roc auc score on test set
        # auc = roc_auc_score(y_true=one_hot_labels[init_test_mask, :], y_score=model_outputs[init_test_mask, :])
        # test_auc.append(auc)
        # print('Test auc: {:.4f}'.format(auc))
        print('--------')

        # Closing writers
        train_writer.close()
        test_writer.close()
        val_writer.close()
        sess.close()

    if model_name == 'gcn_cheby':
        print('Results of k1={} k2={}'.format(locality1, locality2))

    elif model_name == 'gcn':
        print('Results of re-parametrization model')

    elif model_name == 'res_gcn_cheby':
        print('Results of res_gcn with localities of: ', locality_sizes)

    else:
        print('Results of 3 layer dense neural network')

    print('Average number of epochs: {:.3f}'.format(np.mean(num_epochs)))
    print('Accuracy on {} folds'.format(num_folds))
    print('train:', train_accuracy)
    print('val', val_accuracy)
    print('test', test_accuracy)
    print()

    # print('Test auc on {} folds'.format(num_folds))
    # print(test_auc)
    # print()
    #
    # test_avg_auc = np.mean(test_auc)
    # print('Average test auc on {} folds'.format(num_folds))
    # print(test_avg_auc, '±', np.std(test_auc))

    return train_accuracy, val_accuracy, test_accuracy,test_Acc,test_auc,test_sen,test_spe,test_f1

gender_adj, site_adj, mixed_adj, features, all_labels, one_hot_labels, dense_features = load_ABIDE_data()
adj_dict = {'gender': gender_adj, 'site': site_adj, 'mixed': mixed_adj}
num_class = 2

support, placeholders = create_support_placeholder(FLAGS.model, 3 + 1, mixed_adj)

train_acc, val_acc, test_acc,test_Acc,test_auc,test_sen,test_spe,test_f1 = train_k_fold('gcn_cheby', support, placeholders,locality1=4, locality2=4)

train_avg_acc, train_std_acc, val_avg_acc, val_std_acc, test_avg_acc, test_std_acc = avg_std_log(train_acc, val_acc, test_acc,test_Acc,test_auc,test_sen,test_spe,test_f1)