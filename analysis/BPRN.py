import pandas as pd
import numpy as np
import scipy.sparse as sp
import matplotlib.cm as cm
import networkx as nx
from networkx.algorithms import bipartite
from networkx.algorithms.community import girvan_newman

# Load the data
df = pd.read_csv(r"July-Sept_Lumbra_filtered.csv")

# Extract unique players and ECO codes
players = df['Player'].unique()
eco_codes = df['ECO Code'].unique()

# Create mappings for player and ECO code indices
player_index = {player: idx for idx, player in enumerate(players)}
eco_index = {opening: idx for idx, opening in enumerate(eco_codes)}

P = len(players)
O = len(eco_codes)

# Initialize a sparse matrix
M = sp.lil_matrix((P, O), dtype=int)  # LIL format is efficient for incremental construction

# Vectorized assignment to the sparse matrix
player_indices = df['Player'].map(player_index)
eco_indices = df['ECO Code'].map(eco_index)
M[player_indices, eco_indices] = 1

# Convert to CSR format for efficient arithmetic operations later
M = M.tocsr()

# print("Players:", players)
# print("Openings:", eco_codes)
# print("Matrix M:\n", M.toarray())  # Convert to dense if you want to inspect it (careful with large matrices)


import numpy as np
import scipy.sparse as sp

# Assuming M is your P x O sparse matrix from the previous step

# Calculate diversification for each player (sum across rows)
# Note: `axis=1` sums across columns, which corresponds to openings.
diversification = np.array(M.sum(axis=1)).flatten()

# Calculate ubiquity for each opening (sum across columns)
# Note: `axis=0` sums across rows, which corresponds to players.
ubiquity = np.array(M.sum(axis=0)).flatten()

# Print the results (optional)
# print("Diversification (d_p) for each player:", diversification)
# print("Ubiquity (u_o) for each opening:", ubiquity)


from scipy.sparse import lil_matrix, csr_matrix

# Convert M to a sparse CSR matrix if it isn't already
M_sparse = csr_matrix(M)

# Calculate the W* matrix using sparse matrix multiplication
W_star = M_sparse.T @ M_sparse

# Set the diagonal to 0 if you need to exclude self-cooccurrences
W_star.setdiag(0)

# Optionally convert W_star to LIL format if you need to modify it further
W_star = W_star.tolil()

# print("Matrix W*:\n", W_star)



import numpy as np
import scipy.sparse as sp

# Assuming M is a sparse matrix representation of your bipartite adjacency matrix
# where P is the number of players and O is the number of openings

# Step 1: Calculate diversification (dp) for each player
dp = np.asarray(M.sum(axis=1)).flatten()  # Summing over columns, converting to dense array

# Step 2: Calculate ubiquity (uo) for each opening
uo = np.asarray(M.sum(axis=0)).flatten()  # Summing over rows, converting to dense array

# Step 3: Calculate the expected co-occurrence for each pair of openings
P = M.shape[0]  # Number of players
expected = np.outer(uo, uo) / P

# Step 4: Calculate the observed co-occurrence W* matrix
W_star = M.T @ M  # Sparse matrix multiplication, gives the W* matrix of shape (O, O)

# Step 5: Calculate Z-scores for each pair of openings
std_dev = np.sqrt(expected)  # Assuming Poisson distribution for co-occurrences

# Convert to dense if necessary when performing the subtraction
observed = W_star.toarray() if sp.issparse(W_star) else W_star

Z_scores = (observed - expected) / std_dev

# Step 6: Apply a threshold to filter the Z-scores
threshold = 3
# Efficient thresholding with sparse matrix output
W_filtered = sp.csr_matrix(np.where(Z_scores > threshold, observed, 0))

# W_filtered remains sparse; convert to dense only if required for final inspection:
# W_filtered_dense = W_filtered.toarray()

# print("Matrix W Filtered:\n", W_filtered)


#NOTE Density Graph
# import matplotlib.pyplot as plt

# # Convert the sparse matrix subset to a dense format for visualization
# W_filtered_dense = W_filtered.toarray()

# plt.figure(figsize=(10, 8))
# plt.imshow(W_filtered_dense[0:500, 0:500], cmap='viridis', interpolation='none')  # Change slice range as needed
# plt.colorbar()
# plt.title("Filtered W* Matrix Subset (0-500)")
# plt.show()


#NOTE Histogram of Co-occurrences
import matplotlib.pyplot as plt

# Extract non-zero elements from the sparse matrix
non_zero_elements = W_filtered.data  # This extracts the non-zero elements directly from the sparse matrix

# Plot the histogram

plt.hist(non_zero_elements, bins=100, color='blue')
# plt.xscale('log')
plt.title("Distribution of Significant Co-occurrences")
plt.xlabel("Co-occurrence Value")
plt.ylabel("Frequency")
plt.show()


#NOTE Mean, Median, Max
# # Extract non-zero elements directly from the sparse matrix
# non_zero_values = W_filtered.data

# # Calculate and print the statistics
# print(f"Mean of significant co-occurrences: {np.mean(non_zero_values)}")
# print(f"Median of significant co-occurrences: {np.median(non_zero_values)}")
# print(f"Max of significant co-occurrences: {np.max(non_zero_values)}")



#NOTE Build relatedness network
import igraph as ig
import leidenalg as la
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.community import louvain_communities

# Create a graph from the filtered W* matrix
G = nx.Graph()

# Add nodes (each node is an opening)
num_openings = W_filtered.shape[0]
G.add_nodes_from(range(num_openings))

# Add edges (only add edges for statistically significant co-occurrences)
rows, cols = W_filtered.nonzero()
for i, j in zip(rows, cols):
    if i < j:  # Ensure we don't add duplicate edges or self-loops
        G.add_edge(i, j, weight=W_filtered[i, j])

# Convert the NetworkX graph to an iGraph object
G_ig = ig.Graph.TupleList(G.edges(data=True), directed=False, edge_attrs=['weight'])

# Step 1: Detect communities using the Louvain method
# Detect communities using the Leiden algorithm
partition = la.find_partition(G_ig, la.ModularityVertexPartition)

# Map iGraph communities back to NetworkX nodes
node_community_map = {}
for idx, community in enumerate(partition):
    for node in community:
        node_community_map[G_ig.vs[node]["name"]] = idx

# Create a list of colors corresponding to each node’s community
node_colors = [node_community_map.get(node, -1) for node in G.nodes()]

# Use a force-directed layout for better separation
pos = nx.spring_layout(G, k=0.6, iterations=100, seed=42)  # Adjust `k` and `iterations` for better results

# Draw the graph
plt.figure(figsize=(14, 10))
nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.tab10, node_size=15)
nx.draw_networkx_edges(G, pos, alpha=0.2)

plt.title('Communities in Chess Opening Network (Leiden Algorithm)')
plt.show()
