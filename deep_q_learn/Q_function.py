import tensorflow as tf

def Q_func(x, adj, w, embed, p, T, initialization_stddev=None,
           scope='', reuse=False, train=True, sess=None, pre_pooling_mlp_layers = 1, post_pooling_mlp_layers = 1):
    """
    x:      B x n_vertices.
    Placeholder for the current state of the solution.
    Each row of x is a binary vector encoding
    which vertices are included in the current partial solution.
    adj:    n_vertices x n_vertices.
    A placeholder for the adjacency matrix of the graph.
    w:      n_vertices x n_vertice.
    A placeholder for the weights matrix of the graph.
    """

    
    with tf.variable_scope(scope, reuse=False):
        if train:
            with tf.variable_scope('thetas'):
                theta1 = tf.Variable(tf.random_normal([p], stddev=initialization_stddev), name='theta1')
                theta2 = tf.Variable(tf.random_normal([p, p], stddev=initialization_stddev), name='theta2')
                theta3 = tf.Variable(tf.random_normal([p, p], stddev=initialization_stddev), name='theta3')
                theta4 = tf.Variable(tf.random_normal([p], stddev=initialization_stddev), name='theta4')
                theta5 = tf.Variable(tf.random_normal([2 * p], stddev=initialization_stddev), name='theta5')
                theta6 = tf.Variable(tf.random_normal([p, p], stddev=initialization_stddev), name='theta6')
                theta7 = tf.Variable(tf.random_normal([p, p], stddev=initialization_stddev), name='theta7')

            with tf.variable_scope('pre_pooling_MLP', reuse=False):
                Ws_pre_pooling = []; bs_pre_pooling = []
                for i in range(pre_pooling_mlp_layers):
                    Ws_pre_pooling.append(tf.Variable(tf.random_normal([p, p], stddev=initialization_stddev),
                                            name='W_MLP_pre_pooling_' + str(i)))
                    bs_pre_pooling.append(tf.Variable(tf.random_normal([p], stddev=initialization_stddev),
                                            name='b_MLP_pre_pooling_' + str(i)))

                Ws_post_pooling = []; bs_post_pooling = []
                for i in range(post_pooling_mlp_layers):
                    Ws_post_pooling.append(tf.Variable(tf.random_normal([p, p], stddev=initialization_stddev),
                                            name='W_MLP_post_pooling_' + str(i)))
                    bs_post_pooling.append(tf.Variable(tf.random_normal([p], stddev=initialization_stddev),
                                            name='b_MLP_post_pooling_' + str(i)))
        else:
            # load theta's and layers from the saved session
            prefix = "q_func"
            theta_list = [tf.convert_to_tensor(sess.run(prefix + "/thetas/theta" + str(i) + ":0"),
                            name='theta%d' % i) for i in range(1,8)]
            Ws_pre_pooling = [tf.convert_to_tensor((sess.run(prefix + "/pre_pooling_MLP/W_MLP_pre_pooling_%d:0" % i)))
                              for i in range(pre_pooling_mlp_layers)]
            bs_pre_pooling = [tf.convert_to_tensor(sess.run(prefix + "/pre_pooling_MLP/b_MLP_pre_pooling_%d:0" % i)) 
                              for i in range(pre_pooling_mlp_layers)]
            Ws_post_pooling = [tf.convert_to_tensor(sess.run(prefix + "/pre_pooling_MLP/W_MLP_post_pooling_%d:0" % i)) 
                               for i in range(post_pooling_mlp_layers)]
            bs_post_pooling = [tf.convert_to_tensor(sess.run(prefix + "/pre_pooling_MLP/b_MLP_post_pooling_%d:0" % i)) 
                               for i in range(post_pooling_mlp_layers)]
            # Unpack passed theta's recovered from training session.
            theta1,theta2,theta3,theta4,theta5,theta6,theta7 = theta_list

        B_adj = tf.transpose(adj, perm=[0, 2, 1])
        B_w = tf.transpose(w, perm=[0, 2, 1])
        # Define the mus
        # Loop over t
        for t in range(T):
            # First part of mu
            mu_part1 = tf.einsum('iv,k->ivk', x, theta1)

            # Second part of mu
            if t != 0:
                # Add some non linear transformation of the neighbors' embedding before pooling
                with tf.variable_scope('pre_pooling_MLP', reuse=False):
                    for i in range(pre_pooling_mlp_layers):
                        A_mu = tf.nn.relu(tf.einsum('kl,ivk->ivl', Ws_pre_pooling[i], A_mu) + bs_pre_pooling[i])
                        B_mu = tf.nn.relu(tf.einsum('kl,ivk->ivl', Ws_pre_pooling[i], B_mu) + bs_pre_pooling[i])

                A_mu_part2 = tf.einsum('kl,ivk->ivl', theta2, tf.einsum('ivu,iuk->ivk', adj, A_mu))
                B_mu_part2 = tf.einsum('kl,ivk->ivl', theta2, tf.einsum('ivu,iuk->ivk', B_adj, B_mu))
                # Add some non linear transformations of the pooled neighbors' embeddings
                with tf.variable_scope('post_pooling_MLP', reuse=False):
                    for i in range(post_pooling_mlp_layers):
                        A_mu_part2 = tf.nn.relu(tf.einsum('kl,ivk->ivl', Ws_post_pooling[i], A_mu_part2) + bs_post_pooling[i])
                        B_mu_part2 = tf.nn.relu(tf.einsum('kl,ivk->ivl', Ws_post_pooling[i], B_mu_part2) + bs_post_pooling[i])

            # Third part of mu
            A_mu_part3_0 = tf.einsum('ikvu->ikv', tf.nn.relu(tf.einsum('k,ivu->ikvu', theta4, w)))
            A_mu_part3_1 = tf.einsum('kl,ilv->ivk', theta3, A_mu_part3_0)
            B_mu_part3_0 = tf.einsum('ikvu->ikv', tf.nn.relu(tf.einsum('k,ivu->ikvu', theta4, B_w)))
            B_mu_part3_1 = tf.einsum('kl,ilv->ivk', theta3, B_mu_part3_0)

            # All all of the parts of mu and apply ReLui
            if t != 0:
                A_mu = tf.nn.relu(tf.add(mu_part1 + A_mu_part2, A_mu_part3_1, name='A_mu_' + str(t)))
                B_mu = tf.nn.relu(tf.add(mu_part1 + B_mu_part2, B_mu_part3_1, name='B_mu_' + str(t)))
            else:
                # Matrix NxK
                A_mu = embed
                B_mu = embed
                #mu = tf.nn.relu(tf.add(mu_part1, mu_part3_1, name='mu_' + str(t)))

        # Define the Qs
        A_Q_part1 = tf.einsum('kl,ivk->ivl', theta6, tf.einsum('ivu,iuk->ivk', adj, A_mu))
        A_Q_part2 = tf.einsum('kl,ivk->ivl', theta7, A_mu)
        B_Q_part1 = tf.einsum('kl,ivk->ivl', theta6, tf.einsum('ivu,iuk->ivk', B_adj, B_mu))
        B_Q_part2 = tf.einsum('kl,ivk->ivl', theta7, B_mu)
        
        return tf.identity(tf.einsum('k,ivk->iv', theta5,
                                     tf.nn.relu(tf.concat([A_Q_part1, A_Q_part2], axis=2))),
                           name='A_Q'), tf.identity(tf.einsum('k,ivk->iv', theta5,
                                     tf.nn.relu(tf.concat([B_Q_part1, B_Q_part2], axis=2))),
                           name='B_Q')