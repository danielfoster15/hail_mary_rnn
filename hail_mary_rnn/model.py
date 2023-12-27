# univariate lstm example
from prepare_team_vectors import *
import numpy as np
import random
import json
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint

# split a univariate sequence into samples


def process_input_output(team_vector, opponent_vector, team_score, opponent_score):
    input_X = np.array(team_vector) - np.array(opponent_vector)
    if team_score > opponent_score:
        output_y = np.array([1, 0, 0])
    elif team_score == opponent_score:
        output_y = np.array([0, 1, 0])
    elif team_score < opponent_score:
        output_y = np.array([0, 0, 1])
    return input_X, output_y


def get_game_results(game_vectors):
    X, y = list(), list()
    for k, v in game_vectors.items():
        if int(k[-4:]) > 2006:
            team_vector, opponent_vector, team_score, opponent_score = v
            input_X, output_y = process_input_output(
                team_vector, opponent_vector, team_score, opponent_score
            )
            X.append(input_X)
            y.append(output_y)
    return X, y


def split_and_shuffle_train_test(X, y, ratio):
    split = int(len(X) * ratio)
    x_y = list(zip(X, y))
    random.seed(4)
    random.shuffle(x_y)
    shuffled_X, shuffled_y = zip(*x_y)
    shuffled_X = np.array(shuffled_X)
    shuffled_y = np.array(shuffled_y)

    X_train = shuffled_X[:split]
    y_train = shuffled_y[:split]

    val_split = int(
        (len(X) - split) * 0.5
    )  # Splitting remaining data equally for validation and test
    X_val = shuffled_X[split : split + val_split]
    y_val = shuffled_y[split : split + val_split]

    X_test = shuffled_X[split + val_split :]
    y_test = shuffled_y[split + val_split :]

    return X_train, y_train, X_test, y_test, X_val, y_val


if __name__ == "__main__":
    games = session.query(Game).all()
    print("got games")
    teams = session.query(Team).all()
    print("got teams")
    print("getting vectors...")
    # game_vectors = get_game_vectors(games)
    # with open('resources/game_vectors.json', 'w') as f:
    #    json.dump(game_vectors, f, indent=4)
    with open("resources/game_vectors.json", "r") as f:
        game_vectors = json.load(f)
    X, y = get_game_results(game_vectors)
    print("got vectors")
    X_train, y_train, X_test, y_test, X_val, y_val = split_and_shuffle_train_test(
        X, y, 0.7
    )

    # Define a custom learning rate
    custom_lr = 0.00001  # Your chosen learning rate

    # Create the optimizer with the custom learning rate
    custom_adam = Adam(learning_rate=custom_lr)

    model = Sequential()
    model.add(
        Dense(24, input_dim=42, activation="relu")
    )  # Changing the first layer to 16 neurons
    model.add(Dense(16, activation="relu"))  # Changing the second layer to 10 neurons
    model.add(Dense(8, activation="relu"))  # Changing the third layer to 5 neurons
    model.add(Dense(3, activation="softmax"))
    model.compile(
        loss="categorical_crossentropy", optimizer=custom_adam, metrics=["accuracy"]
    )
    model.summary()
    filepath = "model-files/best_model.nofuture.h5"
    es = EarlyStopping(monitor="loss", patience=500, verbose=1, mode="min")
    mc = ModelCheckpoint(
        filepath, save_best_only=True, monitor="loss", mode="min", verbose=1
    )

    model.fit(
        X_train,
        y_train,
        epochs=3000,
        batch_size=16,
        validation_data=(X_val, y_val),
        callbacks=[mc, es],
    )
    # model = load_model('/home/daniel/git/hail_mary_rnn/model-files/best_model.1005-0.57.h5')
    scores = model.evaluate(X_test, y_test, verbose=1)
    print("%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))
