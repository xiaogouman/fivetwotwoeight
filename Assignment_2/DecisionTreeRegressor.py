import numpy as np
import os
import json
import operator

class MyDecisionTreeRegressor():
    def __init__(self, max_depth=5, min_samples_split=1):
        '''
        Initialization
        :param max_depth: type: integer
        maximum depth of the regression tree. The maximum
        depth limits the number of nodes in the tree. Tune this parameter
        for best performance; the best value depends on the interaction
        of the input variables.
        :param min_samples_split: type: integer
        minimum number of samples required to split an internal node:

        root: type: dictionary, the root node of the regression tree.
        '''

        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None
        
    def get_groups(self, j, s, data):
        left_data = []
        right_data = []
        for each_data in data:
            if each_data[j] <= s:
                left_data.append(each_data)
            else:
                right_data.append(each_data)
        return np.array(left_data), np.array(right_data)    
    
    def split_data(self, data):
        min_error = np.finfo(float).max
        split_variable = 0
        split_threshold = 0
        left_mean = 0
        right_mean = 0
        my_left_data = []
        my_right_data = []
        for j in range(data.shape[1]-1):
            x_j = data[:,j]
            for i in range(len(x_j)):
                # threshold
                s = x_j[i]
                left_data, right_data = self.get_groups(j, s, data)
                if len(left_data) > 0 and len(right_data) > 0:
                    left_y, right_y = left_data[:,-1], right_data[:,-1]
                    
                    c1, c2 = np.mean(left_y), np.mean(right_y)
                    error = sum((left_y - c1)*(left_y - c1)) + sum((right_y - c2)*(right_y - c2))
                    if error < min_error:
                        min_error, split_variable, split_threshold, left_mean, right_mean, my_left_data, my_right_data = \
                            error, j, s, c1, c2, left_data, right_data

        return {'splitting_variable': split_variable, 'splitting_threshold': split_threshold,
                'left': left_mean, 'right': right_mean, 'groups': [my_left_data, my_right_data]}

    def split(self, node, depth):
        groups = node['groups']
        del node['groups']

        if depth == self.max_depth:
            return
        else:
            if len(groups[0]) >= self.min_samples_split:
                node['left'] = self.split_data(groups[0])
                self.split(node['left'], depth+1)
            if len(groups[1]) >= self.min_samples_split:
                node['right'] = self.split_data(groups[1])
                self.split(node['right'], depth+1)

    def fit(self, X, y):
        '''
        Inputs:
        X: Train feature data, type: numpy array, shape: (N, num_feature)
        Y: Train label data, type: numpy array, shape: (N,)

        You should update the self.root in this function.
        '''
        y = np.reshape(y, (len(y), 1))
        data = np.append(X, y, axis=1)
        self.root = self.split_data(data)
        self.split(self.root, 1)

    def traverse_tree(self, node, x):
        if isinstance(node, float):
            return node
        if x[node['splitting_variable']] <= node['splitting_threshold']:
            return self.traverse_tree(node['left'], x)
        else:
            return self.traverse_tree(node['right'], x)

    def predict(self, X):
        '''
        :param X: Feature data, type: numpy array, shape: (N, num_feature)
        :return: y_pred: Predicted label, type: numpy array, shape: (N,)
        '''
        y_pred = []
        for x in X:
            y_pred.append(self.traverse_tree(self.root, x))
        return y_pred

    def get_model_string(self):
        model_dict = self.root
        return model_dict

    def save_model_to_json(self, file_name):
        model_dict = self.root
        with open(file_name, 'w') as fp:
            json.dump(model_dict, fp)


# For test
if __name__=='__main__':
    for i in range(3):
        x_train = np.genfromtxt("Test_data" + os.sep + "x_" + str(i) +".csv", delimiter=",")
        y_train = np.genfromtxt("Test_data" + os.sep + "y_" + str(i) +".csv", delimiter=",")

        for j in range(2):
            tree = MyDecisionTreeRegressor(max_depth=5, min_samples_split=j + 2)
            tree.fit(x_train, y_train)

            model_string = tree.get_model_string()

            with open("Test_data" + os.sep + "decision_tree_" + str(i) + "_" + str(j) + ".json", 'r') as fp:
                test_model_string = json.load(fp)

            print(operator.eq(model_string, test_model_string))

            y_pred = tree.predict(x_train)

            y_test_pred = np.genfromtxt("Test_data" + os.sep + "y_pred_decision_tree_"  + str(i) + "_" + str(j) + ".csv", delimiter=",")
            print(np.square(y_pred - y_test_pred).mean() <= 10**-10)

