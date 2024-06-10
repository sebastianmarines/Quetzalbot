from typing import List

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Tag
from sklearn.ensemble import RandomForestClassifier

from api.models import HtmlHealing, element_t

pd.set_option("future.no_silent_downcasting", True)


def preprocess_data(df):
    df = df.fillna("None")
    X = pd.get_dummies(df.drop("element", axis=1))
    element_dict = dict(zip(df["element"].unique(), range(df["element"].nunique())))
    y = df["element"].replace(element_dict).infer_objects(copy=False)
    return X, y, element_dict


def train_model(X_train, y_train):
    rf = RandomForestClassifier(n_estimators=50, random_state=0)
    rf.fit(X_train, y_train)
    return rf


def predict_elements(test, rf, element_dict, X_train_columns):
    test = test.fillna("None")
    processed_test = pd.get_dummies(test)

    missing_features = set(X_train_columns) - set(processed_test.columns)
    for feature in missing_features:
        processed_test[feature] = 0

    processed_test = processed_test[X_train_columns]
    processed_array = processed_test.to_numpy()
    probabilities = rf.predict_proba(processed_array)

    predicted_elements = [
        list(element_dict.keys())[np.argmax(probs)] for probs in probabilities
    ]
    return predicted_elements


def get_all_elements(tag: Tag):
    elements: List[element_t] = []

    def get_element(tag: Tag):
        attrs = {k: v for k, v in tag.attrs.items() if k != "class"}

        elem_id = tag.get("id", None)
        tag_name = tag.name
        classes = " ".join(tag.get("class", []))
        text_content = tag.get_text(strip=False)
        selector = str(tag)
        attributes = "".join([f"{k}={v}" for k, v in attrs.items()])

        return element_t(
            element=(
                f"id={elem_id}"
                if elem_id is not None
                else classes if classes != "" else text_content
            ),
            id=elem_id,
            tag_name=tag_name,
            classes=classes,
            text_content=text_content,
            selector=selector,
            attributes=attributes,
        )

    for child in (t for t in tag.children if t.name != "script"):
        if isinstance(child, Tag):
            element = get_element(child)
            elements.append(element)
            elements.extend(get_all_elements(child))

    return elements


def get_model(df_train):
    X_train, y_train, element_dict = preprocess_data(df_train)
    rf_model = train_model(X_train, y_train)
    return rf_model


def html_to_df(html: str):
    soup = BeautifulSoup(html.replace("\n", " "), "html.parser")
    body = list(soup.children)[0]

    all_elements = get_all_elements(body)
    df_train = pd.DataFrame(all_elements)

    return df_train


def heal(data: HtmlHealing):
    df_train = html_to_df(data.html)
    df_test = pd.DataFrame(data.prev_element._asdict(), index=[0])
    X_train, y_train, element_dict = preprocess_data(df_train)
    rf_model = train_model(X_train, y_train)
    predicted_elements = predict_elements(df_test, rf_model, element_dict, X_train.columns)
    return predicted_elements[0]
