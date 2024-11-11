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

    def visualize_tree(self):
        if not self.root:
            return None

        plt.close('all')
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        
        graph = nx.DiGraph()
        self._add_edges(graph, self.root)
        
        positions = {}
        self._calculate_positions(self.root, 0, 0.5, 1.0, positions)
        
        if positions and len(positions) > 0:
            edges = list(graph.edges())
            if edges:
                nx.draw_networkx_edges(
                    graph, 
                    positions, 
                    edge_color='gray',
                    arrows=True,
                    arrowsize=20,
                    connectionstyle="arc3,rad=0.2"
                )
    
            nodes = list(graph.nodes())
            colors = []
            for node in nodes:
                if node.sentiment == 1:
                    colors.append('#90EE90')  
                elif node.sentiment == -1:
                    colors.append('#FFB6C1')  
                else:
                    colors.append('#E0E0E0')  
            
            nx.draw_networkx_nodes(
                graph,
                positions,
                nodelist=nodes,
                node_color=colors,
                node_size=2500
            )
            
            labels = {node: f"{node.word}\n({node.sentiment})" for node in nodes}
            nx.draw_networkx_labels(
                graph,
                positions,
                labels,
                font_size=8
            )
        
        plt.title("Visualização da Árvore AVL de Sentimentos")
        ax.set_xticks([])
        ax.set_yticks([])
        plt.axis('off')
        
        plt.tight_layout()
        
        return fig

    def _calculate_positions(self, node, level, x, width, positions):
        if not node:
            return

        positions[node] = (x, -level)

        if node.left:
            self._calculate_positions(
                node.left,
                level + 1,
                x - width/(2**(level + 1)),
                width,
                positions
            )
        if node.right:
            self._calculate_positions(
                node.right,
                level + 1,
                x + width/(2**(level + 1)),
                width,
                positions
            )

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

    def analyze_text(self, text):
        words = text.lower().split()
        sentiment_scores = []
        found_words = []
        
        for word in words:
            node = self._find_word(self.root, word)
            if node:
                sentiment_scores.append(node.sentiment)
                found_words.append(word)
        
        if not sentiment_scores:
            return 0, [], "Nenhuma palavra encontrada no dicionário de sentimentos."
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        return avg_sentiment, found_words, self._get_feedback(avg_sentiment)
    
    def _find_word(self, node, word):
        if not node:
            return None
        
        if word == node.word:
            return node
        elif word < node.word:
            return self._find_word(node.left, word)
        else:
            return self._find_word(node.right, word)
    
    def _get_feedback(self, sentiment_score):
        if sentiment_score > 0.3:
            return "Que legal, você aparenta estar feliz! 😊"
        elif sentiment_score < -0.3:
            return "Você aparentemente está triste... 😔"
        else:
            return "Seu texto parece neutro... 😐"


st.set_page_config(
    page_title="Análise de Sentimentos",
    layout="wide"
)

st.title("Análise de Sentimentos com Árvore AVL")

if 'avl_tree' not in st.session_state:
    st.session_state.avl_tree = AVLTree()

# Criação das abas
tab1, tab2 = st.tabs(["📝 Adicionar palavras", "📊 Analisar Texto"])

with tab1:
    
    col1, col2 = st.columns([3, 2])
    with col1:
        word = st.text_input("Digite uma palavra:", key="word_input")
    with col2:
        sentiment = st.select_slider(
            "Selecionar sentimento:",
            options=[-1, 0, 1],
            format_func=lambda x: "Negativo 😔" if x == -1 else ("Neutro 😐" if x == 0 else "Positivo 😊"),
            key="sentiment_slider"
        )

    if st.button("Inserir palavra", key="insert_button"):
        if word:
            st.session_state.avl_tree.insert(word.lower(), sentiment)
            st.success(f"Palavra '{word}' inserida com sentimento {sentiment}")
        else:
            st.error("Por favor, digite uma palavra.")
    if st.session_state.avl_tree.root:
        st.subheader("Visualização da Árvore")
        try:
            fig = st.session_state.avl_tree.visualize_tree()
            if fig is not None:
                st.pyplot(fig, clear_figure=True)
            else:
                st.info("Não há dados suficientes para visualizar a árvore.")
        except Exception as e:
            st.error(f"Erro ao visualizar a árvore: {str(e)}")
            st.info("Tente adicionar mais palavras à árvore.")
    else:
        st.info("A árvore está vazia. Insira algumas palavras para começar!")

with tab2:
    st.header("Análise de Sentimentos do Texto")
    
    text_to_analyze = st.text_area(
        "Digite seu texto para análise:",
        height=150,
        key="text_analysis"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        analyze_button = st.button("Analisar", key="analyze_button")
    
    if analyze_button:
        if text_to_analyze:
            sentiment_score, found_words, feedback = st.session_state.avl_tree.analyze_text(text_to_analyze)
            
            st.markdown("---")
            st.markdown(f"### {feedback}")
            
            if found_words:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("📚 Palavras analisadas:", ", ".join(found_words))
                with col2:
                    st.write(f"📊 Pontuação média: {sentiment_score:.2f}")
            else:
                st.warning("⚠️ Nenhuma palavra do texto foi encontrada na árvore. Adicione mais palavras ao dicionário!")
        else:
            st.error("⚠️ Por favor, digite algum texto para análise.")

