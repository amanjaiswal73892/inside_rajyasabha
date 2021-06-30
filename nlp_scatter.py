from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import plotly.express as px
import pandas as pd
import numpy as np
import pickle

# We used the combined dataset for our project.
df = pd.read_csv('Dataset/Complete_sorted_by_date.csv')
# This csv file contains pre-computed indexes, to save computation time and prevent computing cosine distances again.
similar_index_df = pd.read_csv("Dataset/similar_index.csv")

# The embeddings for questions are pre-computed and stored in a dataframe.
with open('Dataset/embed_word2vec.pickle', 'rb') as f:
    embed = pickle.load(f)
    embed = embed.reset_index(drop=True)


def get_tsne_projections(sample_size: int, pca_n_component=20,
                         tsne_perplexity=30):
    # First, we perform PCA to reduce computation time for T-sne.
    features = np.array([x for x in embed.vector[:sample_size]])
    pca = PCA(n_components=pca_n_component)
    components = pca.fit_transform(features)
    # Second, we use pca_components for TSNE
    tsne = TSNE(n_components=3, random_state=0, perplexity=tsne_perplexity)
    projections = tsne.fit_transform(components)
    projection_df = pd.DataFrame({
        'x': projections[:, 0],
        'y': projections[:, 1],
        'z': projections[:, 2],
        'i': df.index[:len(projections)]

    })
    return projection_df


def get_question_from_index(index: int):
    """This function returns the question Title, description and who asked the question given an index. This is used for getting question from clicked points."""

    out = df.loc[index,['question_title','question_by','question_description']].to_list()

    return out[0],out[1],out[2]

def get_similar_question_by_index(index):
    """This function is used for getting similar question from an index, used during click events"""

    similar_index = similar_index_df.loc[index].similar_index
    return get_question_from_index(similar_index)



def scatter_embedding_with_text(sample_size: int, pca_n_component=20, tsne_perplexity=30):
    """ This function plots the scatter_3d plot using the T-sne projections."""

    projection_df = get_tsne_projections(sample_size, pca_n_component, tsne_perplexity)
    fig = px.scatter_3d(
        projection_df, x='x', y='y', z='z',
        custom_data='i',
        color=df.ministry[:len(projection_df)],
        text = df.question_title[:len(projection_df)])

    fig = fig.update_layout(legend_orientation='v',
                      autosize=False)
    fig.update_layout(legend_title="Ministeries",
                  legend_bordercolor='grey',legend_borderwidth=1,legend_font_size=8)
    fig.update_layout(  legend=dict(
                        yanchor="top",
                        y=1.1,
                        xanchor="left",
                        x=-0.1))
    fig.update_layout(margin_l=0)
    fig.update_layout(margin_r=0)
    fig.update_layout(margin_t=0)
    fig.update_layout(margin_b=0)
    fig.update_traces(textfont_size=12)

    # fig =  fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False)

    return fig,projection_df 

