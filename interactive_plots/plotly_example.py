### Using plotly library ###
import numpy as np
import plotly.express as px
from tqdm import tqdm
import plotly.graph_objects as go
from plotly.subplots import make_subplots

##IMPORT DATA
fulldata = np.genfromtxt('../Final_Protoype/outputs/7328.3562yrs_0100_t03_2_TMAP2/0100_t03_2_TMAP.csv',skip_header = 1, delimiter = ',') #results from running models
tdata = np.transpose(fulldata)
masses = tdata[0]
periods = tdata[1]
incls = tdata[2]
natives = tdata[3]
ohs= tdata[4]
diffs = tdata[5]
ecs = tdata[6]


#TITLES FOR PLOTS
titles =  []

for f in range(9):
    g = f*380
    m = round(masses[g],4)
    titles.append(f'MS Star Mass = {m} solMass')

#COLOURS
c1 = ['slateblue','mediumpurple','darkorchid','lightgreen','turquoise','aqua','steelblue','darkviolet','dodgerblue']
c2 = ['orange','gold','yellowgreen','mediumorchid','fuchsia','crimson','orangered','lime','firebrick']

#MAKING FIGURE
fig = make_subplots(
    rows=3, cols=3,
    specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'},{'type': 'scatter3d'}],
           [{'type': 'scatter3d'}, {'type': 'scatter3d'},{'type': 'scatter3d'}],
           [{'type': 'scatter3d'}, {'type': 'scatter3d'},{'type': 'scatter3d'}]],
    subplot_titles = titles
    )

# adding surfaces to subplots.
for i in tqdm (range(9), desc="Loading data and plotting…", ascii=False, ncols=75): #gives progress bar

    j = i*380

    p = periods[j:j+379]
    ic = incls[j:j+379]
    n = natives[j:j+379]
    oh = ohs[j:j+379]
    d = diffs[j:j+379]
    e = ecs[j:j+379]

    emask = (e!=0)

    p1 = p[~emask]
    i1 = ic[~emask]
    n1 = n[~emask]
    oh1 = oh[~emask]
    d1 = d[~emask]

    p2 = p[emask]
    i2 = ic[emask]
    n2 = n[emask]
    oh2 = oh[emask]
    d2 = d[emask]

    if i < 3:
        a = i+1
        b = 1
    if (3<=i<6):
        a = i-2
        b = 2
    if i>=6:
        a = i-5
        b = 3

    fig.add_trace(
        go.Scatter3d(
            x=i1,
            y=p1,
            z=n1,
            mode='markers',
            marker = dict(size =2,
            color = c1[i]),
            name = 'Not Eclipsing'
        ),
        row=a, col=b
        )
    fig.add_trace(
        go.Scatter3d(
            x=i2,
            y=p2,
            z=n2,
            mode='markers',
            marker = dict(size =2,
            color = c2[i]),
            name = 'Eclipsing'
        ),
        row=a, col=b
        )

#camera = dict(
#    eye=dict(x=2, y=2, z=0.1)
#)

fig.update_layout(
    showlegend = False,
    title_text='Amplitudes of WD binaries',
    height=1200,
    width=1200,
    #scene_camera=camera,
    #font=dict(
        #family="Courier New, monospace",
        #size=10,
        #color="RebeccaPurple")
)

for i in range(1,10):
    fig['layout']['scene{}'.format(i)]['xaxis']['title']='Inclination (degs)'
    fig['layout']['scene{}'.format(i)]['yaxis']['title']='Period (days)'
    fig['layout']['scene{}'.format(i)]['zaxis']['title']='Amplitude (mag)'

print('plotting done')

fig.show()
print('exporting as html')
fig.write_html("plotly_example.html")
fig.write_image("plotly_example.png")
print('finished')
