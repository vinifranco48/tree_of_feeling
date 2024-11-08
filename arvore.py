import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx

class AVLNode:
    def __init__(self, word, sentiment):
        self.word = word
        self.sentiment = sentiment
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None

    def insert(self, word, sentiment):
        self.root = self._insert_recursive(self.root, word, sentiment)

    def _insert_recursive(self, node, word, sentiment):
        if not node:
            return AVLNode(word, sentiment)

        if word < node.word:
            node.left = self._insert_recursive(node.left, word, sentiment)
        elif word > node.word:
            node.right = self._insert_recursive(node.right, word, sentiment)
        else:
            node.sentiment = sentiment
            return node

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        if balance > 1 and word < node.left.word:
            return self._rotate_right(node)
        if balance < -1 and word > node.right.word:
            return self._rotate_left(node)
        if balance > 1 and word > node.left.word:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1 and word < node.right.word:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _rotate_left(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _rotate_right(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _get_height(self, node):
        return node.height if node else 0

    def _get_balance(self, node):
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def get_tree_height(self, node):
        if not node:
            return 0
        return max(self.get_tree_height(node.left), self.get_tree_height(node.right)) + 1

    def _calculate_positions(self, node, level, x, width, positions):
        if not node:
            return

        positions[node] = (x, -level)  # Negative level to invert the y-axis

        if node.left:
            self._calculate_positions(node.left, level + 1, x - width/(2**(level + 1)), width, positions)
        if node.right:
            self._calculate_positions(node.right, level + 1, x + width/(2**(level + 1)), width, positions)

    def visualize_tree(self):
        if not self.root:
            return None

        plt.clf()
        fig, ax = plt.subplots(figsize=(12, 8))
        
        graph = nx.DiGraph()
        self._add_edges(graph, self.root)
        
        # Calculate custom positions
        positions = {}
        tree_height = self.get_tree_height(self.root)
        self._calculate_positions(self.root, 0, 0.5, 1.0, positions)
        
        # Draw edges
        nx.draw_networkx_edges(graph, positions, edge_color='gray', arrows=True, 
                             arrowsize=20, ax=ax, connectionstyle="arc3,rad=0.2")
        
        # Prepare nodes and labels
        nodes = list(graph.nodes())
        labels = {node: f"{node.word}\n({node.sentiment})" for node in nodes}
        
        # Color nodes based on sentiment
        colors = []
        for node in nodes:
            if node.sentiment == 1:
                colors.append('#90EE90')  # Light green for positive
            elif node.sentiment == -1:
                colors.append('#FFB6C1')  # Light pink for negative
            else:
                colors.append('#E0E0E0')  # Light gray for neutral
        
        # Draw nodes
        nx.draw_networkx_nodes(graph, positions, node_color=colors, 
                             node_size=2500, ax=ax)
        
        # Add labels
        nx.draw_networkx_labels(graph, positions, labels, font_size=8)
        
        plt.title("AVL Tree Sentiment Visualization")
        plt.axis('off')
        
        # Adjust layout to prevent text overlap
        plt.tight_layout()
        return fig

    def _add_edges(self, graph, node):
        if not node:
            return
        graph.add_node(node)
        if node.left:
            graph.add_edge(node, node.left)
            self._add_edges(graph, node.left)
        if node.right:
            graph.add_edge(node, node.right)
            self._add_edges(graph, node.right)

# Initialize Streamlit session
st.title("AVL Tree Sentiment Visualization")

# Initialize tree in Streamlit session if it doesn't exist
if 'avl_tree' not in st.session_state:
    st.session_state.avl_tree = AVLTree()

# Input interface
col1, col2 = st.columns([3, 2])
with col1:
    word = st.text_input("Enter a word:")
with col2:
    sentiment = st.select_slider(
        "Select sentiment:",
        options=[-1, 0, 1],
        format_func=lambda x: "Negative" if x == -1 else ("Neutral" if x == 0 else "Positive")
    )

if st.button("Insert Word"):
    if word:
        st.session_state.avl_tree.insert(word, sentiment)
        st.success(f"Word '{word}' inserted with sentiment {sentiment}")
    else:
        st.error("Please enter a valid word.")

# Visualize the tree
if st.session_state.avl_tree.root:
    st.subheader("AVL Tree Visualization")
    fig = st.session_state.avl_tree.visualize_tree()
    st.pyplot(fig)
else:
    st.info("The tree is empty. Insert some words to begin!")

# Add button to clear the tree
if st.button("Clear Tree"):
    st.session_state.avl_tree = AVLTree()
    st.experimental_rerun()