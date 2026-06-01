from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split


def xgb_signal(df):

    df = df.dropna()

    df['Target'] = (
        df['Close'].shift(-1) > df['Close']
    ).astype(int)

    features = df[
        ['RSI', 'EMA20', 'EMA50']
    ]

    target = df['Target']

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        shuffle=False
    )

    model = XGBClassifier()

    model.fit(X_train, y_train)

    pred = model.predict(
        [features.iloc[-1]]
    )[0]

    return "BUY" if pred == 1 else "SELL"
