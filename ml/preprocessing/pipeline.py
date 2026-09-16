import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

def get_train_val_test_split(
    df: pd.DataFrame, 
    target_col: str = "label", 
    test_size: float = 0.15, 
    val_size: float = 0.15, 
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Performs 70% Train, 15% Validation, 15% Test stratified split.
    The test set remains completely untouched until locked model evaluation.
    """
    # First split off test set (15%)
    df_train_val, df_test = train_test_split(
        df, 
        test_size=test_size, 
        stratify=df[target_col], 
        random_state=random_state
    )

    # Next split remaining 85% into Train (70%) and Validation (15%)
    relative_val_size = val_size / (1.0 - test_size)  # 0.15 / 0.85 = 0.17647
    df_train, df_val = train_test_split(
        df_train_val, 
        test_size=relative_val_size, 
        stratify=df_train_val[target_col], 
        random_state=random_state
    )

    return df_train, df_val, df_test

class LeakageFreeTextPipeline:
    """TF-IDF vectorizer pipeline fitted strictly on training data."""
    def __init__(self, max_features: int = 1000):
        self.vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english', ngram_range=(1, 2))

    def fit_transform_train(self, train_texts: pd.Series) -> np.ndarray:
        return self.vectorizer.fit_transform(train_texts).toarray()

    def transform_unseen(self, texts: pd.Series) -> np.ndarray:
        return self.vectorizer.transform(texts).toarray()

class LeakageFreeTabularPipeline:
    """StandardScaler pipeline fitted strictly on training data."""
    def __init__(self):
        self.scaler = StandardScaler()

    def fit_transform_train(self, train_features: np.ndarray) -> np.ndarray:
        clean_features = np.nan_to_num(train_features, nan=0.0, posinf=0.0, neginf=0.0)
        return self.scaler.fit_transform(clean_features)

    def transform_unseen(self, features: np.ndarray) -> np.ndarray:
        clean_features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        return self.scaler.transform(clean_features)
