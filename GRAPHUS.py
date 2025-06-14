import time
import matplotlib.pyplot as plt
import networkx as nx

def binary_tree(levels):
    """Genera un albero binario con un certo numero di livelli"""
    G = nx.DiGraph()
    def add_edges(node, depth):
        if depth < levels:
            left = node + '0'
            right = node + '1'
            G.add_edge(node, left)
            G.add_edge(node, right)
            add_edges(left, depth + 1)
            add_edges(right, depth + 1)
    G.add_node('')
    add_edges('', 0)
    return G

def plot_tree(G, title):
    """Plotta l'albero con nodi verticalmente allineati per livello"""
    pos = hierarchy_pos(G, '')
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, node_size=20, width=0.5, arrows=False)
    plt.title(title)
    plt.axis('off')
    plt.show()

def hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """Crea posizioni gerarchiche per un grafo"""
    def _hierarchy_pos(G, root, left, right, vert_loc, xcenter, pos=None, parent=None):
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.successors(root))
        if len(children) != 0:
            dx = (right - left) / 2
            nextx = left + dx
            for child in children:
                pos = _hierarchy_pos(G, child, left, left + dx, vert_loc - vert_gap, nextx, pos, root)
                left += dx
        return pos
    return _hierarchy_pos(G, root, 0, width, vert_loc, xcenter)

def chiedi_lingua():
    print("Seleziona la lingua / Choisissez la langue / Wählen Sie die Sprache / Choose language:")
    print("1) ITA\n2) FRA\n3) DEU\n4) ENG")
    scelta = input("Inserisci numero (1-4): ").strip()
    return scelta if scelta in {'1', '2', '3', '4'} else '4'

def domanda_input(scelta):
    domande = {
        "1": "Quanti livelli? (1-20, oppure 'stop' per uscire): ",
        "2": "Combien de niveaux ? (1-20, ou 'stop' pour quitter) : ",
        "3": "Wie viele Ebenen? (1-20, oder 'stop' zum Beenden): ",
        "4": "How many levels? (1-20, or 'stop' to exit): "
    }
    while True:
        risposta = input(domande.get(scelta, domande["4"])).strip().lower()
        if risposta == 'stop':
            return None
        try:
            n = int(risposta)
            if 1 <= n <= 20:
                return n
            else:
                print("Valore fuori intervallo (1-20)")
        except ValueError:
            print("Input non valido")

def info_grafo(G, lang):
    info = {
        "1": [
            f"Numero di nodi: {G.number_of_nodes()}",
            f"Numero di archi: {G.number_of_edges()}",
            f"Grado massimo: {max(dict(G.out_degree()).values())}",
            f"Altezza stimata: {max(len(n) for n in G.nodes())}"
        ],
        "2": [
            f"Nombre de nœuds : {G.number_of_nodes()}",
            f"Nombre d’arêtes : {G.number_of_edges()}",
            f"Degré maximum : {max(dict(G.out_degree()).values())}",
            f"Hauteur estimée : {max(len(n) for n in G.nodes())}"
        ],
        "3": [
            f"Anzahl der Knoten: {G.number_of_nodes()}",
            f"Anzahl der Kanten: {G.number_of_edges()}",
            f"Maximaler Grad: {max(dict(G.out_degree()).values())}",
            f"Geschätzte Höhe: {max(len(n) for n in G.nodes())}"
        ],
        "4": [
            f"Number of nodes: {G.number_of_nodes()}",
            f"Number of edges: {G.number_of_edges()}",
            f"Maximum degree: {max(dict(G.out_degree()).values())}",
            f"Estimated height: {max(len(n) for n in G.nodes())}"
        ]
    }
    return info.get(lang, info["4"])

def titolo_plot(n, lang, G):
    labels = {
        "1": f"Albero binario con {n} livelli - {G.number_of_nodes()} nodi",
        "2": f"Arbre binaire à {n} niveaux - {G.number_of_nodes()} nœuds",
        "3": f"Binärbaum mit {n} Ebenen - {G.number_of_nodes()} Knoten",
        "4": f"Binary tree with {n} levels - {G.number_of_nodes()} nodes"
    }
    return labels.get(lang, labels["4"])

def main():
    lingua = chiedi_lingua()
    while True:
        livelli = domanda_input(lingua)
        if livelli is None:
            print("\nFine programma.\n")
            break
        start = time.time()
        G = binary_tree(livelli)
        end = time.time()
        print("\n" + "-"*40)
        for riga in info_grafo(G, lingua):
            print(riga)
        print(f"Tempo di esecuzione: {end - start:.4f} secondi")
        print("-"*40)
        plot_tree(G, titolo_plot(livelli, lingua, G))

if __name__ == "__main__":
    main()
