### Using plotly library ###
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

##DATA HANDLING
fulldata = np.genfromtxt('../data.csv',skip_header = 1, delimiter = ',') #results from running models
tdata = np.transpose(fulldata)
masses = tdata[0]
periods = tdata[1]
incls = tdata[2]
ohs = tdata[4]
ecs = tdata[6]

## PLotting
fig = go.Figure()


distinct_masses = []

#making array so only 1st mass is visible orginally on plot
is_vis = []
for u in range(20):
    if u == 0:
        is_vis.append(True)
    else:
        is_vis.append(False)

#adding surface for the observational limit of 0.1 mag
x, y ,z= np.linspace(0, 10, 100), np.linspace(0, 90, 100), 0.1*np.ones((100,100))
mycolorscale = [[0.1, '#aa9ce2'],
                [1, '#aa9ce2']]
fig.add_trace(
    go.Surface(x=x, y=y, z=z, showscale=False,hoverinfo='skip',opacity=0.5,showlegend=True,
               name='Ground-based Dectection Limit (0.1 mag)',visible=True, colorscale=mycolorscale,
               )
)

#extracting the data for each mass and plotting them
for n in range(20):

    j = n*380

    m = round(masses[j],4)

    try:
        p = periods[j:j+379]
        ic = incls[j:j+379]
        a = ohs[j:j+379]
        e = ecs[j:j+379]
    except:
        p = periods[j:]
        ic = incls[j:]
        a = ohs[j:]
        e = ecs[j:]

    emask = (e!=0)

    p1 = p[~emask]
    i1 = ic[~emask]
    a1 = a[~emask]


    p2 = p[emask]
    i2 = ic[emask]
    a2 = a[emask]

    distinct_masses.append(m) #adds mass to list so can use it in title

    fig.add_trace( #surface constructed from points
    go.Mesh3d(x=p, y=ic, z=a, colorscale = "Portland",
              intensity=a, showscale=False,
              hoverinfo='skip', visible = is_vis[n]
             ))

    fig.add_trace( #scatter plots are only used for the hover text now (so opacity is very low)
        go.Scatter3d( #plot non-eclipsing data
            x = p1,
            y = i1,
            z = a1,
            mode='markers',
            marker = dict(size =20, color='deepskyblue',opacity=0.000001),
            hovertemplate ="Period: %{x} days"+ #format of box when you hover over point
             "<br>Inclination: %{y} degs<br>"+
              "Amplitude: %{z} mag",
            name = 'Not Eclipsing',
            showlegend = False,
            visible = is_vis[n] #makes it so only 1st mass is visible on startup
            ))
    fig.add_trace( #sam but for plotting eclipsing data (different colour and label)
        go.Scatter3d(
            x = p2,
            y = i2,
            z = a2,
            mode='markers',
            marker = dict(size =20,color='hotpink',opacity=0.000001),
            hovertemplate ="Period: %{x} days"+
             "<br>Inclination: %{y} degs<br>"+
              "Amplitude: %{z} mag",
            name = 'Eclipsing',
            showlegend = False,
            visible = is_vis[n]
            ))


#makes the lists for the options for the dropdown menu
buts = []
for i in range(20):
    k = i*3
    vis = np.array(False*np.ones(61),dtype=bool) #61 and shifted indices so plane is always visible
    vis[0], vis[k+1], vis[k+2], vis[k+3] = True, True, True, True #makes 1st and 3 adjacent indices True so plane,surface, non-eclipsing and eclipsing data for the mass are shown when the option is selected

    but = dict(label = str(distinct_masses[i]),
                  method = 'update',
                  args = [{'visible': vis}, # the index of True aligns with the indices of plot traces
                          {'title': f'Mass of MS Star: {distinct_masses[i]} solMass',
                           'showlegend':True}])
    buts.append(but) #adds dropdown option to drop down list


fig.update_layout(
    updatemenus=[go.layout.Updatemenu(active=0,buttons=list(buts))], #adds dropdown menu
    title={'text':f'Mass of MS Star: {distinct_masses[0]} solMass'})
    #makes first mass the title on start up, as that is the one shown (otherwise no title)

#configuring the axes labels
fig['layout']['scene']['xaxis']['title']='Period (days)'
fig['layout']['scene']['yaxis']['title']='Inclination (degs)'
fig['layout']['scene']['zaxis']['title']='Amplitude (mag)'

#shows graph and saves it in HTML format
fig.show()
fig.write_html("plotly_surface.html")
