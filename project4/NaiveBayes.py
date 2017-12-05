import pandas
import numpy as np
import sys
import os

NUM_FOLDS = 5 # Number of folds in our classifier

# Averages for each feature found in the spambase documentation
FEATURE_MEANS = [.10455, .21301, .28066, .065425, .31222, .095901, .11421, .10529, .090067, .23941,
                 .059824, .5417, .09393, .058626, .049205, .24885, .13259, .18474, 1.6621, .085577,
                 .80976, .1212, .10165, .094269, .5495, .26538, .7673, .12484, .098915, .10285,
                 .064753, .047048, .097299, .047835, .10541, .097477, .13695, .013201, .078629, .064834,
                 .043667, .13234, .046099, .079196, .30122, .17982, .0054445, .031869, .038575, .13903,
                 .016976, .26907, .075811, .044238, 5.1915, 52.173, 283.29, .39404]

# Split the dataset into NUM_FOLDS partitions for cross-validation later on
def generate_folds(dataset):
    if dataset is None:
        return None

    first_fold = []
    second_fold = []
    third_fold = []
    fourth_fold = []
    fifth_fold = []

    '''for index, row in dataset.iterrows():
        if (index) % 5 == 0:
            first_fold.append(row)
        elif (index-1) % 5 == 0:
            second_fold.append(row)
        elif (index-2) % 5 == 0:
            third_fold.append(row)
        elif (index-3) % 5 == 0:
            fourth_fold.append(row)
        elif (index+1) % 5 == 0:
            fifth_fold.append(row)'''
    first_fold = dataset.iloc[::5, :]
    second_fold = dataset.iloc[1::5, :]
    third_fold = dataset.iloc[2::5, :]
    fourth_fold = dataset.iloc[3::5, :]
    fifth_fold = dataset.iloc[4::5, :]

    folds = [first_fold, second_fold, third_fold, fourth_fold, fifth_fold]
    '''print("num folds: " + str(NUM_FOLDS))
    print("first fold: " + str(len(folds[0])))
    print("second fold: " + str(len(folds[1])))
    print("third fold: " + str(len(folds[2])))
    print("fourth fold: " + str(len(folds[3])))
    print("fifth fold: " + str(len(folds[4])) + "\n")'''
    return folds

def train(fold_number, dataset, folds):
    testing_set = folds[fold_number]
    training_set = None

    # Generate the training set based on the k-1 folds that aren't the testing set
    for i in range(0, NUM_FOLDS):
        if training_set is None and not i == fold_number:
            training_set = folds[i]
        elif not i == fold_number:
            training_set = training_set.append(folds[i])

    num_spam = len(training_set.loc[training_set[57] == 1])
    num_non_spam = len(training_set.loc[training_set[57] == 0])
    num_spam_dev = len(testing_set.loc[testing_set[57] == 1])
    num_non_spam_dev = len(testing_set.loc[testing_set[57] == 0])

    pos_neg_train_dev = (num_spam, num_non_spam, num_spam_dev, num_non_spam_dev)

    under_spam = []
    over_spam = []
    under_not_spam = []
    over_not_spam = []
    for i in range(0, 57): # Iterate over the 57 feature columns (but not the 58th column, the class label)
        under_spam_freq = float(len(training_set.loc[(training_set[57] == 1) & (training_set[i] <= FEATURE_MEANS[i])])) / num_spam
        if under_spam_freq == 0:
            under_spam_freq = .0014
        over_spam_freq = float(len(training_set.loc[(training_set[57] == 1) & (training_set[i] > FEATURE_MEANS[i])])) / num_spam
        if over_spam_freq == 0:
            over_spam_freq = .0014
        under_not_spam_freq = float(len(training_set.loc[(training_set[57] == 0) & (training_set[i] <= FEATURE_MEANS[i])])) / num_non_spam
        if under_not_spam_freq == 0:
            under_not_spam_freq = .0014
        over_not_spam_freq = float(len(training_set.loc[(training_set[57] == 0) & (training_set[i] > FEATURE_MEANS[i])])) / num_non_spam
        if over_not_spam_freq == 0:
            over_not_spam_freq = .0014
        under_spam.append( under_spam_freq ) # Pr(f <= mean | spam)
        over_spam.append( over_spam_freq ) # Pr(f > mean | spam)
        under_not_spam.append( under_not_spam_freq ) # Pr(f <= mean | not spam)
        over_not_spam.append( over_not_spam_freq ) # Pr(f > mean | not spam)

    prob_spam = float(num_spam) / (num_spam + num_non_spam)
    prob_non_spam = float(num_non_spam) / (num_spam + num_non_spam)

    correct = 0
    wrong = 0
    false_positives = 0
    false_negatives = 0
    positive_samples = 0
    negative_samples = 0
    for index, row in testing_set.iterrows():
        spam_prob = prob_spam
        non_spam_prob = prob_non_spam
        #if index == 0:
            #print("start spam: " + str(spam_prob) + ", start not spam: " + str(non_spam_prob))
        for i in range(0, 57):
            feature_val = row[i]
            if feature_val <= FEATURE_MEANS[i]:
                spam_prob *= under_spam[i]
                non_spam_prob *= under_not_spam[i]
                #if index == 0:
                    #print("feature: " + str(feature_val) + ", mean: " + str(FEATURE_MEANS[i]) + ", spam prob: " + str(spam_prob) + ", not spam prob: " + str(non_spam_prob) + ", under spam i: " + str(under_spam[i]) + ", under not spam i: " + str(under_not_spam[i]))
            else:
                spam_prob *= over_spam[i]
                non_spam_prob *= over_not_spam[i]
                #if index == 0:
                    #print("feature: " + str(feature_val) + ", mean: " + str(FEATURE_MEANS[i]) + ", spam prob: " + str(spam_prob) + ", not spam prob: " + str(non_spam_prob) + ", over spam i: " + str(over_not_spam[i]) + ", over not spam i: " + str(over_not_spam[i]))
        #if index == 0:
            #print("spam prob: " + str(spam_prob) + ", non-spam prob: " + str(non_spam_prob) + ", class: " + ("spam" if spam_prob > non_spam_prob else "not spam"))
        output_class = 1 if spam_prob > non_spam_prob else 0
        real_class = row[57]

        if output_class == 1:
            positive_samples += 1
        else:
            negative_samples += 1

        if output_class == real_class:
            correct += 1
        elif output_class == 0:
            wrong += 1
            false_negatives += 1
        elif output_class == 1:
            wrong += 1
            false_positives += 1
    accuracy = float(correct) / (correct+wrong)
    #print("Accuracy: " + str(accuracy))
    #print("False negatives: " + str(false_negatives))
    #print("False positives: " + str(false_positives) + "\n")
    return (false_negatives, false_positives, accuracy, pos_neg_train_dev, [under_spam, over_spam, under_not_spam, over_not_spam])

data = None

if not os.path.exists(sys.argv[1]):
    print("That data file doesn't exist!")
    sys.exit()
elif not len(sys.argv) == 2:
    print("Invalid number of arguments!")
    sys.exit()
with open(sys.argv[1]) as spam_data:
    column_names = [i for i in range(0, 58)]
    data = pandas.read_csv(spam_data, names = column_names)

folds = generate_folds(data)

total_accuracy = 0.0
total_false_negatives = 0.0
total_false_positives = 0.0
print("\n**NOTE** Iteration Fold_1 indicates fold #1 is used for testing and folds #2-5 are used for training.  Same rule follows for future iterations.\n")
print("Fold | False Positives | False Negatives | Error\n------------------------------------------------")
pos_neg_train_dev_table = ""
prob_table_iter_text = ""
for i in range(0, NUM_FOLDS): # perform cross-validation
    false_negatives, false_positives, accuracy, pos_neg_train_dev, feature_freqs = train(i, data, folds) # train with training set on fold i, pass in the data and the remaining folds
    total_accuracy += accuracy
    total_false_negatives += false_negatives
    total_false_positives += false_positives
    pos_neg_train_dev_table += str(i+1) + " | " + str(pos_neg_train_dev[0]) + " | " + str(pos_neg_train_dev[1]) + " | " + str(pos_neg_train_dev[2]) + " | " + str(pos_neg_train_dev[3]) + "\n"
    prob_table_iter_text += str(i+1) + " "
    for j in range(0, 57):
        prob_table_iter_text += "| " + str(feature_freqs[0][j]) + " | " + str(feature_freqs[1][j]) + " | " + str(feature_freqs[2][j]) + " | " + str(feature_freqs[3][j]) + " "
    prob_table_iter_text += "\n"
    print("Fold_" + str(i+1) + ", " + str(false_positives) + ", " + str(false_negatives) + ", " + str(1.0 - accuracy))

average_accuracy = total_accuracy / NUM_FOLDS # Average the accuracy over all the folds
average_false_negatives = total_false_negatives / NUM_FOLDS
average_false_positives = total_false_positives / NUM_FOLDS
print("Avg, " + str(average_false_positives) + ", " + str(average_false_negatives) + ", " + str(1.0 - average_accuracy))

print("\nIteration | pos train samples | neg train samples | pos dev examples | neg dev examples")
print("---------------------------------------------------------------------------------------")
print(pos_neg_train_dev_table)

prob_table_text = "Iteration "
for i in range(0, 57):
    prob_table_text += "| Pr(F" + str(i+1) + " <= mui | spam)" + "| Pr(" + str(i+1) + " > mui | spam)" + "| Pr(" + str(i+1) + " <= mui | non-spam)" + "| Pr(" + str(i+1) + " > mui | non-spam)"
print(prob_table_text)
print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
print(prob_table_iter_text)
