Creating a Bipartite Network of Players and Openings:

Focus on building a straightforward bipartite network that connects players to the openings they frequently use. This will form the foundation for calculating similarities between openings.
Projecting the Network to Create an Opening Similarity Network:

Proceed with projecting the bipartite network to create a one-layer network of openings. This network will show how openings are related based on shared players.
Filtering Out Spurious Connections Using BiCM:

You can still use the Bipartite Configuration Model (BiCM) to ensure that the connections between openings are statistically significant, but this step can be optional depending on your confidence in the raw data's quality.
Clustering Openings Based on Similarity Using Leiden Algorithm:

Apply clustering to group similar openings. The clustering will help identify common patterns and groupings within the opening network, which can be very useful for making recommendations.
Prediction of Recommendations for Openings Using Logistic Regression:

Implement a logistic regression model to predict which openings a player is likely to adopt based on the similarity network and their current repertoire. This model will be simpler without incorporating player fitness or opening complexity, focusing solely on the direct relationships between openings.

