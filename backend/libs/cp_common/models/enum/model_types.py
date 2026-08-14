from enum import StrEnum


class ModelType(StrEnum):
    """Supported analytical and machine-learning model families."""

    NN = "nn"
    PCA = "pca"
    SVM = "svm"
    KMEANS = "kmeans"
    BNN = "bnn"
    CNN = "cnn"
    PHYSICS = "physics"
