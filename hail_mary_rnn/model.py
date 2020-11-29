# univariate lstm example
from prepare_team_vectors import *
import numpy as np
import random
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint

# split a univariate sequence into samples


def split_sequence(sequence, n_steps):
    X, y = list(), list()
    for i in range(len(sequence)):
        # find the end of this pattern
        end_ix = i + n_steps
        # check if we are beyond the sequence
        if end_ix > len(sequence)-1:
            break
        # gather input and output parts of the pattern
        seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return array(X), array(y)


def get_game_sequences_for_teams(games, teams, vector_dict):
    # X is input, a sequence of 3 games
    X, y = list(), list()
    for team in teams:
        game_vectors = get_vector_by_team_and_game(games, team, vector_dict)
        for team_vector, opponent_vector, team_score, opponent_score, date in game_vectors:
            input_X = np.sum(team_vector, axis=0) - \
                np.sum(opponent_vector, axis=0)
           # print(input_X.shape)
            if team_score > opponent_score:
                output_y = np.array([1, 0, 0])
            elif team_score == opponent_score:
                output_y = np.array([0, 1, 0])
            elif team_score < opponent_score:
                output_y = np.array([0, 0, 1])
            X.append(input_X)
            y.append(output_y)
    # print(output_y.shape)
    return X, y


def split_and_shuffle_train_test(X, y, ratio):
    split = int(len(X) * ratio)
    val = int(len(X[split:])/2)
    x_y = list(zip(X,y))
    random.seed(4)
    random.shuffle(x_y)
    shuffled_X = []
    shuffled_y = []
    for team, result in x_y:
        shuffled_X.append(team)
        shuffled_y.append(result)
    shuffled_X = np.array(shuffled_X)
    shuffled_y = np.array(shuffled_y)
    X_train = shuffled_X[:split]
    y_train = shuffled_y[:split]
    X_test = shuffled_X[split:val]
    y_test = shuffled_y[split:val]
    X_val = shuffled_X[val:]
    y_val = shuffled_y[val:]
    return X_train, y_train, X_test, y_test, X_val, y_val


if __name__ == '__main__':
    games = session.query(Game).all()
    print('got games')
    vector_dict = load_vectors_to_dict('resources/player_vectors.txt')
    teams = session.query(Team).all()
    print('got teams')
    print('getting vectors...')
    X, y = get_game_sequences_for_teams(games, teams, vector_dict)
    print('got vectors')
    X_train, y_train, X_test, y_test, X_val, y_val = split_and_shuffle_train_test(X, y, .8)
    model = Sequential()
    model.add(Dense(12, input_dim=41, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(3, activation='softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam', metrics=['accuracy'])
    model.summary()
    filepath = "model-files/best_model.{epoch:02d}-{loss:.2f}.h5"
    es = EarlyStopping(monitor='loss', patience=500, verbose=1, mode='min')
    mc = ModelCheckpoint(filepath, save_best_only=True,
                         monitor='loss', mode='min', verbose=1)

    model.fit(X_train,
              y_train,
              epochs=3000,
              batch_size=16,
              validation_data=(X_test, y_test), callbacks=[mc, es])
    #model = load_model('/home/daniel/git/hail_mary_rnn/model-files/best_model.1005-0.57.h5')
    scores = model.evaluate(X_val, y_val, verbose=1)
    print("%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))