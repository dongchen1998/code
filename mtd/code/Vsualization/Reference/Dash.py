import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import networkx as nx
import io
import base64

# 初始化Dash应用
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 设置应用布局
app.layout = html.Div([
    dbc.Row(
        dbc.Col(
            html.H1("Gene Co-expression Network"),
            width={'size': 6, 'offset': 3},
        )
    ),
    dbc.Row(
        dbc.Col(
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                multiple=True  # allow multiple files to be uploaded
            ),
            width={'size': 6, 'offset': 3},
        )
    ),
    dbc.Row(
        dbc.Col(
            dcc.Graph(
                id='my-graph'
            ),
            width=12,
        )
    )
])

# 定义创建基因网络的函数，这是之前定义的函数，保持不变
def create_gene_network(df,color,bubble_size_ratio,k_value,iterations_value):

    # 计算相关性
    correlation_matrix = df.transpose().corr()

    # 使用networkx创建一个网络图
    G = nx.Graph()
    for gene1 in df.index:
        for gene2 in df.index:
            if gene1 != gene2:
                G.add_edge(gene1, gene2, weight=correlation_matrix.loc[gene1, gene2])

    threshold = 0.5 # 相关性系数
    edges = [(u, v) for (u, v, d) in G.edges(data=True) if abs(d['weight']) > threshold]
    G = G.edge_subgraph(edges).copy()  # 使用edges创建一个新的图，并使用copy()避免状态问题

    # pos设置,k越小则点越紧
    pos = nx.spring_layout(G, k=k_value, iterations=iterations_value)

    # 将位置作为节点属性添加到G中
    for node in G.nodes():
        G.nodes[node]['pos'] = pos[node]

    # 使用plotly创建网络图
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    
    # 分别创建正相关和负相关的边
    edge_x_pos, edge_y_pos = [], []
    edge_x_neg, edge_y_neg = [], []
    
    # 根据权重将边分为正负两组
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        if edge[2]['weight'] > 0:
            edge_x_pos.extend([x0, x1, None])
            edge_y_pos.extend([y0, y1, None])
        else:
            edge_x_neg.extend([x0, x1, None])
            edge_y_neg.extend([y0, y1, None])


    edge_trace_pos = go.Scatter(
        x=edge_x_pos, y=edge_y_pos,
        line=dict(width=0.3, color='red'),
        hoverinfo='none',
        mode='lines'
    )
    
    edge_trace_neg = go.Scatter(
        x=edge_x_neg, y=edge_y_neg,
        line=dict(width=0.2, color='blue'),
        hoverinfo='none',
        mode='lines'
    )

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale=color,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = []
    node_sizes = []  # 添加一个列表来存储基于节点连接数的大小
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(adjacencies[0])
        node_degree = len(adjacencies[1])
        # 设置节点大小
        scaled_size = 15 + (node_degree * bubble_size_ratio)  # 基础大小为5，每个连接增加5个单位大小
        node_sizes.append(scaled_size)

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text
    node_trace.marker.size = node_sizes  # 更新marker的大小

    fig = go.Figure(data = [edge_trace_pos, edge_trace_neg, node_trace],
                    layout=go.Layout(
                        title='Gene Co-expression Network',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        annotations=[
                            dict(
                                text="",
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.005, y=-0.002)
                        ],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    # 定义fig的布局，设置宽度和高度
    fig.update_layout(
        autosize=False,
        width=800, 
        height=600,
        template="plotly_white"
    )
    # fig.update_traces(marker_symbol='diamond') # 更改marker的形状

    fig.show()

# 添加回调以响应文件上传
@app.callback(
    Output('my-graph', 'figure'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_graph(contents, filename):
    # 当没有文件被上传时，不更新图表
    if contents is None:
        return dash.no_update

    # 解析上传的文件并创建DataFrame
    content_string = contents[0].split(',')[1]
    decoded = base64.b64decode(content_string)
    if 'csv' in filename[0]:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename[0]:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded))
    else:
        return dash.no_update

    # 调用之前定义的函数创建图表
    fig = create_gene_network(df, 'Portland', 1, 0.5, 10)
    return fig

# 运行应用
if __name__ == '__main__':
    app.run_server(debug=True)
