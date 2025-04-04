import numpy as np
from sklearn.decomposition import PCA


def extract_pca_components(hidden_space_by_language, n_components=10):
    """
    Extract common subspace across languages using PCA.
    This identifies directions that explain most variance in both languages.

    hidden_space_by_language: { [lang]: np.array([n_layers, n_entries, d_model]) }
    """
    languages = list(hidden_space_by_language.keys())

    n_layers = hidden_space_by_language[languages[0]].shape[0]
    d_model = hidden_space_by_language[languages[0]].shape[2]

    pca_components = []
    pca_means = []
    explained_variance_ratios = []

    for layer in range(n_layers):
        # Concatenate embeddings from both languages
        combined_embeddings = np.empty((0, d_model))

        for lang in languages:
            combined_embeddings = np.concatenate(
                [combined_embeddings, hidden_space_by_language[lang][layer, :, :]], axis=0
            )

        # Apply PCA to find common directions
        pca = PCA(n_components=n_components)
        pca.fit_transform(combined_embeddings)

        pca_components.append(pca.components_)  # Principal components [n_components, d_model]
        pca_means.append(pca.mean_)
        explained_variance_ratios.append(pca.explained_variance_ratio_)

    return pca_components, pca_means, explained_variance_ratios


def project_onto_pca(hidden_space_by_language, pca_components, pca_means):
    """
    Project each language's embeddings onto the common subspace.

    hidden_space_by_language: { [lang]: np.array([n_layers, n_entries, d_model]) }
    """
    n_layers = len(pca_components)
    projections = {}

    for lang in hidden_space_by_language:
        projections[lang] = []

        for layer in range(n_layers):
            # Get embeddings for this layer and language
            layer_embeddings = hidden_space_by_language[lang][layer, :, :]  # [n_entries, d_model]
            centered_layer_embeddings = layer_embeddings - pca_means[layer]
            projection = pca_components[layer] @ centered_layer_embeddings.T
            projections[lang].append(projection)

    return projections
